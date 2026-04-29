import threading
import time
import sys
import datetime

from serial_reader import PORT, BAUD_RATE
from data_processor import export_summary
import dashboard  # imports and runs main dashboard

# =========================================================
# CONFIG
# =========================================================
EXPORT_INTERVAL = 60  # seconds
RUNNING = True

# =========================================================
# EXPORT THREAD
# =========================================================
def export_thread():
    global RUNNING

    while RUNNING:
        time.sleep(EXPORT_INTERVAL)
        try:
            export_summary()
        except Exception as e:
            print(f" Export error: {e}")


# =========================================================
# STARTUP INFO
# =========================================================
def print_startup():
    started = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("\n SMART PROXIMITY PIPELINE STARTED")
    print("─" * 50)
    print(f"Started     : {started}")          
    print(f"Serial Port : {PORT}")
    print(f"Baud Rate   : {BAUD_RATE}")
    print(f"Log File    : data/sensor_log.csv")
    print(f"Summary File: data/summary.csv")
    print(f"Export Rate : every {EXPORT_INTERVAL}s")
    print("─" * 50)
    print(" Close PlatformIO Serial Monitor before running")
    print("Press Ctrl+C to stop\n")


# =========================================================
# MAIN
# =========================================================
def main():
    global RUNNING

    print_startup()

    # Start export thread
    t_export = threading.Thread(target=export_thread, daemon=True)
    t_export.start()

    try:
        # Run dashboard (this blocks due to matplotlib)
        dashboard.main()

    except KeyboardInterrupt:
        print("\n Shutdown signal received...")

    finally:
        RUNNING = False

        # Final export
        print("💾 Saving final summary...")
        try:
            export_summary()
        except Exception as e:
            print(f" Final export failed: {e}")

        print("\n Goodbye!")
        sys.exit(0)


# =========================================================
if __name__ == "__main__":
    main()