import datetime
from pydantic import BaseModel, Field
from .order_status import Status
import uuid
from .type import Type

class Order(BaseModel):
    order_pk: str = Field(default_factory=lambda: f"ORDER#{uuid.uuid4()}")
    order_sk: str = Field(default='#METADATA')
    order_total_price: float = 0
    order_status: Status = Field(default=Status.PENDING)
    created_at: datetime.datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime.datetime = Field(default_factory=datetime.utcnow)
    type: Type = Field(default=Type.ORDER)

    def to_dynamodb_item(self) -> dict:
        return {
            "PK": self.order_pk,
            "SK": self.order_sk,
            "order_total_price": self.order_total_price,
            "order_status": self.order_status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "type": self.type.value,
        }