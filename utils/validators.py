"""
Validation utilities
"""
import json
from typing import Dict, Any, List
from utils.logger import get_logger

logger = get_logger(__name__)

def validate_json_schema(data: Dict[str, Any], required_keys: List[str]) -> bool:
    """
    Validate that JSON data contains required keys
    
    Args:
        data: JSON data as dict
        required_keys: List of required key names
        
    Returns:
        True if valid, raises ValueError if invalid
    """
    missing_keys = [key for key in required_keys if key not in data]
    
    if missing_keys:
        error_msg = f"Missing required keys: {missing_keys}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    return True

def safe_float(value: Any, default: float = 0.0) -> float:
    """Safely convert value to float"""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

def safe_int(value: Any, default: int = 0) -> int:
    """Safely convert value to int"""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
