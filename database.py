from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Create SQLite database
SQLALCHEMY_DATABASE_URL = "sqlite:///./food_ordering.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Database Models

class MenuItemDB(Base):
    __tablename__ = "menu_items"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    is_available = Column(Boolean, default=True)

class OrderDB(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_name = Column(String, nullable=True)
    customer_whatsapp = Column(String, nullable=False, index=True)
    status = Column(String, default="pending")  # pending, preparing, out-for-delivery, delivered, cancelled
    total_price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationship
    items = relationship("OrderItemDB", back_populates="order", cascade="all, delete-orphan")

class OrderItemDB(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    menu_item_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    
    # Relationship
    order = relationship("OrderDB", back_populates="items")

class CustomerSessionDB(Base):
    __tablename__ = "customer_sessions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    whatsapp_number = Column(String, unique=True, nullable=False, index=True)
    state = Column(String, default="main_menu")
    cart = Column(Text, default="[]")  # Store as JSON string
    last_interaction = Column(DateTime, default=datetime.now)
    customer_name = Column(String, nullable=True)
    order_history = Column(Text, default="[]")  # Store as JSON string

# Create all tables
def init_db():
    """Initialize database and create tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

# Dependency to get database session
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize sample data
def initialize_sample_data():
    """Add sample menu items and orders"""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_menu = db.query(MenuItemDB).first()
        if existing_menu:
            print("✅ Sample data already exists")
            return
        
        # Add sample menu items
        menu_items = [
            MenuItemDB(name="Margherita Pizza", description="Classic cheese pizza", price=299.0, is_available=True),
            MenuItemDB(name="Pepperoni Pizza", description="Spicy pepperoni pizza", price=349.0, is_available=True),
            MenuItemDB(name="Coke", description="Cold beverage", price=50.0, is_available=True),
            MenuItemDB(name="Garlic Bread", description="Crispy garlic bread", price=99.0, is_available=True)
        ]
        
        for item in menu_items:
            db.add(item)
        
        db.commit()
        
        # Add sample orders
        sample_orders = [
            {
                "customer_name": "Rajesh Kumar",
                "customer_whatsapp": "+919876543210",
                "status": "delivered",
                "total_price": 648.0,
                "items": [{"menu_item_id": 1, "quantity": 2}, {"menu_item_id": 3, "quantity": 1}]
            },
            {
                "customer_name": "Priya Sharma",
                "customer_whatsapp": "+919123456789",
                "status": "out-for-delivery",
                "total_price": 647.0,
                "items": [{"menu_item_id": 2, "quantity": 1}, {"menu_item_id": 4, "quantity": 2}, {"menu_item_id": 3, "quantity": 2}]
            },
            {
                "customer_name": "Amit Patel",
                "customer_whatsapp": "+919988776655",
                "status": "preparing",
                "total_price": 1047.0,
                "items": [{"menu_item_id": 1, "quantity": 3}, {"menu_item_id": 3, "quantity": 3}]
            },
            {
                "customer_name": "Sneha Reddy",
                "customer_whatsapp": "+919445566778",
                "status": "pending",
                "total_price": 596.0,
                "items": [{"menu_item_id": 4, "quantity": 4}, {"menu_item_id": 3, "quantity": 4}]
            }
        ]
        
        for order_data in sample_orders:
            items = order_data.pop("items")
            order = OrderDB(**order_data)
            db.add(order)
            db.flush()  # Get order ID
            
            for item_data in items:
                order_item = OrderItemDB(order_id=order.id, **item_data)
                db.add(order_item)
        
        db.commit()
        print("✅ Sample data initialized successfully!")
        
    except Exception as e:
        print(f"❌ Error initializing sample data: {e}")
        db.rollback()
    finally:
        db.close()