"""Generic response shapes shared by all endpoints (CONTRACTS §1)."""
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class Schema(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class Page(Schema, Generic[T]):
    items: list[T]
    total: int
    page: int = 1
    page_size: int = 10


class ErrorDetail(Schema):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class ErrorBody(Schema):
    error: ErrorDetail


class LatLon(Schema):
    lat: float
    lon: float


class Ok(Schema):
    ok: bool = True


class ImportResult(Schema):
    accepted: int
    rejected: list[dict[str, Any]]


ERROR_RESPONSES: dict[int | str, dict[str, Any]] = {
    400: {"model": ErrorBody}, 401: {"model": ErrorBody}, 403: {"model": ErrorBody},
    404: {"model": ErrorBody}, 409: {"model": ErrorBody}, 422: {"model": ErrorBody},
    429: {"model": ErrorBody},
}
