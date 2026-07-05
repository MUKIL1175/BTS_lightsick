from machine import Pin
from neopixel import NeoPixel
import time

# -----------------------
# Pin Configuration
# -----------------------
TOUCH_PIN = 1       # D1
RGB_PIN = 2         # D2
BUZZER_PIN = 21     # D3 (change if needed)
BUTTON_PIN = 17     # GPIO17

NUM_LEDS = 8

# -----------------------
# Hardware Initialization
# -----------------------
touch = Pin(TOUCH_PIN, Pin.IN)
button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)
buzzer = Pin(BUZZER_PIN, Pin.OUT)

pixels = NeoPixel(Pin(RGB_PIN), NUM_LEDS)

# -----------------------
# Colors
# -----------------------
colors = [
    (255, 0, 0),      # Red
    (0, 255, 0),      # Green
    (0, 0, 255),      # Blue
    (255, 255, 0),    # Yellow
    (255, 0, 255),    # Magenta
    (0, 255, 255),    # Cyan
    (255, 255, 255),  # White
    (255, 128, 0),    # Orange
]

color_index = 0


# -----------------------
# Functions
# -----------------------
def set_ring(color):
    for i in range(NUM_LEDS):
        pixels[i] = color
    pixels.write()


def clear_ring():
    for i in range(NUM_LEDS):
        pixels[i] = (0, 0, 0)
    pixels.write()


def beep(duration=20):
    buzzer.value(1)
    time.sleep_ms(duration)
    buzzer.value(0)


# -----------------------
# Startup
# -----------------------
clear_ring()                     # Ensure LEDs start OFF
set_ring(colors[color_index])    # Initial color

previous_touch = touch.value()
previous_button = button.value()

print("Lightstick Ready!")

# -----------------------
# Main Loop
# -----------------------
try:
    while True:
        current_touch = touch.value()
        current_button = button.value()

        # Touch sensor rising edge
        touch_pressed = (
            current_touch == 1 and
            previous_touch == 0
        )

        # Button press (active LOW)
        button_pressed = (
            current_button == 0 and
            previous_button == 1
        )

        # Either touch or button does the same action
        if touch_pressed or button_pressed:
            beep()

            color_index = (color_index + 1) % len(colors)
            set_ring(colors[color_index])

            # Debounce
            time.sleep_ms(300)

        previous_touch = current_touch
        previous_button = current_button

        time.sleep_ms(20)

except KeyboardInterrupt:
    print("Stopping...")

finally:
    clear_ring()
    buzzer.value(0)

    print("RGB OFF")
    print("Buzzer OFF")