# 🚨 Smart Proximity Alert System

A full end-to-end IoT system built with an **ESP32 microcontroller** and a **Python live dashboard** — combining embedded firmware, real-time serial communication, data processing and live visualisation.

---

## 📸 System Overview

```
ESP32 Hardware                    Python Dashboard
──────────────                    ────────────────
HC-SR04 (distance)  ──Serial──►  Serial parser
LED proximity zones              Rolling buffer
Button toggle                    Live matplotlib charts
16x2 LCD display                 Auto CSV logging
Battery simulation               Terminal status panel
```

---

## 🛠️ Hardware Requirements

| Component | Quantity |
|-----------|----------|
| ESP32 DevKit | 1 |
| HC-SR04 Ultrasonic Sensor | 1 |
| 16x2 LCD Display (non-I2C) | 1 |
| Green LED | 1 |
| Yellow LED | 1 |
| Red LED | 1 |
| Tactile Push Button | 1 |
| 220Ω Resistors (for LEDs) | 3 |
| 1kΩ Resistors (voltage divider) | 3 |
| Breadboard + Jumper Wires | — |

---

## 🔌 Wiring Diagram

### HC-SR04 Ultrasonic Sensor
```
HC-SR04 VCC  → ESP32 VIN (5V)
HC-SR04 GND  → GND
HC-SR04 TRIG → GPIO 5  (direct)
HC-SR04 ECHO → GPIO 18 (via voltage divider)

Voltage divider on ECHO pin (5V → 3.3V):
ECHO → [1kΩ] → GPIO 18
               ↓
           [1kΩ + 1kΩ]
               ↓
              GND
```

### LEDs
```
GPIO 25 → [220Ω] → Green LED  → GND  (SAFE zone)
GPIO 26 → [220Ω] → Yellow LED → GND  (WARNING zone)
GPIO 32 → [220Ω] → Red LED   → GND  (DANGER zone)
```

### Button
```
GPIO 4 → Button → GND
(INPUT_PULLUP enabled — no external resistor needed)
```

### 16x2 LCD (4-bit mode, 3.3V)
```
LCD Pin 1  (VSS)  → GND
LCD Pin 2  (VDD)  → ESP32 3.3V
LCD Pin 3  (V0)   → Contrast voltage divider (1kΩ/1kΩ from 3.3V to GND)
LCD Pin 4  (RS)   → GPIO 19
LCD Pin 5  (RW)   → GND
LCD Pin 6  (EN)   → GPIO 23
LCD Pin 11 (D4)   → GPIO 13
LCD Pin 12 (D5)   → GPIO 12
LCD Pin 13 (D6)   → GPIO 14
LCD Pin 14 (D7)   → GPIO 27
LCD Pin 15 (A)    → 3.3V via 220Ω
LCD Pin 16 (K)    → GND
```

---

## 📁 Project Structure

```
smart-proximity-alert/
├── firmware/
│   ├── src/
│   │   └── main.cpp          ← ESP32 firmware (PlatformIO)
│   └── platformio.ini        ← Build configuration
├── dashboard/
│   ├── serial_reader.py      ← Serial parser & generator
│   ├── data_processor.py     ← Rolling buffer, stats, CSV logger
│   ├── dashboard.py          ← Live matplotlib + terminal UI
│   └── pipeline.py           ← Full system orchestrator
├── data/
│   ├── sensor_log.csv        ← Auto-generated on first run
│   └── summary.csv           ← Auto-generated on first run
└── README.md
```

---

## ⚙️ Firmware Features

- **HC-SR04** distance readings every 500ms using non-blocking `millis()`
- **3-zone LED system:**
  - 🟢 Green — SAFE (> 100cm)
  - 🟡 Yellow — WARNING (40–100cm)
  - 🔴 Red — DANGER (< 40cm)
- **Debounced button toggle** — system ON/OFF with 50ms software debounce
- **16x2 LCD** alternating between distance/zone and battery screens every 2s
- **Simulated battery** draining 1% every 30 seconds
- **Structured Serial output** at 115200 baud:

```
[t=1024ms] Distance: 34.2cm | Zone: DANGER | Bat: 87%
[t=1524ms] >> System toggled OFF
[SYSTEM OFF]
```

---



## 📊 Python Dashboard Features

- **Live serial parsing** — structured data extracted from every Serial line
- **Rolling statistics** — mean, min, max distance over last 20 readings
- **Zone distribution** — live bar chart of SAFE / WARNING / DANGER counts
- **Alert system:**
  - Sustained DANGER (3 consecutive readings) → `⚠️ SUSTAINED DANGER`
  - Battery below 20% → `🔋 CRITICAL BATTERY`
  - Dashboard flashes red on alert
- **Auto CSV logging** — every valid reading saved to `data/sensor_log.csv`
- **Summary export** — per-zone statistics saved to `data/summary.csv` every 60 seconds
- **Terminal status panel** — refreshes on every new reading

---


## 🧠 Skills Demonstrated

- Embedded C/C++ in the Arduino framework (PlatformIO)
- Non-blocking timing with `millis()`
- Hardware debouncing and state machines
- I2C-free LCD integration (4-bit parallel mode)
- Python serial communication with `pyserial`
- Real-time data processing with `pandas`
- Live data visualisation with `matplotlib`
- Multithreading with `threading.Lock()` for shared state
- Generator patterns for data streaming
- CSV logging and automated report export
- End-to-end IoT pipeline design

---

## 👤 Author

Built as part of a self-directed embedded systems and Python learning journey.
Background: BSc Mechatronics Engineering.
Focus: Embedded Systems | IoT | Robotics

---

## 📄 License

MIT License — free to use, modify and distribute with attribution.
