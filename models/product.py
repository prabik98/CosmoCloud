from pydantic import BaseModel, Field, validator
from bson import ObjectId
from typing import List
from datetime import datetime

class Product(BaseModel):
    # id: str
    id: str = Field(..., description="Product ID")
    name: str
    price: float
    # available_quantity: int
    available_quantity: int = Field(..., description="New available quantity")

    # @validator("id", pre=True, always=True)
    # def validate_id(cls, v):
    #     if isinstance(v, ObjectId):
    #         return str(v)
    #     else:
    #         raise ValueError("Invalid ObjectId format")

    @validator("available_quantity", pre=True, always=True)
    def validate_available_quantity(cls, v):
        if not isinstance(v, int) or v < 0:
            raise ValueError("Invalid available_quantity value")
        return v

class OrderItem(BaseModel):
    product_id: str
    bought_quantity: int

    # @validator("product_id", pre=True, always=True)
    # def validate_product_id(cls, v):
    #     if isinstance(v, ObjectId):
    #         return str(v)
    #     else:
    #         raise ValueError("Invalid ObjectId format")

class UserAddress(BaseModel):
    city: str
    country: str
    zip_code: str

class Order(BaseModel):
    id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    items: List[OrderItem]
    total_amount: float
    user_address: UserAddress

    # @validator("items")
    # def validate_items(cls, value):
    #     for item in value:
    #         if not isinstance(item.product_id, ObjectId):
    #             raise ValueError("Invalid product_id in items")
    #     return value