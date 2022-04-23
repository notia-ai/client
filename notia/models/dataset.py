from datetime import datetime
from typing import (
    Optional,
)
from pydantic import BaseModel, Field
from enum import Enum


class StatusEnum(str, Enum):
    pending = "pending"
    confirmed = "confirmed"


class DatasetMeta(BaseModel):
    slug: str
    name: str
    description: str
    size: int
    created_at: datetime
    price: int
    status: StatusEnum
    license_: str = Field(None, alias="license")


class Dataset:
    """A Dataset backed by an Arrow table."""

    def __init__(
        self,
        meta: Optional[DatasetMeta] = None,
    ):
        self._meta = meta
