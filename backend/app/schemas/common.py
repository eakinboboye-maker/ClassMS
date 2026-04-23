from typing import Generic, TypeVar, Any
from pydantic import BaseModel

T = TypeVar("T")


class MessageResponse(BaseModel):
    message: str


class StatusResponse(BaseModel):
    status: str
    detail: str | None = None


class PaginatedMeta(BaseModel):
    total: int
    limit: int | None = None
    offset: int | None = None


class Envelope(BaseModel, Generic[T]):
    success: bool = True
    data: T | None = None
    message: str | None = None


class PaginatedEnvelope(BaseModel, Generic[T]):
    success: bool = True
    data: list[T]
    meta: PaginatedMeta
    message: str | None = None


class ErrorEnvelope(BaseModel):
    success: bool = False
    error: str
    details: Any | None = None
