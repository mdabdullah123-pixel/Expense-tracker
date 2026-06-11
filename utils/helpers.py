"""
Helper utilities for the Expense Tracker application.

Provides common helper functions for currency formatting, validation,
date handling, report generation, and logging setup.
"""

import logging
import os
import re
from datetime import date, datetime, timedelta
from typing import Optional, Tuple


def setup_logging(level: str = "INFO") -> None:
    """
    Configure application-wide logging.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(os.path.join("data", "app.log"), mode="a"),
        ],
    )


def format_currency(amount: float) -> str:
    """
    Format a number as Indian Rupee currency string.
    
    Args:
        amount: Numeric amount to format
        
    Returns:
        Formatted currency string (e.g., "₹1,234.56")
    """
    return f"₹{amount:,.2f}"


def validate_amount(amount_str: str) -> Tuple[bool, Optional[float], str]:
    """
    Validate and parse a monetary amount from string input.
    
    Args:
        amount_str: String representation of amount
        
    Returns:
        Tuple of (is_valid, parsed_amount, error_message)
    """
    if not amount_str or not amount_str.strip():
        return False, None, "Amount is required"
    
    try:
        # Remove currency symbols and whitespace
        cleaned = amount_str.strip().replace("₹", "").replace(",", "").strip()
        amount = float(cleaned)
        
        if amount <= 0:
            return False, None, "Amount must be greater than 0"
        
        if amount > 999999999:  # ~10 crore limit
            return False, None, "Amount seems too large"
        
        return True, amount, ""
        
    except (ValueError, TypeError):
        return False, None, "Invalid amount format"


def get_date_range(period: str, custom_start: Optional[date] = None, custom_end: Optional[date] = None) -> Tuple[date, date]:
    """
    Get start and end dates based on a predefined period or custom range.
    
    Args:
        period: "week", "month", "quarter", "year", "all", "custom"
        custom_start: Custom start date (used with period="custom")
        custom_end: Custom end date (used with period="custom")
        
    Returns:
        Tuple of (start_date, end_date)
    """
    today = date.today()
    
    if period == "week":
        start = today - timedelta(days=today.weekday())  # Monday of current week
        end = today
    elif period == "month":
        start = date(today.year, today.month, 1)
        end = today
    elif period == "quarter":
        # First day of current quarter
        quarter_month = ((today.month - 1) // 3) * 3 + 1
        start = date(today.year, quarter_month, 1)
        end = today
    elif period == "year":
        start = date(today.year, 1, 1)
        end = today
    elif period == "custom" and custom_start and custom_end:
        start = custom_start
        end = custom_end
    else:  # "all" or fallback
        start = date(2020, 1, 1)  # From 2020 for all data
        end = today
    
    return start, end


def generate_markdown_report(title: str, sections: list) -> str:
    """
    Generate a markdown formatted report from sections.
    
    Args:
        title: Report title
        sections: List of dicts with 'heading' and 'content' keys
        
    Returns:
        Markdown formatted string
    """
    report = [
        f"# {title}",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "---",
        "",
    ]
    
    for section in sections:
        report.append(f"## {section['heading']}")
        report.append("")
        report.append(section["content"])
        report.append("")
        report.append("---")
        report.append("")
    
    return "\n".join(report)


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent injection attacks.
    
    Args:
        text: User input text
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    # Remove potentially dangerous characters
    sanitized = re.sub(r"[<>\"'%;()&]", "", text)
    return sanitized.strip()


def parse_amount_from_text(text: str) -> Optional[float]:
    """
    Extract a monetary amount from text.
    
    Args:
        text: Text that may contain an amount (e.g., "₹450" or "Rs. 450")
        
    Returns:
        Parsed amount or None if not found
    """
    if not text:
        return None
    
    # Patterns: ₹450, Rs. 450, INR 450, 450 rupees
    patterns = [
        r"₹\s*(\d+(?:\.\d{1,2})?)",
        r"Rs\.?\s*(\d+(?:\.\d{1,2})?)",
        r"INR\s*(\d+(?:\.\d{1,2})?)",
        r"(\d+(?:\.\d{1,2})?)\s*rupees?",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))
    
    return None