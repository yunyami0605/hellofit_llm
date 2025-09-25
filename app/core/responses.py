from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    message: Optional[str] = None

    @staticmethod
    def ok(data: T = None, message: str = "success") -> "ApiResponse[T]":
        return ApiResponse(success=True, data=data, message=message)

    @staticmethod
    def fail(message: str = "error") -> "ApiResponse[None]":
        return ApiResponse(success=False, message=message)
