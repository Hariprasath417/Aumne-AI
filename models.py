from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# Menu Item Models
class MenuItem(BaseModel):
    id: int
    name: str
    description: str
    price: float
    is_available: bool = True

class MenuItemCreate(BaseModel):
    name: str
    description: str
    price: float
    is_available: bool = True

class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    is_available: Optional[bool] = None

# Order Models
class OrderItem(BaseModel):
    menu_item_id: int
    quantity: int

class Order(BaseModel):
    id: int
    customer_name: Optional[str] = None
    customer_whatsapp: str
    items: List[OrderItem]
    status: str = "pending"  # pending, preparing, out-for-delivery, delivered, cancelled
    total_price: float
    created_at: str

class OrderCreate(BaseModel):
    customer_name: Optional[str] = None
    customer_whatsapp: str
    items: List[OrderItem]

class OrderStatusUpdate(BaseModel):
    status: str

# Customer Session Models
class CustomerSession(BaseModel):
    state: str = "main_menu"
    cart: List[OrderItem] = []
    last_interaction: str
    customer_name: Optional[str] = None
    order_history: List[int] = []