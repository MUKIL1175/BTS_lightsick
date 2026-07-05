# buzzer.py - non-blocking beep sequences using PWM, driven by an asyncio task

import uasyncio as asyncio
from machine import Pin, PWM
from config import BUZZER_PIN


class Buzzer:
    def __init__(self):
        self.pwm = PWM(Pin(BUZZER_PIN))
        self.pwm.duty_u16(0)
        self.current_task = None

    def _stop(self):
        try:
            self.pwm.duty_u16(0)
        except Exception:
            pass

    def stop(self):
        if self.current_task and not self.current_task.done():
            self.current_task.cancel()
            self.current_task = None
        self._stop()

    async def _play_step(self, freq, dur_ms, gap_ms):
        if freq > 0:
            try:
                self.pwm.freq(freq)
                self.pwm.duty_u16(32768)  # 50% duty
            except Exception:
                pass
        else:
            self._stop()
        await asyncio.sleep_ms(dur_ms)
        self._stop()
        if gap_ms:
            await asyncio.sleep_ms(gap_ms)

    async def _run_sequence(self, steps, loop):
        try:
            while True:
                for freq, dur_ms, gap_ms in steps:
                    await self._play_step(freq, dur_ms, gap_ms)
                if not loop:
                    break
        except asyncio.CancelledError:
            pass
        finally:
            self._stop()

    def play_sequence(self, steps, loop=False):
        self.stop()
        self.current_task = asyncio.create_task(self._run_sequence(steps, loop))

    def beep(self, freq_hz, duration_ms):
        self.play_sequence([(freq_hz, duration_ms, 0)], loop=False)

    def beep_confirm(self):
        self.beep(2000, 60)

    def beep_ap_on(self):
        self.play_sequence([(1500, 70, 40), (2200, 90, 0)], loop=False)

    def beep_ap_off(self):
        self.play_sequence([(2200, 70, 40), (1200, 90, 0)], loop=False)

    def play_combo(self, name):
        if name == "combo_siren":
            self.play_sequence([(800, 200, 0), (1200, 200, 0)], loop=True)
        elif name == "combo_sparkle":
            self.play_sequence([
                (1047, 100, 20),
                (1318, 100, 20),
                (1568, 100, 20),
                (2093, 120, 500)
            ], loop=True)
        elif name == "combo_rhythm":
            self.play_sequence([
                (150, 80, 50),
                (150, 80, 600)
            ], loop=True)
        else:
            self.stop()
