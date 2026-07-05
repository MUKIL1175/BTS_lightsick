# config.py - Seeed XIAO ESP32C6, pin defs + timing constants

# ===================== PINS =====================
TOUCH_PIN = 1       # D1 - external touch module (digital HIGH/LOW)
RGB_PIN = 2          # D2 - NeoPixel data line
BUZZER_PIN = 21       # D3 - buzzer (PWM tone)
BUTTON_PIN = 17        # GPIO17 - tactile push button
BATT_ADC_PIN = 0        # A0/GPIO0 - battery voltage divider

NUM_LEDS = 8

# ===================== TIMING (ms) =====================
DEBOUNCE_MS = 30
LONG_PRESS_MS = 1500
DOUBLE_TAP_WINDOW_MS = 350
TOUCH_DEBOUNCE_MS = 80
AP_IDLE_TIMEOUT_MS = 300_000   # 5 min auto-off
BATTERY_DISPLAY_MS = 2500

LED_FPS = 60
LED_FRAME_MS = 1000 // LED_FPS

POLL_MS = 10   # main input-poll loop tick

# ===================== BATTERY =====================
BATT_ADC_MAX_MV = 3300.0
BATT_DIVIDER_RATIO = 2.0
BATT_FULL_MV = 4200.0
BATT_EMPTY_MV = 3300.0

# ===================== WIFI AP =====================
AP_SSID = "BTS-Lightstick"
AP_PASSWORD = "btslove7"
AP_CHANNEL = 6
AP_MAX_CLIENTS = 4

# ===================== MISC =====================
GLOBAL_BRIGHTNESS = 120   # 0-255 cap, applied as a scale factor (no native brightness in neopixel module)
