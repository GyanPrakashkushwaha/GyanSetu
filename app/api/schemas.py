from pydantic import BaseModel
from typing import TypeVar, Generic, Optional

# 1. Define the Generic Type Variable
T = TypeVar("T")

# 2. Inherit from both BaseModel AND Generic[T]
class APIResponse(BaseModel, Generic[T]):
    """Standardized wrapper for all API responses."""
    success: bool
    message: str
    data: Optional[T] = None  # Using Optional in case an endpoint returns no payload