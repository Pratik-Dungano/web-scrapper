"""
utils.py
Shared utility functions for validation, logging, etc.
"""
import sys
from datetime import datetime
import random
import yaml

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

def log_info(message: str) -> None:
    """
    Log an info message to the console and append to a log file.
    Args:
        message (str): The info message to log.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] [INFO] {message}"
    print(formatted)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception as e:
        print(f"[ERROR] Failed to write to log file: {e}", file=sys.stderr)

def get_proxies(proxy_file: str) -> list:
    """
    Load proxies from a file (one per line).
    Returns a list of proxy URLs.
    """
    try:
        with open(proxy_file, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except Exception:
        return []

def get_delay(min_delay: float, max_delay: float) -> float:
    """
    Return a random delay between min_delay and max_delay seconds.
    """
    return random.uniform(min_delay, max_delay)

def load_config(config_file: str) -> dict:
    """
    Load YAML config file for custom selectors/regex.
    Returns a dict or empty dict if not found/invalid.
    """
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}

# Additional utility functions can be added here as needed.
