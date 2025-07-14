"""
output.py
Handles outputting extracted data to CSV or JSON formats.
"""
from typing import List, Dict
import csv
import json


def write_csv(data: List[Dict[str, str]], filename: str) -> None:
    """
    Write extracted data to a CSV file.
    Args:
        data (List[Dict[str, str]]): List of extracted company info dicts.
        filename (str): Output CSV file name.
    """
    if not data:
        return
    fieldnames = list(data[0].keys())
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def write_json(data: List[Dict[str, str]], filename: str) -> None:
    """
    Write extracted data to a JSON file.
    Args:
        data (List[Dict[str, str]]): List of extracted company info dicts.
        filename (str): Output JSON file name.
    """
    with open(filename, mode='w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
