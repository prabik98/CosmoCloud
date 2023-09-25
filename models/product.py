from pydantic import BaseModel, Field, validator
from bson import ObjectId
from typing import List, Optional
from datetime import datetime

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class Product(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    price: float
    available_quantity: int = Field(..., description="New available quantity")

    @validator("available_quantity", pre=True, always=True)
    def validate_available_quantity(cls, v):
        if not isinstance(v, int) or v < 0:
            raise ValueError("Invalid available_quantity value")
        return v
    class Config:
        json_encoders = {ObjectId: str}

class UpdateProduct(BaseModel):
    name: Optional[str]
    price: Optional[float]
    available_quantity: Optional[int] = Field(..., description="New available quantity")

    @validator("available_quantity", pre=True, always=True)
    def validate_available_quantity(cls, v):
        if not isinstance(v, int) or v < 0:
            raise ValueError("Invalid available_quantity value")
        return v
    class Config:
        json_encoders = {ObjectId: str}

class OrderItem(BaseModel):
    product_id: str
    bought_quantity: int

    @validator("bought_quantity", pre=True, always=True)
    def validate_bought_quantity(cls, v):
        if not isinstance(v, int) or v <= 0:
            raise ValueError("Invalid available_quantity value")
        return v

class UserAddress(BaseModel):
    city: str
    country: str
    zip_code: str

class Order(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    items: List[OrderItem]
    total_amount: Optional[float]
    user_address: UserAddress
    class Config:
        json_encoders = {ObjectId: str}