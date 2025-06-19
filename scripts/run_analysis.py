import subprocess

if __name__ == "__main__":
    subprocess.run([
        "python", "app/analyze_logs.py",
        "--logs", "data/logs",
        "--term", "error",
        "--verbose"
    ], check=True)