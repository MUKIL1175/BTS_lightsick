# BTS Lightstick — User Manual

A custom smart lightstick built on the Seeed XIAO ESP32C6, with manual touch/button control and an optional phone-controlled web app for selecting your bias and viewing battery level.

---

## 1. What's in the Box (Hardware)

| Component | Connection |
|---|---|
| NeoPixel LED strip (8 LEDs) | D2 |
| Touch sensor module | D1 |
| Tactile push button | GPIO17 |
| Buzzer | D3 |
| Battery (via voltage divider) | A0 |

---

## 2. Getting Started

1. Power on the lightstick (connect/charge the battery).
2. The strip will show a slow **breathing purple glow** — this is idle mode, and means the stick booted successfully.
3. No phone or Wi-Fi connection is required for basic use — the touch sensor and button work standalone.

---

## 3. Physical Controls

### Tactile Button (GPIO17)

| Action | What it does |
|---|---|
| **Short press** (quick tap) | Returns the stick to idle breathing mode |
| **Double tap** (two quick taps) | Shows current battery level as a colored LED bar (green/yellow/red) for ~2.5 seconds |
| **Long press** (hold ~1.5 sec) | Toggles the Wi-Fi control page **on/off** — confirmed by a beep and a cyan (on) or red (off) flash |

### Touch Sensor (D1)

| Action | What it does |
|---|---|
| **Touch** | Randomly cycles to a different member's color + pattern, with a confirmation beep — handy for live use without needing your phone |

---

## 4. Battery Indicator

Double-tap the button (or tap the battery icon on the web app) to see your charge level:

- **Green** bar = above 60%
- **Yellow** bar = 25–60%
- **Red** bar = below 25%

The number of lit LEDs (out of 8) is proportional to charge. Display auto-returns to idle after ~2.5 seconds.

---

## 5. Wi-Fi Control Page (Phone App)

The lightstick can host its own Wi-Fi hotspot with a built-in control webpage — no internet needed.

### Turning it on
- **Long-press the button** (hold ~1.5 sec) until you hear a rising beep and see a cyan flash.
- The stick is now broadcasting a Wi-Fi network.

### Connecting your phone
1. Open Wi-Fi settings on your phone.
2. Connect to network: **`BTS-Lightstick`**
3. Enter password: **`borahae7`**
4. Open a browser and go to: **`http://192.168.4.1`** (or it may auto-open a captive portal prompt)

### Using the control page
- A green dot at the top-left means you're connected live.
- Tap any of the **7 member tiles** (RM, Jin, Suga, J-Hope, Jimin, V, Jungkook) to instantly change the stick's color and animation pattern to that member's signature look.
- Tap the **⚡ battery button** (top right) to check current charge — both on the page and on the physical LEDs.
- Tap **Idle** (bottom) to return the stick to the default breathing purple glow.

### Turning it off
- **Long-press the button again** — confirmed by a falling beep and a red flash.
- The Wi-Fi network will disappear and your phone will disconnect.

### Auto Shut-Off
To save battery, the Wi-Fi hotspot **automatically turns off after 5 minutes of no activity** (no taps on the web page). Just long-press the button again to turn it back on whenever you need it.

---

## 6. Member Color Guide

| Member | Color | Pattern |
|---|---|---|
| RM | Purple | Wave |
| Jin | Pink | Pulse (breathing) |
| Suga | Grey | Sparkle |
| J-Hope | Gold | Chase (comet) |
| Jimin | Magenta-pink | Pulse (breathing) |
| V | Burgundy/brown | Wave |
| Jungkook | Sky blue | Chase (comet) |

---

## 7. Quick Troubleshooting

| Problem | Try this |
|---|---|
| LEDs don't light up at boot | Check battery charge; double-tap to view battery level once it boots |
| Touch sensor doesn't respond | Make sure you're touching firmly — external touch modules need contact, not just proximity |
| Can't find `BTS-Lightstick` Wi-Fi | Confirm you long-pressed for the full ~1.5 sec (short press won't trigger it); listen for the confirmation beep |
| Web page won't load | Make sure your phone is connected to the `BTS-Lightstick` network specifically (not your home Wi-Fi), then visit `192.168.4.1` |
| Web page loaded but taps don't change LEDs | Check the connection dot top-left is green; if grey, wait a second for it to auto-reconnect |
| Wi-Fi turned off by itself | This is normal — it auto-shuts off after 5 minutes idle to save battery. Long-press to turn it back on |

---

## 8. Quick Reference Card

```
SHORT PRESS   -> idle mode
DOUBLE TAP    -> show battery
LONG PRESS    -> toggle Wi-Fi control page on/off
TOUCH         -> random member color (no phone needed)

Wi-Fi:  BTS-Lightstick
Pass:   borahae7
Page:   192.168.4.1
```
