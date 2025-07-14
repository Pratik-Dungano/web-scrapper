"""
utils.py
Shared utility functions for validation, logging, etc.
"""
import sys
from datetime import datetime

LOG_FILE = "scraper_errors.log"

def log_error(message: str) -> None:
    """
    Log an error message to the console and append to a log file.
    Args:
        message (str): The error message to log.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] [ERROR] {message}"
    print(formatted, file=sys.stderr)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception as e:
        print(f"[ERROR] Failed to write to log file: {e}", file=sys.stderr)

# Additional utility functions can be added here as needed.
