from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional, Any

T = TypeVar("T") 

class APIResponse(BaseModel, Generic[T]):
    success: bool = Field(..., description="Indicates if the operation was successful")
    message: str = Field(..., description="Human-readable status message")
    data: Optional[T] = Field(default=None, description="The payload (if successful)")
    error_details: Optional[Any] = Field(default=None, description="Debugging details (if failed)")