from datetime import datetime, timedelta
import re


def format_date_for_jagriti(date_obj) -> str:
    """Format date object to string format expected by Jagriti API (ISO format)"""
    if date_obj is None:
        return ""
    return date_obj.strftime("%Y-%m-%d")


def get_default_date_range():
    """Get default date range (last 30 days)"""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    return start_date, end_date


def clean_text(text: str) -> str:
    """Clean and normalize text data"""
    if not text:
        return ""
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text.strip())
    return text


def normalize_state_name(state_name: str) -> str:
    """Normalize state name to match Jagriti format"""
    return state_name.upper().strip()


def normalize_commission_name(commission_name: str) -> str:
    """Normalize commission name to match Jagriti format"""
    return commission_name.strip()


def validate_search_value(search_value: str) -> bool:
    """Validate search value"""
    if not search_value or len(search_value.strip()) < 2:
        return False
    return True
