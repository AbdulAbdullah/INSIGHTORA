"""
Reusable Validation Functions

Common validation utilities used across modules.
"""

import re
from typing import Optional, List, Dict, Any
from email_validator import validate_email, EmailNotValidError
import phonenumbers
from phonenumbers import NumberParseException


def validate_email_address(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        bool: True if valid email format
    """
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False


def validate_password_strength(password: str) -> Dict[str, Any]:
    """
    Validate password strength and return detailed feedback.
    
    Args:
        password: Password to validate
        
    Returns:
        Dict containing validation results
    """
    result = {
        "is_valid": True,
        "score": 0,
        "feedback": [],
        "requirements": {
            "min_length": len(password) >= 8,
            "has_uppercase": bool(re.search(r'[A-Z]', password)),
            "has_lowercase": bool(re.search(r'[a-z]', password)),
            "has_digit": bool(re.search(r'\d', password)),
            "has_special": bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password)),
            "no_common_patterns": not _has_common_patterns(password)
        }
    }
    
    score = sum(result["requirements"].values())
    result["score"] = score
    
    if not result["requirements"]["min_length"]:
        result["feedback"].append("Password must be at least 8 characters long")
    
    if not result["requirements"]["has_uppercase"]:
        result["feedback"].append("Password must contain at least one uppercase letter")
    
    if not result["requirements"]["has_lowercase"]:
        result["feedback"].append("Password must contain at least one lowercase letter")
    
    if not result["requirements"]["has_digit"]:
        result["feedback"].append("Password must contain at least one digit")
    
    if not result["requirements"]["has_special"]:
        result["feedback"].append("Password must contain at least one special character")
    
    if not result["requirements"]["no_common_patterns"]:
        result["feedback"].append("Password contains common patterns and is easily guessable")
    
    result["is_valid"] = score >= 5
    
    return result


def _has_common_patterns(password: str) -> bool:
    """Check for common password patterns."""
    common_patterns = [
        r'123456',
        r'password',
        r'qwerty',
        r'abc123',
        r'admin',
        r'letmein',
        r'welcome',
        r'monkey',
        r'dragon'
    ]
    
    password_lower = password.lower()
    return any(re.search(pattern, password_lower) for pattern in common_patterns)


def validate_phone_number(phone: str, country_code: Optional[str] = None) -> Dict[str, Any]:
    """
    Validate phone number format.
    
    Args:
        phone: Phone number to validate
        country_code: ISO country code (e.g., 'US', 'GB')
        
    Returns:
        Dict containing validation results
    """
    try:
        parsed_number = phonenumbers.parse(phone, country_code)
        
        return {
            "is_valid": phonenumbers.is_valid_number(parsed_number),
            "is_possible": phonenumbers.is_possible_number(parsed_number),
            "formatted": phonenumbers.format_number(
                parsed_number, 
                phonenumbers.PhoneNumberFormat.INTERNATIONAL
            ),
            "country_code": phonenumbers.region_code_for_number(parsed_number),
            "number_type": phonenumbers.number_type(parsed_number).name
        }
    except NumberParseException as e:
        return {
            "is_valid": False,
            "error": str(e),
            "formatted": None,
            "country_code": None,
            "number_type": None
        }


def validate_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        bool: True if valid URL format
    """
    url_pattern = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(url_pattern.match(url))


def validate_json_structure(data: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
    """
    Validate JSON structure against required fields.
    
    Args:
        data: JSON data to validate
        required_fields: List of required field names
        
    Returns:
        Dict containing validation results
    """
    missing_fields = []
    invalid_fields = []
    
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
        elif data[field] is None or data[field] == "":
            invalid_fields.append(field)
    
    return {
        "is_valid": len(missing_fields) == 0 and len(invalid_fields) == 0,
        "missing_fields": missing_fields,
        "invalid_fields": invalid_fields
    }


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage.
    
    Args:
        filename: Original filename
        
    Returns:
        str: Sanitized filename
    """
    safe_filename = re.sub(r'[^\w\-_\.]', '_', filename)
    
    safe_filename = re.sub(r'_+', '_', safe_filename)
    
    if len(safe_filename) > 100:
        name, ext = safe_filename.rsplit('.', 1) if '.' in safe_filename else (safe_filename, '')
        safe_filename = name[:95] + ('.' + ext if ext else '')
    
    return safe_filename


def validate_sql_query(query: str) -> Dict[str, Any]:
    """
    Basic SQL query validation for security.
    
    Args:
        query: SQL query to validate
        
    Returns:
        Dict containing validation results
    """
    dangerous_patterns = [
        r'\bDROP\b',
        r'\bDELETE\b',
        r'\bTRUNCATE\b',
        r'\bALTER\b',
        r'\bCREATE\b',
        r'\bINSERT\b',
        r'\bUPDATE\b',
        r'\bEXEC\b',
        r'\bEXECUTE\b',
        r'--',
        r'/\*',
        r'xp_',
        r'sp_',
    ]
    
    query_upper = query.upper()
    detected_patterns = []
    
    for pattern in dangerous_patterns:
        if re.search(pattern, query_upper):
            detected_patterns.append(pattern.replace('\\b', '').replace('\\', ''))
    
    return {
        "is_safe": len(detected_patterns) == 0,
        "detected_patterns": detected_patterns,
        "is_select_only": query_upper.strip().startswith('SELECT')
    }