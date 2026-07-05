# webserver.py - SoftAP toggle + asyncio HTTP/WebSocket server, serves /web as static files
#
# Minimal hand-rolled WebSocket implementation (RFC6455) since MicroPython's
# standard library has no WS support built in. No external packages needed.

import time
import network
import uasyncio as asyncio
import ubinascii
import uhashlib
import ujson as json

from config import AP_SSID, AP_PASSWORD, AP_CHANNEL, AP_MAX_CLIENTS, AP_IDLE_TIMEOUT_MS
from members import MEMBER_COUNT

WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
WEB_ROOT = "/web"

CONTENT_TYPES = {
    "html": "text/html",
    "css": "text/css",
    "js": "application/javascript",
    "json": "application/json",
}


def _ws_accept_key(client_key):
    h = uhashlib.sha1(client_key.encode() + WS_GUID.encode())
    return ubinascii.b2a_base64(h.digest()).decode().strip()


class WSConnection:
    """One connected WebSocket client."""

    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer
        self.alive = True

    async def send_text(self, text):
        data = text.encode()
        length = len(data)
        try:
            if length < 126:
                header = bytes([0x81, length])
            elif length < 65536:
                header = bytes([0x81, 126]) + length.to_bytes(2, "big")
            else:
                header = bytes([0x81, 127]) + length.to_bytes(8, "big")
            self.writer.write(header + data)
            await self.writer.drain()
        except Exception:
            self.alive = False

    async def recv_text(self):
        """Returns decoded text frame payload, or None on close/error."""
        try:
            head = await self.reader.readexactly(2)
        except Exception:
            return None
        if not head:
            return None

        b0, b1 = head[0], head[1]
        opcode = b0 & 0x0F
        masked = (b1 & 0x80) != 0
        plen = b1 & 0x7F

        if plen == 126:
            ext = await self.reader.readexactly(2)
            plen = int.from_bytes(ext, "big")
        elif plen == 127:
            ext = await self.reader.readexactly(8)
            plen = int.from_bytes(ext, "big")

        mask_key = b""
        if masked:
            mask_key = await self.reader.readexactly(4)

        payload = await self.reader.readexactly(plen) if plen else b""

        if masked and payload:
            payload = bytes(payload[i] ^ mask_key[i % 4] for i in range(len(payload)))

        if opcode == 0x8:  # close frame
            return None
        if opcode == 0x9:  # ping - reply pong (best-effort, ignored content)
            try:
                self.writer.write(bytes([0x8A, 0]))
                await self.writer.drain()
            except Exception:
                pass
            return ""
        if opcode != 0x1:  # only handle text frames
            return ""

        return payload.decode()


