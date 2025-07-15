from typing import Optional, Annotated
from pydantic import BaseModel, BeforeValidator

def validate_price(value) -> float:
    if not isinstance(value, (int, float)):
        raise ValueError('Price must be a number')
    if value != round(value, 2):
        raise ValueError('Price has to be to two decimal points')
    if value < 0:
        raise ValueError('Price cannot be negative')
    return value

def validate_name(value) -> str:
    if not isinstance(value, str):
        raise ValueError('Name must be of type string')
    value =  value.strip()
    if not value:
        raise ValueError('Name field must not be empty')
    return value

NameStr = Annotated[str, BeforeValidator(validate_name)]
PriceFloat = Annotated[float, BeforeValidator(validate_price)]

class Item(BaseModel):
    name: NameStr
    price: PriceFloat
    description: Optional[str] = None

class Category(BaseModel):
    name: NameStr
