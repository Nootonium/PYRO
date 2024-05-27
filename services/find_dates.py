import re
from datetime import datetime


def find_dates(text):
    # Pattern to match most common date formats
    full_date_pattern  = r'\b(20\d{2})[-/ ]?(0[1-9]|1[0-2])[-/ ]?(0[1-9]|[12]\d|3[01])\b|\b(0[1-9]|[12]\d|3[01])[-/ ]?(0[1-9]|1[0-2])[-/ ]?(20\d{2})\b'
    partial_date_pattern = r'\b(\d{2})[-/ ]?(0[1-9]|1[0-2])[-/ ]?(0[1-9]|[12]\d|3[01])\b|\b(0[1-9]|[12]\d|3[01])[-/ ]?(0[1-9]|1[0-2])[-/ ]?(\d{2})\b'

    full_dates = re.findall(full_date_pattern, text)
    partial_dates = re.findall(partial_date_pattern, text)

    formatted_dates = []

    # Handle full dates
    for date in full_dates:
        if date[0]:  # Format is YYYY-MM-DD
            year, month, day = date[0], date[1], date[2]
        else:  # Format is DD-MM-YYYY
            day, month, year = date[3], date[4], date[5]
        formatted_dates.append(f"{year}-{month}-{day}")

    # Handle partial dates (assuming they are meant to be in the 21st century)
    for date in partial_dates:
        if date[0]:  # Format is YY-MM-DD
            year, month, day = f"20{date[0]}", date[1], date[2]
        else:  # Format is DD-MM-YY
            day, month, year = date[3], date[4], f"20{date[5]}"
        formatted_dates.append(f"{year}-{month}-{day}")

    # Ensure all dates are in ISO 8601 format
    formatted_dates = [datetime.strptime(date, "%Y-%m-%d").strftime("%Y-%m-%d") for date in formatted_dates]

    return formatted_dates