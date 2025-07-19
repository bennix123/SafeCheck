# response_handler.py
from fastapi import status
from fastapi.responses import JSONResponse
from typing import Any, Dict, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class APIResponseHandler:
    """
    A standardized response handler for API operations
    Formats all responses consistently with:
    - success: boolean indicating status
    - message: human-readable message
    - data: response payload (if successful)
    - error: error details (if failed)
    - timestamp: time of response
    """
    
    @staticmethod
    def success_response(
        data: Any = None,
        message: str = "Operation successful",
        status_code: int = status.HTTP_200_OK,
        meta: Optional[Dict] = None
    ) -> JSONResponse:
        response = {
            "success": True,
            "message": message,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if meta:
            response["meta"] = meta
            
        return JSONResponse(
            content=response,
            status_code=status_code
        )

    @staticmethod
    def error_response(
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_details: Optional[Dict] = None,
        error_code: Optional[str] = None
    ) -> JSONResponse:
        response = {
            "success": False,
            "message": message,
            "error": {
                "code": error_code,
                "details": error_details or {}
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return JSONResponse(
            content=response,
            status_code=status_code
        )

   