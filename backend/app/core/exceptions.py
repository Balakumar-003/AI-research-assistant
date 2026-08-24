from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.logger import logger

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error: {exc.errors()}", extra={"request_id": getattr(request.state, "request_id", "unknown")})
    return JSONResponse(
        status_code=422,
        content={"detail": "Invalid request parameters", "errors": exc.errors()},
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.error(f"HTTP error: {exc.detail}", extra={"request_id": getattr(request.state, "request_id", "unknown")})
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Internal server error: {str(exc)}", exc_info=exc, extra={"request_id": getattr(request.state, "request_id", "unknown")})
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred."},
    )
