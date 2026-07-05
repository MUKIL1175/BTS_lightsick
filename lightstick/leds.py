# leds.py - non-blocking NeoPixel animation engine (uasyncio task)

import math
import time
import neopixel
import machine
import uasyncio as asyncio

from config import RGB_PIN, NUM_LEDS, LED_FRAME_MS, GLOBAL_BRIGHTNESS, BATTERY_DISPLAY_MS
from members import MEMBERS, MEMBER_COUNT, IDLE_COLOR, PATTERN_SOLID, PATTERN_PULSE, PATTERN_SPARKLE, PATTERN_CHASE, PATTERN_WAVE

MODE_IDLE = 0
MODE_MEMBER = 1
MODE_BATTERY = 2
MODE_AP_STATUS = 3
MODE_OFF = 4
MODE_CUSTOM_EFFECT = 5


def _scale(c, factor):
    # factor 0-255
    return (c[0] * factor // 255, c[1] * factor // 255, c[2] * factor // 255)


def _scale_global(c):
    return _scale(c, GLOBAL_BRIGHTNESS)


def _sin8(x):
    # x: 0-255 maps to one full sine cycle, returns 0-255
    rad = (x % 256) * (2 * math.pi / 256)
    return int((math.sin(rad) + 1) * 127.5)


def _beatsin8(bpm, lo, hi, t_ms):
    # smooth oscillation between lo/hi at given bpm, driven by elapsed ms
    cycle_ms = 60000 / bpm
    phase = (t_ms % cycle_ms) / cycle_ms  # 0..1
    s = (math.sin(phase * 2 * math.pi) + 1) / 2  # 0..1
    return int(lo + s * (hi - lo))


class LedController:
    def __init__(self):
        self.np = neopixel.NeoPixel(machine.Pin(RGB_PIN), NUM_LEDS)
        self.mode = MODE_IDLE
        self.member_idx = 0
        self.battery_percent = 0
        self.ap_on = False
        self.mode_start_ms = time.ticks_ms()
        self.tick = 0
        self._sparkle_buf = [(0, 0, 0)] * NUM_LEDS
        self.custom_color = (106, 13, 173)  # default purple
        self.custom_effect = "solid"
        self.duration_ms = 2000
        self.clear()

    def clear(self):
        for i in range(NUM_LEDS):
            self.np[i] = (0, 0, 0)
        self.np.write()

    # ---- public control API (called from input/web handlers) ----
    def set_member(self, idx):
        if 0 <= idx < MEMBER_COUNT:
            self.member_idx = idx
            self.mode = MODE_MEMBER
            self.mode_start_ms = time.ticks_ms()

    def show_battery(self, percent):
        self.battery_percent = percent
        self.mode = MODE_BATTERY
        self.mode_start_ms = time.ticks_ms()

    def flash_ap_status(self, ap_on):
        self.ap_on = ap_on
        self.mode = MODE_AP_STATUS
        self.mode_start_ms = time.ticks_ms()

    def set_idle(self):
        self.mode = MODE_IDLE
        self.mode_start_ms = time.ticks_ms()

    def set_custom_color(self, r, g, b):
        self.custom_color = (r, g, b)

    def set_custom_effect(self, eff_type, duration_ms):
        self.custom_effect = eff_type
        self.duration_ms = duration_ms
        self.mode = MODE_CUSTOM_EFFECT
        self.mode_start_ms = time.ticks_ms()

    def set_off(self):
        self.mode = MODE_OFF
        self.clear()

    # ---- frame renderers ----
    def _render_idle(self, now):
        b = _beatsin8(12, 40, 180, now)
        c = _scale(IDLE_COLOR, b)
        for i in range(NUM_LEDS):
            self.np[i] = c

    def _render_pattern(self, now):
        name, color, pattern = MEMBERS[self.member_idx]

        if pattern == PATTERN_SOLID:
            c = _scale_global(color)
            for i in range(NUM_LEDS):
                self.np[i] = c

        elif pattern == PATTERN_PULSE:
            b = _beatsin8(20, 50, 255, now)
            c = _scale(color, min(b, GLOBAL_BRIGHTNESS))
            for i in range(NUM_LEDS):
                self.np[i] = c

        elif pattern == PATTERN_SPARKLE:
            # fade existing buffer, randomly add a sparkle pixel
            import urandom
            for i in range(NUM_LEDS):
                r, g, b = self._sparkle_buf[i]
                self._sparkle_buf[i] = (r * 7 // 8, g * 7 // 8, b * 7 // 8)
            if urandom.getrandbits(8) < 90:
                pos = urandom.getrandbits(8) % NUM_LEDS
                self._sparkle_buf[pos] = _scale_global(color)
            for i in range(NUM_LEDS):
                self.np[i] = self._sparkle_buf[i]

        elif pattern == PATTERN_CHASE:
            for i in range(NUM_LEDS):
                r, g, b = self._sparkle_buf[i]
                self._sparkle_buf[i] = (r * 3 // 5, g * 3 // 5, b * 3 // 5)
            pos = (self.tick // 4) % NUM_LEDS
            self._sparkle_buf[pos] = _scale_global(color)
            for i in range(NUM_LEDS):
                self.np[i] = self._sparkle_buf[i]

        elif pattern == PATTERN_WAVE:
            for i in range(NUM_LEDS):
                wave = _sin8((i * 32 + self.tick * 6) % 256)
                self.np[i] = _scale(color, min(wave, GLOBAL_BRIGHTNESS))

    def _render_battery(self, now):
        pct = self.battery_percent
        lit = (pct * NUM_LEDS) // 100
        if pct > 60:
            color = (0, 255, 0)
        elif pct > 25:
            color = (255, 200, 0)
        else:
            color = (255, 0, 0)
        color = _scale_global(color)
        for i in range(NUM_LEDS):
            self.np[i] = color if i < lit else (0, 0, 0)

        if time.ticks_diff(now, self.mode_start_ms) > BATTERY_DISPLAY_MS:
            self.mode = MODE_IDLE

    def _render_ap_status(self, now):
        color = (0, 255, 255) if self.ap_on else (255, 0, 0)
        b = _beatsin8(40, 60, 255, now)
        c = _scale(color, min(b, GLOBAL_BRIGHTNESS))
        for i in range(NUM_LEDS):
            self.np[i] = c

        if time.ticks_diff(now, self.mode_start_ms) > 900:
            self.mode = MODE_IDLE

    def _render_off(self):
        for i in range(NUM_LEDS):
            self.np[i] = (0, 0, 0)

    def _render_custom_effect(self, now):
        eff = self.custom_effect
        dur = self.duration_ms
        c_col = self.custom_color

        if eff == "solid":
            c = _scale_global(c_col)
            for i in range(NUM_LEDS):
                self.np[i] = c

        elif eff == "strobe":
            if (now % dur) < (dur // 2):
                c = _scale_global(c_col)
            else:
                c = (0, 0, 0)
            for i in range(NUM_LEDS):
                self.np[i] = c

        elif eff == "fade_in":
            phase = (now % dur) / dur
            c = _scale(c_col, int(phase * GLOBAL_BRIGHTNESS))
            for i in range(NUM_LEDS):
                self.np[i] = c

        elif eff == "fade_out":
            phase = (now % dur) / dur
            c = _scale(c_col, int((1.0 - phase) * GLOBAL_BRIGHTNESS))
            for i in range(NUM_LEDS):
                self.np[i] = c

        elif eff == "breath":
            phase = (now % dur) / dur
            s = (math.sin(phase * 2 * math.pi) + 1) / 2
            b = int(25 + s * (GLOBAL_BRIGHTNESS - 25))
            c = _scale(c_col, b)
            for i in range(NUM_LEDS):
                self.np[i] = c

        elif eff == "rotate_cw":
            pos_f = ((now % dur) / dur) * NUM_LEDS
            for i in range(NUM_LEDS):
                diff = (pos_f - i) % NUM_LEDS
                if diff < 4:
                    factor = (4 - diff) / 4.0
                    self.np[i] = _scale(c_col, int(factor * GLOBAL_BRIGHTNESS))
                else:
                    self.np[i] = (0, 0, 0)

        elif eff == "rotate_ccw":
            pos_f = (1.0 - ((now % dur) / dur)) * NUM_LEDS
            for i in range(NUM_LEDS):
                diff = (pos_f - i) % NUM_LEDS
                if diff < 4:
                    factor = (4 - diff) / 4.0
                    self.np[i] = _scale(c_col, int(factor * GLOBAL_BRIGHTNESS))
                else:
                    self.np[i] = (0, 0, 0)

        elif eff == "drop_fill_cw":
            step_dur = dur // NUM_LEDS
            elapsed = now % dur
            k = elapsed // step_dur
            step_elapsed = elapsed % step_dur
            for i in range(NUM_LEDS):
                self.np[i] = (0, 0, 0)
            for i in range(NUM_LEDS - k, NUM_LEDS):
                self.np[i] = _scale_global(c_col)
            if k < NUM_LEDS:
                moving_range = NUM_LEDS - k
                moving_pos = int((step_elapsed / step_dur) * moving_range)
                if moving_pos < moving_range:
                    self.np[moving_pos] = _scale_global(c_col)

        elif eff == "drop_fill_ccw":
            step_dur = dur // NUM_LEDS
            elapsed = now % dur
            k = elapsed // step_dur
            step_elapsed = elapsed % step_dur
            for i in range(NUM_LEDS):
                self.np[i] = (0, 0, 0)
            for i in range(k):
                self.np[i] = _scale_global(c_col)
            if k < NUM_LEDS:
                moving_range = NUM_LEDS - k
                moving_pos = (NUM_LEDS - 1) - int((step_elapsed / step_dur) * moving_range)
                if moving_pos >= k:
                    self.np[moving_pos] = _scale_global(c_col)

        elif eff == "mid_fill":
            step = int(((now % dur) / dur) * 5)
            for i in range(NUM_LEDS):
                if (3 - step) < i < (4 + step):
                    self.np[i] = _scale_global(c_col)
                else:
                    self.np[i] = (0, 0, 0)

        elif eff == "combo_siren":
            elapsed = now % 400
            if elapsed < 200:
                for i in range(NUM_LEDS):
                    self.np[i] = _scale_global((255, 0, 0)) if i < 4 else _scale_global((0, 0, 255))
            else:
                for i in range(NUM_LEDS):
                    self.np[i] = _scale_global((0, 0, 255)) if i < 4 else _scale_global((255, 0, 0))

        elif eff == "combo_sparkle":
            import urandom
            for i in range(NUM_LEDS):
                r, g, b = self._sparkle_buf[i]
                self._sparkle_buf[i] = (r * 7 // 8, g * 7 // 8, b * 7 // 8)
            if urandom.getrandbits(8) < 120:
                pos = urandom.getrandbits(8) % NUM_LEDS
                colors = [(255,0,0), (0,255,0), (0,0,255), (255,255,0), (0,255,255), (255,0,255)]
                rand_color = colors[urandom.getrandbits(8) % len(colors)]
                self._sparkle_buf[pos] = _scale_global(rand_color)
            for i in range(NUM_LEDS):
                self.np[i] = self._sparkle_buf[i]

        elif eff == "combo_rhythm":
            elapsed = now % 810
            if (0 <= elapsed <= 80) or (130 <= elapsed <= 210):
                c = _scale_global((255, 20, 147))
            else:
                c = _scale((255, 20, 147), 15)
            for i in range(NUM_LEDS):
                self.np[i] = c

    def _render_frame(self):
        now = time.ticks_ms()
        self.tick = (self.tick + 1) & 0xFFFF

        if self.mode == MODE_IDLE:
            self._render_idle(now)
        elif self.mode == MODE_MEMBER:
            self._render_pattern(now)
        elif self.mode == MODE_BATTERY:
            self._render_battery(now)
        elif self.mode == MODE_AP_STATUS:
            self._render_ap_status(now)
        elif self.mode == MODE_OFF:
            self._render_off()
        elif self.mode == MODE_CUSTOM_EFFECT:
            self._render_custom_effect(now)

        self.np.write()

    async def run(self):
        # asyncio task: non-blocking frame-rate-gated animation loop
        while True:
            self._render_frame()
            await asyncio.sleep_ms(LED_FRAME_MS)
