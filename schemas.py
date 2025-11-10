"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

# Core user schema (for reference/examples)
class User(BaseModel):
    name: str = Field(..., description="Full name")
    email: EmailStr = Field(..., description="Email address")
    address: Optional[str] = Field(None, description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Sportswear products
    Collection name: "product"
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Category e.g., Tops, Bottoms, Footwear, Accessories")
    sport: str = Field(..., description="Primary sport e.g., Running, Yoga, Football")
    brand: Optional[str] = Field(None, description="Brand name")
    sizes: List[str] = Field(default_factory=list, description="Available sizes e.g., XS,S,M,L,XL or numeric for shoes")
    colors: List[str] = Field(default_factory=list, description="Available colors")
    image: Optional[str] = Field(None, description="Main image URL")
    in_stock: bool = Field(True, description="Whether product is in stock")
    stock: int = Field(0, ge=0, description="Units in stock")

class OrderItem(BaseModel):
    product_id: str = Field(..., description="Product ObjectId as string")
    quantity: int = Field(..., ge=1)
    size: Optional[str] = None
    color: Optional[str] = None

class CustomerInfo(BaseModel):
    name: str
    email: EmailStr
    address: str
    city: str
    country: str
    postal_code: str

class Order(BaseModel):
    """
    Orders
    Collection name: "order"
    """
    items: List[OrderItem]
    customer: CustomerInfo
    subtotal: float = Field(..., ge=0)
    shipping: float = Field(..., ge=0)
    total: float = Field(..., ge=0)
    status: str = Field(default="pending", description="pending, paid, shipped, delivered, cancelled")
    placed_at: Optional[datetime] = None
