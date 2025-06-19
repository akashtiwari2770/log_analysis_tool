import os
import subprocess

if __name__ == "__main__":
    os.makedirs("data/logs", exist_ok=True)
    with open("data/logs/demo.csv", "w") as f:
        f.write("""Timestamp,Level,Component,Message
2023-06-01 10:00,INFO,Demo,Service started
2023-06-01 10:05,ERROR,Demo,Connection failed
2023-06-01 10:10,ERROR,Demo,Authentication failed
""")
    subprocess.run([
        "python", "app/analyze_logs.py",
        "--logs", "data/logs",
        "--term", "error",
        "--verbose"
    ], check=True)
