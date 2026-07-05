# inputs.py - debounced button + touch module, asyncio polling task

import time
import uasyncio as asyncio
from machine import Pin
from config import (
    BUTTON_PIN, TOUCH_PIN, DEBOUNCE_MS, LONG_PRESS_MS,
    DOUBLE_TAP_WINDOW_MS, TOUCH_DEBOUNCE_MS, POLL_MS,
)

BTN_NONE = 0
BTN_SHORT_PRESS = 1
BTN_DOUBLE_TAP = 2
BTN_LONG_PRESS = 3


class Inputs:
    def __init__(self, on_short=None, on_double=None, on_long=None, on_touch=None):
        self.button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)  # idle HIGH, pressed LOW
        self.touch = Pin(TOUCH_PIN, Pin.IN)                  # external module, digital HIGH/LOW

        self.on_short = on_short
        self.on_double = on_double
        self.on_long = on_long
        self.on_touch = on_touch

        self._last_raw = 1
        self._stable = 1
        self._last_debounce_ms = time.ticks_ms()
        self._press_start_ms = 0
        self._long_fired = False
        self._last_release_ms = 0
        self._waiting_double = False

        self._touch_last_raw = 0
        self._touch_stable = 0
        self._touch_last_debounce_ms = time.ticks_ms()

    def _poll_button(self):
        now = time.ticks_ms()
        raw = self.button.value()

        if raw != self._last_raw:
            self._last_debounce_ms = now
        self._last_raw = raw

        if time.ticks_diff(now, self._last_debounce_ms) > DEBOUNCE_MS and raw != self._stable:
            self._stable = raw
            if self._stable == 0:
                self._press_start_ms = now
                self._long_fired = False
            else:
                held_for = time.ticks_diff(now, self._press_start_ms)
                if held_for >= LONG_PRESS_MS:
                    pass  # long press already fired during hold
                else:
                    if self._waiting_double and time.ticks_diff(now, self._last_release_ms) <= DOUBLE_TAP_WINDOW_MS:
                        self._waiting_double = False
                        if self.on_double:
                            self.on_double()
                        return
                    else:
                        self._waiting_double = True
                        self._last_release_ms = now

        if self._stable == 0 and not self._long_fired and time.ticks_diff(now, self._press_start_ms) >= LONG_PRESS_MS:
            self._long_fired = True
            self._waiting_double = False
            if self.on_long:
                self.on_long()
            return

        if self._waiting_double and time.ticks_diff(now, self._last_release_ms) > DOUBLE_TAP_WINDOW_MS:
            self._waiting_double = False
            if self.on_short:
                self.on_short()

    def _poll_touch(self):
        now = time.ticks_ms()
        raw = self.touch.value()

        if raw != self._touch_last_raw:
            self._touch_last_debounce_ms = now
        self._touch_last_raw = raw

        if time.ticks_diff(now, self._touch_last_debounce_ms) > TOUCH_DEBOUNCE_MS and raw != self._touch_stable:
            self._touch_stable = raw
            if self._touch_stable == 1:
                if self.on_touch:
                    self.on_touch()

    async def run(self):
        while True:
            self._poll_button()
            self._poll_touch()
            await asyncio.sleep_ms(POLL_MS)
