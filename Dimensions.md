# Component Dimensions Reference

> **Note:** Dimensions are typical values and may vary slightly depending on the manufacturer. These measurements are suitable for enclosure and PCB planning.

| Component | Typical Dimensions (L × W × H) | Notes |
|-----------|--------------------------------|------|
| **Seeed XIAO ESP32-C6** | **21.0 × 17.5 × 3.8 mm** | Without headers |
| **Digital Touch Sensor Module (TTP223)** | **24 × 24 × 7 mm** | Includes pin header |
| **Momentary Push Button (6×6 mm)** | **6 × 6 × 5 mm** | Standard tactile switch |
| **WS2812B 8-LED Ring** | **Outer Ø 32 mm**<br>**Inner Ø 18 mm**<br>Thickness: **2 mm** | Common Adafruit-compatible ring |
| **Piezo Buzzer (3.3 V)** | **Ø12 × 9.5 mm** | Active or passive type |
| **Li-Po Battery (500 mAh)** | **50 × 30 × 5 mm** | Approximate |
| **Li-Po Battery (1000 mAh)** | **60 × 35 × 6–7 mm** | Approximate |
| **18650 Cell (Alternative)** | **Ø18.5 × 65 mm** | Flat-top cell |
| **100 kΩ Resistor (Through-hole)** | **6.3 × Ø2.5 mm** | Axial 1/4W |
| **330 Ω Resistor (Through-hole)** | **6.3 × Ø2.5 mm** | Axial 1/4W |
| **100 kΩ / 330 Ω (SMD 0805)** | **2.0 × 1.25 × 0.55 mm** | If using SMD PCB |
| **1000 µF Electrolytic Capacitor** | **Ø10 × 20 mm** | Typical radial capacitor |
| **Slide Power Switch (Mini SPDT)** | **19 × 8 × 7 mm** | Excluding actuator |
| **JST-PH 2-Pin Connector** | **8 × 5.8 × 6 mm** | PCB mount |
| **USB-C Cable Plug** | **≈11 × 8 × 6 mm** | Clearance for enclosure opening |

---

# PCB & Wiring Clearance Recommendations

| Item | Recommended Clearance |
|------|-----------------------|
| Around XIAO ESP32-C6 | **2 mm** |
| Around Push Button | **1 mm** |
| Around Touch Sensor | **2 mm** |
| Around LED Ring | **2 mm** |
| Battery Compartment | **2–3 mm** |
| USB-C Opening | **1 mm** each side |
| Power Switch Slot | **0.5 mm** each side |

---

# Mounting Hole Information

## Seeed XIAO ESP32-C6

- Mounting holes: **None**
- Recommended mounting:
  - Double-sided tape
  - Snap-fit enclosure
  - Printed clips

## WS2812B LED Ring

Typical values:

- Outer Diameter: **32 mm**
- Inner Diameter: **18 mm**
- Mounting Holes: **4 × M2**
- Hole Diameter: **2.2 mm**

---

# Battery Connector

## JST-PH 2.0

| Dimension | Value |
|-----------|-------|
| Pitch | **2.0 mm** |
| Width | **8 mm** |
| Height | **6 mm** |
| Depth | **5.8 mm** |

---

# Suggested Internal Space Allocation

| Component | Allocate Space |
|-----------|----------------|
| XIAO ESP32-C6 | **25 × 22 × 6 mm** |
| Touch Sensor | **26 × 26 × 8 mm** |
| Push Button | **8 × 8 × 7 mm** |
| LED Ring | **36 × 36 × 4 mm** |
| Piezo Buzzer | **14 × 14 × 12 mm** |
| 500 mAh Battery | **52 × 32 × 7 mm** |
| 1000 mAh Battery | **62 × 37 × 8 mm** |
| 18650 Cell | **19 × 67 mm** |
| Electrolytic Capacitor | **12 × 12 × 22 mm** |
| Power Switch | **21 × 10 × 8 mm** |

---

# Overall Enclosure Recommendation

## Using 500 mAh Battery

- **70 × 50 × 22 mm**

## Using 1000 mAh Battery

- **80 × 55 × 24 mm**

## Using 18650 Battery

- **90 × 45 × 24 mm**

These dimensions provide adequate clearance for wiring, PCB tolerances, and future maintenance while keeping the enclosure compact.