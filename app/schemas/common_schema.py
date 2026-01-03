from pydantic import BaseModel
from typing import Generic, TypeVar, List, Optional

T = TypeVar('T')

class PaginationSchema(BaseModel, Generic[T]):
    page: int
    size: int
    tatal: int
    total_pages: int

class ResponseSchema(BaseModel, Generic[T]):
    data: Optional[T] = None
    message: str = "Success"
    pagination: Optional[PaginationSchema] = None

class TokenData(BaseModel):
    username: Optional[str] = None