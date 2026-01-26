import time
from typing import Any, Dict


def success_response(data: Any, message: str = "Request Successful") -> Dict[str, Any]:
    return {
        "status": "success",
        "message": message,
        "data": data,
        "timestamp": int(time.time() * 1000),
    }


def failure_response(message: str, data: Any = None) -> Dict[str, Any]:
    return {
        "status": "failure",
        "message": message,
        "data": data,
        "timestamp": int(time.time() * 1000),
    }
