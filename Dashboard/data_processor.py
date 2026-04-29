import os
import csv
from collections import deque, Counter
import pandas as pd


# ── A — CSV Logger 
def log_to_csv(reading, filepath="data/sensor_log.csv"):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    # Only log valid sensor readings
    required_keys = {"system_time", "distance", "zone", "battery"}
    if not required_keys.issubset(reading.keys()):
        return

    file_exists = os.path.isfile(filepath)

    with open(filepath, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "distance", "zone", "battery"])

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "timestamp": reading["system_time"],
            "distance":  reading["distance"],
            "zone":      reading["zone"],
            "battery":   reading["battery"]
        })


# ── B — Rolling Buffer ─
class SensorBuffer:
    def __init__(self, size=20):
        self.buffer = deque(maxlen=size)

    def add(self, reading):
        self.buffer.append(reading)

    def get_stats(self):
        if not self.buffer:
            return None

        distances = [r["distance"] for r in self.buffer if r.get("zone") != "--"]
        zones     = [r["zone"]     for r in self.buffer if r.get("zone") != "--"]
        batteries = [r["battery"]  for r in self.buffer]

        return {
            "count":       len(self.buffer),
            "dist_mean":   round(sum(distances) / len(distances), 2) if distances else None,
            "dist_min":    round(min(distances), 2) if distances else None,
            "dist_max":    round(max(distances), 2) if distances else None,
            "bat_mean":    round(sum(batteries) / len(batteries), 2) if batteries else None,
            "zone_counts": dict(Counter(zones))
        }

    def get_alert(self):
        if len(self.buffer) < 3:
            return None

        last_three = list(self.buffer)[-3:]

        # Sustained danger check
        if all(r.get("zone") == "DANGER" for r in last_three):
            return "  SUSTAINED DANGER — object very close!"

        # Battery check
        latest = self.buffer[-1]
        if latest.get("battery", 100) < 20:
            return " CRITICAL BATTERY"

        return None


# ── C — Data Exporter ─────────────────────────────
def export_summary(filepath="data/summary.csv", source_file="data/sensor_log.csv"):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    if not os.path.isfile(source_file):
        print("No sensor_log.csv found")
        return

    df = pd.read_csv(source_file)

    if df.empty:
        print(" Log file is empty")
        return

    summary = df.groupby("zone").agg(
        count       = ("zone",     "count"),
        dist_mean   = ("distance", "mean"),
        dist_min    = ("distance", "min"),
        dist_max    = ("distance", "max"),
    ).round(2).reset_index()

    summary.to_csv(filepath, index=False)
    print(f" Summary exported to {filepath}")