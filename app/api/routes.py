

T = TypeVar("T")

class APIResponseModel(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None