# Components List

## Core Microcontroller

* **Seeed XIAO ESP32-C6** – Main microcontroller with Wi-Fi and Bluetooth support.

## Input Components

* **1 × Digital Touch Sensor Module**

  * Connected to **GPIO1 (D1)**
  * Provides HIGH/LOW digital touch detection.

* **1 × Momentary Tactile Push Button**

  * Connected to **GPIO17**
  * Used for user input (single press, double tap, long press).

## Output Components

* **1 × WS2812B / NeoPixel LED Ring (8 LEDs)**

  * Connected to **GPIO2 (D2)**
  * 8 individually addressable RGB LEDs.

* **1 × Piezo Buzzer (3.3 V compatible)**

  * Connected to **GPIO21**
  * Used for audio feedback through PWM tones.

## Power System

* **1 × 3.7 V Li-Po Battery**

  * Recommended capacity: **500–1000 mAh**
  * Supplies portable power.

* **Battery Voltage Divider**

  * Connected to **GPIO0 (A0)**
  * Used to safely measure battery voltage.
  * Divider ratio: **2:1**

## Passive Components

* **2 × Resistors** (for battery voltage divider)

  * Example values:

    * 100 kΩ
    * 100 kΩ
  * Produces a 2:1 voltage division.

* **1 × 330 Ω Resistor** (recommended)

  * In series with the NeoPixel data line.
  * Improves signal integrity and protects the first LED.

* **1 × 1000 µF Electrolytic Capacitor** (recommended)

  * Across battery supply near the LED ring.
  * Helps prevent voltage spikes during LED power changes.

## Connectivity

* USB-C cable (for programming and charging)
* JST-PH battery connector (if not already integrated)

## Optional Components

* Power switch
* 3D printed enclosure
* Diffuser for LED ring
* Mounting hardware (M2 screws, standoffs, or adhesive)

---

## GPIO Assignment

| GPIO   | Function       | Component               |
| ------ | -------------- | ----------------------- |
| GPIO0  | Analog Input   | Battery voltage monitor |
| GPIO1  | Digital Input  | Touch sensor            |
| GPIO2  | Digital Output | WS2812B / NeoPixel data |
| GPIO17 | Digital Input  | Push button             |
| GPIO21 | PWM Output     | Piezo buzzer            |

---

## Summary Bill of Materials (BOM)

| Qty | Component                                    |
| --: | -------------------------------------------- |
|   1 | Seeed XIAO ESP32-C6                          |
|   1 | WS2812B 8-LED NeoPixel Ring                  |
|   1 | Digital touch sensor module                  |
|   1 | Piezo buzzer                                 |
|   1 | Momentary tactile push button                |
|   1 | 3.7 V Li-Po battery                          |
|   2 | 100 kΩ resistors (battery divider)           |
|   1 | 330 Ω resistor (LED data line, recommended)  |
|   1 | 1000 µF electrolytic capacitor (recommended) |
|   1 | USB-C cable                                  |
|   1 | Power switch (optional)                      |
|   1 | Enclosure (optional)                         |
