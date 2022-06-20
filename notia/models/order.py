from datetime import datetime
from typing import (
    Optional,
)
from pydantic import BaseModel


class Order(BaseModel):
    display_id: str
    order_timestamp: datetime
    purchase_price: Optional[int]
    purchase_name: str
    purchase_size: int
    purchase_description: str
    download_token: str
    seller_name: str
    dataset_slug: str
