# logging_utils.py
from datetime import datetime

def log_action(action, filename, algorithm, status, output_path):
    with open("log.txt", "a") as f:
        f.write(f"{datetime.now()} | {action.upper()} | {filename} | {algorithm} | {status} | {output_path}\n")