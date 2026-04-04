from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


# ─── Enums ───────────────────────────────────────────────────────────────────

class UserRole(str, Enum):
    admin = "admin"
    client = "client"


class OrderStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


# ─── Schemas ──────────────────────────────────────────────────────────────────

class UserBase(BaseModel):
    email: str
    name: str


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None


class User(UserBase):
    id: int
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    image_url: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    price: float = Field(ge=0)
    compare_price: Optional[float] = None
    image_url: Optional[str] = None
    images: list[str] = []
    sizes: list[str] = []
    category_id: Optional[int] = None
    team: Optional[str] = None
    league: Optional[str] = None
    year: Optional[str] = None
    type: Optional[str] = None  # home, away, third, retro
    stock: int = 0
    featured: bool = False
    active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    compare_price: Optional[float] = None
    image_url: Optional[str] = None
    images: Optional[list[str]] = None
    sizes: Optional[list[str]] = None
    category_id: Optional[int] = None
    team: Optional[str] = None
    league: Optional[str] = None
    year: Optional[str] = None
    type: Optional[str] = None
    stock: Optional[int] = None
    featured: Optional[bool] = None
    active: Optional[bool] = None


class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CartItemBase(BaseModel):
    product_id: int
    size: str
    quantity: int = Field(ge=1)


class CartItem(CartItemBase):
    id: int
    user_id: int
    created_at: datetime


class CartItemCreate(CartItemBase):
    pass


class OrderItemBase(BaseModel):
    product_id: int
    size: str
    quantity: int
    unit_price: float


class OrderItem(OrderItemBase):
    id: int
    order_id: int

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    status: OrderStatus = OrderStatus.pending
    total: float
    shipping_address: Optional[str] = None
    shipping_city: Optional[str] = None
    shipping_state: Optional[str] = None
    shipping_zip: Optional[str] = None
    customer_name: str
    customer_email: str
    customer_phone: str
    pagarme_payment_id: Optional[str] = None
    pagarme_qr_code: Optional[str] = None
    pagarme_qr_code_url: Optional[str] = None


class OrderCreate(BaseModel):
    items: list[OrderItemBase]
    shipping_address: str
    shipping_city: str
    shipping_state: str
    shipping_zip: str
    customer_name: str
    customer_email: str
    customer_phone: str


class Order(OrderBase):
    id: int
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    items: list[OrderItem] = []

    class Config:
        from_attributes = True


# ─── Pagination ───────────────────────────────────────────────────────────────

class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    per_page: int
    pages: int