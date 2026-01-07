from pydantic import BaseModel
from typing import Generic, TypeVar, List, Optional

T = TypeVar('T')

class PaginationSchema(BaseModel, Generic[T]):
    page: int
    size: int
    total: int
    total_pages: int

class ResponseSchema(BaseModel, Generic[T]):
    data: Optional[T] = None
    message: str = "Success"
    pagination: Optional[PaginationSchema] = None

    @classmethod
    def custom_response(cls, code: str, message: str, data: T, pagination: PaginationSchema = None):
        return cls(code=code, message=message, data=data, pagination=pagination)

    @classmethod
    def success_response(cls, data: T):
        return cls(code='000', message='success', data=data)

class TokenData(BaseModel):
    username: Optional[str] = None