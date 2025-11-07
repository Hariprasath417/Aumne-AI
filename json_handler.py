import json
import os
from typing import List, Dict, Any, Optional
from models import MenuItem, Order, CustomerSession, OrderItem
from datetime import datetime

# File paths
MENU_FILE = "menu.json"
ORDERS_FILE = "orders.json"
SESSIONS_FILE = "customer_sessions.json"

# Initialize JSON files if they don't exist
def initialize_files():
    """Create JSON files with default data if they don't exist"""
    if not os.path.exists(MENU_FILE):
        default_menu = [
            {"id": 1, "name": "Margherita Pizza", "description": "Classic cheese pizza", "price": 299.0, "is_available": True},
            {"id": 2, "name": "Pepperoni Pizza", "description": "Spicy pepperoni pizza", "price": 349.0, "is_available": True},
            {"id": 3, "name": "Coke", "description": "Cold beverage", "price": 50.0, "is_available": True},
            {"id": 4, "name": "Garlic Bread", "description": "Crispy garlic bread", "price": 99.0, "is_available": True}
        ]
        with open(MENU_FILE, 'w') as f:
            json.dump(default_menu, f, indent=2)
    
    if not os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'w') as f:
            json.dump([], f, indent=2)
    
    if not os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, 'w') as f:
            json.dump({}, f, indent=2)

# Menu operations
def read_menu() -> List[MenuItem]:
    """Read all menu items"""
    with open(MENU_FILE, 'r') as f:
        data = json.load(f)
    return [MenuItem(**item) for item in data]

def write_menu(menu_items: List[MenuItem]):
    """Write menu items to file"""
    with open(MENU_FILE, 'w') as f:
        json.dump([item.model_dump() for item in menu_items], f, indent=2)

def get_menu_item(item_id: int) -> Optional[MenuItem]:
    """Get a specific menu item by ID"""
    menu = read_menu()
    for item in menu:
        if item.id == item_id:
            return item
    return None

def add_menu_item(item: MenuItem) -> MenuItem:
    """Add a new menu item"""
    menu = read_menu()
    # Generate new ID
    item.id = max([m.id for m in menu], default=0) + 1
    menu.append(item)
    write_menu(menu)
    return item

def update_menu_item(item_id: int, updates: Dict[str, Any]) -> Optional[MenuItem]:
    """Update a menu item"""
    menu = read_menu()
    for i, item in enumerate(menu):
        if item.id == item_id:
            updated_data = item.model_dump()
            updated_data.update({k: v for k, v in updates.items() if v is not None})
            menu[i] = MenuItem(**updated_data)
            write_menu(menu)
            return menu[i]
    return None

# Order operations
def read_orders() -> List[Order]:
    """Read all orders"""
    with open(ORDERS_FILE, 'r') as f:
        data = json.load(f)
    return [Order(**order) for order in data]

def write_orders(orders: List[Order]):
    """Write orders to file"""
    with open(ORDERS_FILE, 'w') as f:
        json.dump([order.model_dump() for order in orders], f, indent=2)

def get_order(order_id: int) -> Optional[Order]:
    """Get a specific order by ID"""
    orders = read_orders()
    for order in orders:
        if order.id == order_id:
            return order
    return None

def add_order(order: Order) -> Order:
    """Add a new order"""
    orders = read_orders()
    # Generate new ID
    order.id = max([o.id for o in orders], default=0) + 1
    order.created_at = datetime.now().isoformat()
    orders.append(order)
    write_orders(orders)
    return order

def update_order_status(order_id: int, status: str) -> Optional[Order]:
    """Update order status"""
    orders = read_orders()
    for i, order in enumerate(orders):
        if order.id == order_id:
            orders[i].status = status
            write_orders(orders)
            return orders[i]
    return None

def cancel_order(order_id: int) -> Optional[Order]:
    """Cancel an order"""
    return update_order_status(order_id, "cancelled")

def get_customer_orders(whatsapp_number: str) -> List[Order]:
    """Get all orders for a customer"""
    orders = read_orders()
    return [order for order in orders if order.customer_whatsapp == whatsapp_number]

def get_customer_active_orders(whatsapp_number: str) -> List[Order]:
    """Get active orders for a customer (not delivered or cancelled)"""
    orders = get_customer_orders(whatsapp_number)
    return [order for order in orders if order.status not in ["delivered", "cancelled"]]

# Customer session operations
def read_sessions() -> Dict[str, CustomerSession]:
    """Read all customer sessions"""
    with open(SESSIONS_FILE, 'r') as f:
        data = json.load(f)
    return {phone: CustomerSession(**session) for phone, session in data.items()}

def write_sessions(sessions: Dict[str, CustomerSession]):
    """Write sessions to file"""
    with open(SESSIONS_FILE, 'w') as f:
        json.dump({phone: session.model_dump() for phone, session in sessions.items()}, f, indent=2)

def get_customer_session(whatsapp_number: str) -> CustomerSession:
    """Get or create customer session"""
    sessions = read_sessions()
    if whatsapp_number not in sessions:
        sessions[whatsapp_number] = CustomerSession(
            last_interaction=datetime.now().isoformat()
        )
        write_sessions(sessions)
    return sessions[whatsapp_number]

def update_customer_session(whatsapp_number: str, session: CustomerSession):
    """Update customer session"""
    sessions = read_sessions()
    session.last_interaction = datetime.now().isoformat()
    sessions[whatsapp_number] = session
    write_sessions(sessions)

def clear_customer_cart(whatsapp_number: str):
    """Clear customer's cart"""
    session = get_customer_session(whatsapp_number)
    session.cart = []
    update_customer_session(whatsapp_number, session)

def add_to_cart(whatsapp_number: str, items: List[OrderItem]):
    """Add items to customer's cart"""
    session = get_customer_session(whatsapp_number)
    session.cart = items
    update_customer_session(whatsapp_number, session)

# Initialize files on import
initialize_files()