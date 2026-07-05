# main.py - entry point, runs LEDs / inputs / web server as concurrent asyncio tasks

import urandom
import uasyncio as asyncio

from leds import LedController
from battery import Battery
from buzzer import Buzzer
from inputs import Inputs
from webserver import WebServer
from members import MEMBER_COUNT

led_ctrl = LedController()
battery = Battery()
buzzer = Buzzer()
server = WebServer(led_ctrl, battery, buzzer)

_last_touch_member = -1


def on_short_press():
    buzzer.stop()
    led_ctrl.set_idle()


def on_double_tap():
    buzzer.stop()
    led_ctrl.show_battery(battery.read_percent())


def on_long_press():
    buzzer.stop()
    server.toggle_ap()


def on_touch():
    global _last_touch_member
    buzzer.stop()
    idx = urandom.getrandbits(8) % MEMBER_COUNT
    while idx == _last_touch_member:
        idx = urandom.getrandbits(8) % MEMBER_COUNT
    _last_touch_member = idx
    led_ctrl.set_member(idx)
    buzzer.beep_confirm()


inputs = Inputs(
    on_short=on_short_press,
    on_double=on_double_tap,
    on_long=on_long_press,
    on_touch=on_touch,
)


async def main():
    led_ctrl.set_idle()
    # AP stays off until long-press toggles it (webserver.run() just watches idle timeout)
    await asyncio.gather(
        led_ctrl.run(),
        inputs.run(),
        server.run(),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    finally:
        asyncio.new_event_loop()
