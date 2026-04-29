import serial
import time
import datetime

# ── Config ────────────────────────────────────────
PORT      = "COM4"
BAUD_RATE = 115200


def connect_serial():
    while True:
        try:
            ser = serial.Serial(PORT, BAUD_RATE, timeout=1)
            print(f"Connected to {PORT}")
            time.sleep(2)  # wait for ESP32 reset
            return ser
        except serial.SerialException:
            print(" Serial not available — retrying in 2s...")
            time.sleep(2)


def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_time_short():
    return datetime.datetime.now().strftime("%H:%M:%S")


def parse_line(line):
    """
    Parses a serial line into a structured dict.
    Returns None if line cannot be parsed.
    """
    now = get_timestamp()

    # ── System event lines 
    if "[SYSTEM OFF]" in line:
        return {"event": "SYSTEM_OFF", "system_time": now}

    if "[SYSTEM ON]" in line:
        return {"event": "SYSTEM_ON", "system_time": now}

    if "OUT OF RANGE" in line:
        return {"event": "OUT_OF_RANGE", "system_time": now}

    if ">>" in line:
        return None  

    # ── Sensor reading lines 
    # Format: "[t=1024ms] Distance: 34.2cm | Zone: DANGER | Bat: 87%"
    try:
        parts = line.split(" | ")
        if len(parts) != 3:
            return None

        # ── Extract timestamp_ms 
        # parts[0] = "[t=1024ms] Distance: 34.2cm"
        bracket_part = parts[0]  # "[t=1024ms] Distance: 34.2cm"

        # Extract ms value between "t=" and "ms]"
        t_start   = bracket_part.index("t=") + 2
        t_end     = bracket_part.index("ms]")
        timestamp_ms = int(bracket_part[t_start:t_end])

        # Extract distance — after "Distance: " and before "cm"
        dist_str  = bracket_part.split("Distance: ")[1]
        distance  = float(dist_str.replace("cm", "").strip())

        # ── Extract zone 
        zone = parts[1].replace("Zone: ", "").strip()

        # ── Extract battery 
        bat_str  = parts[2].replace("Bat: ", "").replace("%", "").strip()
        battery  = int(bat_str)

        return {
            "timestamp_ms": timestamp_ms,
            "distance":     distance,
            "zone":         zone,
            "battery":      battery,
            "system_time":  now
        }

    except (ValueError, IndexError):
        return None  # unparseable line — skip silently


def serial_reader():
    """
    Generator — yields parsed dicts from serial port.
    Handles reconnection automatically.
    """
    ser = connect_serial()

    while True:
        try:
            if ser.in_waiting:
                line = ser.readline().decode(errors='ignore').strip()

                if not line:
                    continue

                parsed = parse_line(line)

                if parsed is None:
                    continue

                # ── Terminal print 
                t = get_time_short()

                if "event" in parsed:
                    if parsed["event"] == "SYSTEM_OFF":
                        print(f" [{t}] SYSTEM OFF")
                    elif parsed["event"] == "SYSTEM_ON":
                        print(f" [{t}] SYSTEM ON")
                    elif parsed["event"] == "OUT_OF_RANGE":
                        print(f"  [{t}] OUT OF RANGE")
                else:
                    print(f" [{t}] "
                          f"Dist: {parsed['distance']}cm | "
                          f"Zone: {parsed['zone']} | "
                          f"Bat: {parsed['battery']}%")

                yield parsed

        except serial.SerialException:
            print("  Disconnected — reconnecting...")
            ser.close()
            ser = connect_serial()

        except KeyboardInterrupt:
            print("\n Stopping serial reader...")
            ser.close()
            break

# 
def main():
    print("Smart Proximity Alert — Serial Reader")
    print("─" * 40)
    for reading in serial_reader():
        pass  # pipeline.py will consume this — for now just print

if __name__ == "__main__":
    main()