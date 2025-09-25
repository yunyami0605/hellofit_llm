from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.core.logger import logger

class AppException(HTTPException):
    def __init__(self, status_code: int, message: str):
        super().__init__(status_code=status_code, detail=message)


async def app_exception_handler(request: Request, exc: AppException):
    logger.error(f"Error occurred: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "path": str(request.url)},
    )
