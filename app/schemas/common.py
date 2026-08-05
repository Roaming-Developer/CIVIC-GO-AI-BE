from typing import Any

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str
    errors: list[dict[str, Any]] | None = None