class WebServer:
    def __init__(self, led_ctrl, battery, buzzer):
        self.led_ctrl = led_ctrl
        self.battery = battery
        self.buzzer = buzzer

        self.ap = network.WLAN(network.AP_IF)
        self.ap_active = False
        self.last_activity_ms = time.ticks_ms()

        self.clients = []  # list of WSConnection
        self._server = None

    # ---------------- AP control ----------------
    def start_ap(self):
        self.ap.active(True)
        self.ap.config(essid=AP_SSID, password=AP_PASSWORD, channel=AP_CHANNEL,
                        max_clients=AP_MAX_CLIENTS, authmode=network.AUTH_WPA2_PSK)
        self.ap_active = True
        self.last_activity_ms = time.ticks_ms()
        self.led_ctrl.flash_ap_status(True)
        self.buzzer.beep_ap_on()
        asyncio.create_task(self._start_http_server())

    def stop_ap(self):
        for c in self.clients:
            try:
                c.writer.close()
            except Exception:
                pass
        self.clients = []
        if self._server:
            self._server.close()
            self._server = None
        self.ap.active(False)
        self.ap_active = False
        self.led_ctrl.flash_ap_status(False)
        self.buzzer.beep_ap_off()

    def toggle_ap(self):
        if self.ap_active:
            self.stop_ap()
        else:
            self.start_ap()

    async def _start_http_server(self):
        self._server = await asyncio.start_server(self._handle_conn, "0.0.0.0", 80)

    # ---------------- connection handling ----------------
    async def _handle_conn(self, reader, writer):
        try:
            request_line = await reader.readline()
            if not request_line:
                writer.close()
                return
            parts = request_line.decode().split()
            if len(parts) < 2:
                writer.close()
                return
            method, path = parts[0], parts[1]

            headers = {}
            while True:
                line = await reader.readline()
                if line in (b"\r\n", b"\n", b""):
                    break
                if b":" in line:
                    k, v = line.decode().split(":", 1)
                    headers[k.strip().lower()] = v.strip()

            if path == "/ws" and headers.get("upgrade", "").lower() == "websocket":
                await self._handle_ws_upgrade(reader, writer, headers)
            else:
                await self._handle_static(path, writer)

        except Exception:
            try:
                writer.close()
            except Exception:
                pass

    async def _handle_ws_upgrade(self, reader, writer, headers):
        key = headers.get("sec-websocket-key", "")
        accept = _ws_accept_key(key)
        resp = (
            "HTTP/1.1 101 Switching Protocols\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            "Sec-WebSocket-Accept: {}\r\n\r\n"
        ).format(accept)
        writer.write(resp.encode())
        await writer.drain()

        conn = WSConnection(reader, writer)
        self.clients.append(conn)
        self.last_activity_ms = time.ticks_ms()

        # send initial battery reading on connect
        await conn.send_text(json.dumps({"battery": self.battery.read_percent()}))

        try:
            while conn.alive:
                msg = await conn.recv_text()
                if msg is None:
                    break
                if msg:
                    self.last_activity_ms = time.ticks_ms()
                    self._handle_ws_message(msg)
        finally:
            if conn in self.clients:
                self.clients.remove(conn)
            try:
                writer.close()
            except Exception:
                pass

    def _handle_ws_message(self, msg):
        try:
            data = json.loads(msg)
        except Exception:
            return

        if "member" in data:
            idx = int(data["member"])
            if 0 <= idx < MEMBER_COUNT:
                self.buzzer.stop()
                self.led_ctrl.set_member(idx)
                self.buzzer.beep_confirm()

        elif data.get("cmd") == "battery":
            self.buzzer.stop()
            pct = self.battery.read_percent()
            self.led_ctrl.show_battery(pct)
            asyncio.create_task(self._broadcast_battery(pct))

        elif data.get("cmd") == "idle":
            self.buzzer.stop()
            self.led_ctrl.set_idle()

        elif data.get("cmd") == "off":
            self.buzzer.stop()
            self.led_ctrl.set_off()

        elif data.get("cmd") == "on":
            self.buzzer.stop()
            self.led_ctrl.set_custom_effect("solid", 2000)

        elif "effect" in data:
            eff = data["effect"]
            dur = int(data.get("duration", 2000))
            r = data.get("r")
            g = data.get("g")
            b = data.get("b")
            if r is not None and g is not None and b is not None:
                self.led_ctrl.set_custom_color(int(r), int(g), int(b))
            self.led_ctrl.set_custom_effect(eff, dur)
            if eff.startswith("combo_"):
                self.buzzer.play_combo(eff)
            else:
                self.buzzer.stop()

        elif "r" in data and "g" in data and "b" in data:
            r = int(data["r"])
            g = int(data["g"])
            b = int(data["b"])
            self.led_ctrl.set_custom_color(r, g, b)

    async def _broadcast_battery(self, pct):
        msg = json.dumps({"battery": pct})
        for c in list(self.clients):
            await c.send_text(msg)

    # ---------------- static file serving ----------------
    async def _handle_static(self, path, writer):
        if path == "/":
            path = "/index.html"
        ext = path.rsplit(".", 1)[-1] if "." in path else "html"
        ctype = CONTENT_TYPES.get(ext, "application/octet-stream")
        fpath = WEB_ROOT + path

        try:
            with open(fpath, "rb") as f:
                body = f.read()
            writer.write("HTTP/1.1 200 OK\r\nContent-Type: {}\r\nContent-Length: {}\r\nConnection: close\r\n\r\n".format(ctype, len(body)).encode())
            writer.write(body)
        except OSError:
            msg = b"Not found"
            writer.write(b"HTTP/1.1 404 Not Found\r\nContent-Length: %d\r\nConnection: close\r\n\r\n" % len(msg))
            writer.write(msg)

        await writer.drain()
        writer.close()

    # ---------------- background idle-timeout task ----------------
    async def run(self):
        while True:
            if self.ap_active:
                if time.ticks_diff(time.ticks_ms(), self.last_activity_ms) > AP_IDLE_TIMEOUT_MS:
                    self.stop_ap()
            await asyncio.sleep_ms(1000)
