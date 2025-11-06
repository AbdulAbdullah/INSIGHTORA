"""
Response and Data Formatters

Reusable formatting utilities for consistent API responses.
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from decimal import Decimal
import json


def success_response(
    data: Any = None,
    message: str = "Success",
    meta: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Format successful API response.
    
    Args:
        data: Response data
        message: Success message
        meta: Additional metadata
        
    Returns:
        Dict: Formatted response
    """
    response = {
        "success": True,
        "message": message,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if meta:
        response["meta"] = meta
    
    return response


def error_response(
    error: str,
    message: str = "An error occurred",
    details: Optional[Dict[str, Any]] = None,
    code: Optional[str] = None
) -> Dict[str, Any]:
    """
    Format error API response.
    
    Args:
        error: Error type/code
        message: Error message
        details: Additional error details
        code: Error code
        
    Returns:
        Dict: Formatted error response
    """
    response = {
        "success": False,
        "error": error,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if details:
        response["details"] = details
    
    if code:
        response["code"] = code
    
    return response


def paginated_response(
    items: List[Any],
    total: int,
    page: int,
    page_size: int,
    message: str = "Success"
) -> Dict[str, Any]:
    """
    Format paginated API response.
    
    Args:
        items: List of items for current page
        total: Total number of items
        page: Current page number
        page_size: Items per page
        message: Success message
        
    Returns:
        Dict: Formatted paginated response
    """
    total_pages = (total + page_size - 1) // page_size
    
    return success_response(
        data=items,
        message=message,
        meta={
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_items": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1
            }
        }
    )


def format_datetime(dt: datetime, format_type: str = "iso") -> str:
    """
    Format datetime for API responses.
    
    Args:
        dt: Datetime object
        format_type: Format type ("iso", "human", "date_only")
        
    Returns:
        str: Formatted datetime string
    """
    if format_type == "iso":
        return dt.isoformat()
    elif format_type == "human":
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    elif format_type == "date_only":
        return dt.strftime("%Y-%m-%d")
    else:
        return dt.isoformat()


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        str: Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def format_currency(amount: Union[int, float, Decimal], currency: str = "USD") -> str:
    """
    Format currency amount.
    
    Args:
        amount: Currency amount
        currency: Currency code
        
    Returns:
        str: Formatted currency string
    """
    if currency == "USD":
        return f"${amount:,.2f}"
    elif currency == "EUR":
        return f"€{amount:,.2f}"
    elif currency == "GBP":
        return f"£{amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"


def format_percentage(value: Union[int, float], decimal_places: int = 1) -> str:
    """
    Format percentage value.
    
    Args:
        value: Percentage value (0-100)
        decimal_places: Number of decimal places
        
    Returns:
        str: Formatted percentage string
    """
    return f"{value:.{decimal_places}f}%"


def sanitize_for_json(obj: Any) -> Any:
    """
    Sanitize object for JSON serialization.
    
    Args:
        obj: Object to sanitize
        
    Returns:
        JSON-serializable object
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, set):
        return list(obj)
    elif hasattr(obj, '__dict__'):
        return {k: sanitize_for_json(v) for k, v in obj.__dict__.items() if not k.startswith('_')}
    elif isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [sanitize_for_json(item) for item in obj]
    else:
        return obj


def format_chart_data(data: List[Dict[str, Any]], chart_type: str) -> Dict[str, Any]:
    """
    Format data for chart visualization.
    
    Args:
        data: Raw data
        chart_type: Type of chart (bar, line, pie, etc.)
        
    Returns:
        Dict: Formatted chart data
    """
    if chart_type in ["bar", "line"]:
        return {
            "labels": [item.get("label", "") for item in data],
            "datasets": [{
                "data": [item.get("value", 0) for item in data],
                "label": "Data"
            }]
        }
    elif chart_type == "pie":
        return {
            "labels": [item.get("label", "") for item in data],
            "data": [item.get("value", 0) for item in data]
        }
    else:
        return {"data": data}