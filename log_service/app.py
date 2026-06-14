import time
import os

log_file_path = "/var/log/shared/access.json"

print("🎧 Log Service started. Watching shared JSON log file...", flush=True)

while not os.path.exists(log_file_path):
    time.sleep(1)

with open(log_file_path, "r") as f:
    f.seek(0, 2)
    while True:
        line = f.readline()
        if not line:
            time.sleep(0.1)
            continue

        print(f"📊 [LOG ENGINE] Processed telemetry line: {line.strip()}", flush=True)
