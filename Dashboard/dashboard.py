import os
import threading
from collections import deque

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from serial_reader import serial_reader
from data_processor import log_to_csv, SensorBuffer

# ── Shared state ──────────────────────────────────
latest_reading   = {}
distance_history = deque(maxlen=20)
buffer           = SensorBuffer(size=20)
lock             = threading.Lock()
flash_flag       = False
flash_counter    = 0

# ── Terminal panel ────────────────────────────────
def print_panel():
    os.system('cls' if os.name == 'nt' else 'clear')

    with lock:
        if not latest_reading:
            print(" Waiting for data...")
            return

        stats = buffer.get_stats()
        alert = buffer.get_alert()
        zone_icon = {"SAFE": "GREEN", "WARNING": "YELLOW", "DANGER": "RED"}.get(
            latest_reading.get('zone', ''), "WHITE")

        print("╔══════════════════════════════════════╗")
        print("║   SMART PROXIMITY ALERT DASHBOARD   ║")
        print("╠══════════════════════════════════════╣")
        print(f"║ Time:      {latest_reading['system_time']}      ║")
        print(f"║ Distance:  {latest_reading['distance']}cm".ljust(39) + "║")
        print(f"║ Zone:      {latest_reading['zone']} {zone_icon}".ljust(39) + "║")
        print(f"║ Battery:   {latest_reading['battery']}%".ljust(39) + "║")
        print("╠══════════════════════════════════════╣")
        print("║ STATS (last 20 readings)             ║")
        if stats:
            print(f"║ Avg Dist:  {stats['dist_mean']}cm".ljust(39) + "║")
            print(f"║ Min Dist:  {stats['dist_min']}cm".ljust(39) + "║")
            print(f"║ Max Dist:  {stats['dist_max']}cm".ljust(39) + "║")
            zones_str = " ".join(
                f"{k}:{v}" for k, v in stats['zone_counts'].items())
            print(f"║ Zones:     {zones_str}".ljust(39) + "║")
        print("╠══════════════════════════════════════╣")
        if alert:
            print(f"║ {alert}".ljust(39) + "║")
        else:
            print("║ No alerts                            ║")
        print("-----------------")

# ── Serial thread ─────────────────────────────────
def read_serial_thread():
    global latest_reading, flash_flag

    for parsed in serial_reader():
        if "event" in parsed:
            continue

        with lock:
            latest_reading = parsed
            distance_history.append(parsed["distance"])
            buffer.add(parsed)

        log_to_csv(parsed)

        alert = buffer.get_alert()
        if alert:
            flash_flag = True

        print_panel()  # update terminal on new data

# ── Chart setup 
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7))

# ── Chart update
def update_chart(frame):
    global flash_flag, flash_counter

    with lock:
        distances = list(distance_history)
        stats     = buffer.get_stats()

    # ── Plot 1 — Distance history ─────────────────
    ax1.clear()
    ax1.plot(distances, marker='o', color='steelblue',
             linewidth=2, label='Distance')
    ax1.axhline(y=100, color='green',  linestyle='--',
                linewidth=1.5, label='Safe boundary')
    ax1.axhline(y=40,  color='orange', linestyle='--',
                linewidth=1.5, label='Warning boundary')
    ax1.set_title("Distance — Last 20 Readings")
    ax1.set_ylabel("Distance (cm)")
    ax1.set_xlabel("Reading")
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(0, 420)

    # ── Plot 2 — Zone distribution ────────────────
    ax2.clear()
    if stats:
        zones  = ["SAFE", "WARNING", "DANGER"]
        counts = [stats["zone_counts"].get(z, 0) for z in zones]
        colors = ['green', 'orange', 'red']
        ax2.bar(zones, counts, color=colors, edgecolor='black')
    ax2.set_title("Zone Distribution")
    ax2.set_ylabel("Count")
    ax2.set_xlabel("Zone")
    ax2.grid(axis='y', alpha=0.3)

    # ── Alert flash 
    if flash_flag:
        fig.patch.set_facecolor('red')
        flash_counter += 1
        if flash_counter >= 1:
            flash_flag    = False
            flash_counter = 0
    else:
        fig.patch.set_facecolor('white')

    plt.tight_layout()

# ── Main 
def main():
    print("Starting Smart Proximity Dashboard...")
    print(" Ensure Serial Monitor is CLOSED\n")

    thread = threading.Thread(target=read_serial_thread, daemon=True)
    thread.start()

    ani = FuncAnimation(fig, update_chart, interval=500)
    plt.show()

if __name__ == "__main__":
    main()