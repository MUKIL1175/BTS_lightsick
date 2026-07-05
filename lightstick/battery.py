# battery.py - ADC battery voltage/percent reading

from machine import ADC, Pin
from config import BATT_ADC_PIN, BATT_ADC_MAX_MV, BATT_DIVIDER_RATIO, BATT_FULL_MV, BATT_EMPTY_MV


class Battery:
    def __init__(self):
        self.adc = ADC(Pin(BATT_ADC_PIN))
        # 0-3.3V full range, 12-bit-ish reading depending on port; read_uv() is most portable
        try:
            self.adc.atten(ADC.ATTN_11DB)  # full 0-3.3V range on ESP32 ports that support it
        except Exception:
            pass

    def read_voltage(self):
        try:
            uv = self.adc.read_uv()  # available on newer MicroPython ESP32 ports, most accurate
            adc_mv = uv / 1000.0
        except AttributeError:
            raw = self.adc.read()  # fallback: 0-65535 on ESP32 ports, or 0-4095 on older
            max_raw = 65535 if raw > 4095 else 4095
            adc_mv = (raw / max_raw) * BATT_ADC_MAX_MV
        real_mv = adc_mv * BATT_DIVIDER_RATIO
        return real_mv / 1000.0

    def read_percent(self):
        v_mv = self.read_voltage() * 1000.0
        if v_mv >= BATT_FULL_MV:
            return 100
        if v_mv <= BATT_EMPTY_MV:
            return 0
        pct = (v_mv - BATT_EMPTY_MV) / (BATT_FULL_MV - BATT_EMPTY_MV) * 100.0
        return max(0, min(100, int(pct)))
