import json
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from database import MenuItemDB, OrderDB, OrderItemDB, CustomerSessionDB, SessionLocal
from models import MenuItem, Order, OrderItem, CustomerSession

# ==================== MENU OPERATIONS ====================

def read_menu(db: Session) -> List[MenuItem]:
    """Read all menu items"""
    items = db.query(MenuItemDB).all()
    return [MenuItem(
        id=item.id,
        name=item.name,
        description=item.description,
        price=item.price,
        is_available=item.is_available
    ) for item in items]

def get_menu_item(db: Session, item_id: int) -> Optional[MenuItem]:
    """Get a specific menu item by ID"""
    item = db.query(MenuItemDB).filter(MenuItemDB.id == item_id).first()
    if item:
        return MenuItem(
            id=item.id,
            name=item.name,
            description=item.description,
            price=item.price,
            is_available=item.is_available
        )
    return None

def add_menu_item(db: Session, item: MenuItem) -> MenuItem:
    """Add a new menu item"""
    db_item = MenuItemDB(
        name=item.name,
        description=item.description,
        price=item.price,
        is_available=item.is_available
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    
    return MenuItem(
        id=db_item.id,
        name=db_item.name,
        description=db_item.description,
        price=db_item.price,
        is_available=db_item.is_available
    )

def update_menu_item(db: Session, item_id: int, updates: dict) -> Optional[MenuItem]:
    """Update a menu item"""
    db_item = db.query(MenuItemDB).filter(MenuItemDB.id == item_id).first()
    if not db_item:
        return None
    
    for key, value in updates.items():
        if value is not None:
            setattr(db_item, key, value)
    
    db.commit()
    db.refresh(db_item)
    
    return MenuItem(
        id=db_item.id,
        name=db_item.name,
        description=db_item.description,
        price=db_item.price,
        is_available=db_item.is_available
    )

# ==================== ORDER OPERATIONS ====================

def read_orders(db: Session) -> List[Order]:
    """Read all orders"""
    orders = db.query(OrderDB).all()
    return [_convert_order_db_to_model(order) for order in orders]

def get_order(db: Session, order_id: int) -> Optional[Order]:
    """Get a specific order by ID"""
    order = db.query(OrderDB).filter(OrderDB.id == order_id).first()
    if order:
        return _convert_order_db_to_model(order)
    return None

def add_order(db: Session, order: Order) -> Order:
    """Add a new order"""
    db_order = OrderDB(
        customer_name=order.customer_name,
        customer_whatsapp=order.customer_whatsapp,
        status=order.status,
        total_price=order.total_price,
        created_at=datetime.now()
    )
    db.add(db_order)
    db.flush()  # Get order ID before adding items
    
    # Add order items
    for item in order.items:
        db_order_item = OrderItemDB(
            order_id=db_order.id,
            menu_item_id=item.menu_item_id,
            quantity=item.quantity
        )
        db.add(db_order_item)
    
    db.commit()
    db.refresh(db_order)
    
    return _convert_order_db_to_model(db_order)

def update_order_status(db: Session, order_id: int, status: str) -> Optional[Order]:
    """Update order status"""
    db_order = db.query(OrderDB).filter(OrderDB.id == order_id).first()
    if not db_order:
        return None
    
    db_order.status = status
    db.commit()
    db.refresh(db_order)
    
    return _convert_order_db_to_model(db_order)

def cancel_order(db: Session, order_id: int) -> Optional[Order]:
    """Cancel an order"""
    return update_order_status(db, order_id, "cancelled")

def get_customer_orders(db: Session, whatsapp_number: str) -> List[Order]:
    """Get all orders for a customer"""
    orders = db.query(OrderDB).filter(OrderDB.customer_whatsapp == whatsapp_number).all()
    return [_convert_order_db_to_model(order) for order in orders]

def get_customer_active_orders(db: Session, whatsapp_number: str) -> List[Order]:
    """Get active orders for a customer (not delivered or cancelled)"""
    orders = db.query(OrderDB).filter(
        OrderDB.customer_whatsapp == whatsapp_number,
        OrderDB.status.notin_(["delivered", "cancelled"])
    ).all()
    return [_convert_order_db_to_model(order) for order in orders]

def _convert_order_db_to_model(db_order: OrderDB) -> Order:
    """Convert database order to Pydantic model"""
    return Order(
        id=db_order.id,
        customer_name=db_order.customer_name,
        customer_whatsapp=db_order.customer_whatsapp,
        items=[
            OrderItem(menu_item_id=item.menu_item_id, quantity=item.quantity)
            for item in db_order.items
        ],
        status=db_order.status,
        total_price=db_order.total_price,
        created_at=db_order.created_at.isoformat()
    )

# ==================== CUSTOMER SESSION OPERATIONS ====================

def get_customer_session(db: Session, whatsapp_number: str) -> CustomerSession:
    """Get or create customer session"""
    db_session = db.query(CustomerSessionDB).filter(
        CustomerSessionDB.whatsapp_number == whatsapp_number
    ).first()
    
    if not db_session:
        db_session = CustomerSessionDB(
            whatsapp_number=whatsapp_number,
            state="main_menu",
            cart="[]",
            last_interaction=datetime.now(),
            order_history="[]"
        )
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
    
    return CustomerSession(
        state=db_session.state,
        cart=[OrderItem(**item) for item in json.loads(db_session.cart)],
        last_interaction=db_session.last_interaction.isoformat(),
        customer_name=db_session.customer_name,
        order_history=json.loads(db_session.order_history)
    )

def update_customer_session(db: Session, whatsapp_number: str, session: CustomerSession):
    """Update customer session"""
    db_session = db.query(CustomerSessionDB).filter(
        CustomerSessionDB.whatsapp_number == whatsapp_number
    ).first()
    
    if not db_session:
        db_session = CustomerSessionDB(whatsapp_number=whatsapp_number)
        db.add(db_session)
    
    db_session.state = session.state
    db_session.cart = json.dumps([item.model_dump() for item in session.cart])
    db_session.last_interaction = datetime.now()
    db_session.customer_name = session.customer_name
    db_session.order_history = json.dumps(session.order_history)
    
    db.commit()

def clear_customer_cart(db: Session, whatsapp_number: str):
    """Clear customer's cart"""
    session = get_customer_session(db, whatsapp_number)
    session.cart = []
    update_customer_session(db, whatsapp_number, session)

def add_to_cart(db: Session, whatsapp_number: str, items: List[OrderItem]):
    """Add items to customer's cart"""
    session = get_customer_session(db, whatsapp_number)
    session.cart = items
    update_customer_session(db, whatsapp_number, session)

# Helper function to get db session
def get_db_session():
    """Get a new database session"""
    return SessionLocal()