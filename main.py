from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from sqlalchemy.orm import Session
import db_handler
import whatsapp_service
import conversation_handler
import message_formatter
from database import init_db, initialize_sample_data, get_db
from models import (
    MenuItem, MenuItemCreate, MenuItemUpdate,
    Order, OrderCreate, OrderStatusUpdate
)

app = FastAPI(
    title="Food Ordering System API",
    description="Backend for WhatsApp-based food ordering system with SQLite database",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins - for development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

# ==================== MENU ENDPOINTS ====================

@app.post("/menu/", response_model=MenuItem, tags=["Menu"])
def create_menu_item(item: MenuItemCreate, db: Session = Depends(get_db)):
    """
    Create a new menu item
    
    - **name**: Item name
    - **description**: Item description
    - **price**: Price in rupees
    - **is_available**: Availability status (default: true)
    """
    menu_item = MenuItem(id=0, **item.model_dump())
    created_item = db_handler.add_menu_item(db, menu_item)
    return created_item

@app.get("/menu/", response_model=List[MenuItem], tags=["Menu"])
def get_all_menu_items(db: Session = Depends(get_db)):
    """
    Retrieve all menu items
    """
    return db_handler.read_menu(db)

@app.get("/menu/{item_id}", response_model=MenuItem, tags=["Menu"])
def get_menu_item(item_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific menu item by ID
    """
    item = db_handler.get_menu_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return item

@app.patch("/menu/{item_id}", response_model=MenuItem, tags=["Menu"])
def update_menu_item(item_id: int, updates: MenuItemUpdate, db: Session = Depends(get_db)):
    """
    Update a menu item (e.g., change availability, price)
    """
    updated_item = db_handler.update_menu_item(
        db,
        item_id,
        updates.model_dump(exclude_unset=True)
    )
    if not updated_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return updated_item

# ==================== ORDER ENDPOINTS ====================

@app.post("/orders/", response_model=Order, tags=["Orders"])
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """
    Create a new order (staff-facing endpoint)
    
    This endpoint allows staff to manually create orders.
    For customer orders via WhatsApp, use the webhook endpoint.
    
    - **customer_whatsapp**: Customer's WhatsApp number (with country code)
    - **items**: List of items with quantities
    """
    # Validate items
    is_valid, error_msg = conversation_handler.validate_order_items(order.items)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Calculate total
    total = conversation_handler.calculate_order_total(order.items)
    
    # Create order
    new_order = Order(
        id=0,
        customer_whatsapp=order.customer_whatsapp,
        customer_name=order.customer_name,
        items=order.items,
        status="pending",
        total_price=total,
        created_at=""
    )
    
    created_order = db_handler.add_order(db, new_order)
    
    # Send WhatsApp confirmation
    items_summary = message_formatter.format_items_summary(order.items)
    whatsapp_service.send_order_confirmation(
        order.customer_whatsapp,
        created_order.id,
        items_summary,
        created_order.total_price
    )
    
    return created_order

@app.get("/orders/", response_model=List[Order], tags=["Orders"])
def get_all_orders(db: Session = Depends(get_db)):
    """
    Retrieve all orders
    """
    return db_handler.read_orders(db)

@app.get("/orders/{order_id}", response_model=Order, tags=["Orders"])
def get_order(order_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific order by ID
    """
    order = db_handler.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.patch("/orders/{order_id}", response_model=Order, tags=["Orders"])
def update_order_status(order_id: int, status_update: OrderStatusUpdate, db: Session = Depends(get_db)):
    """
    Update order status and send WhatsApp notification
    
    Allowed statuses:
    - pending
    - preparing
    - out-for-delivery
    - delivered
    - cancelled
    """
    allowed_statuses = ["pending", "preparing", "out-for-delivery", "delivered", "cancelled"]
    
    if status_update.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Allowed: {', '.join(allowed_statuses)}"
        )
    
    # Get order first
    order = db_handler.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Update status
    updated_order = db_handler.update_order_status(db, order_id, status_update.status)
    
    # Send WhatsApp notification
    whatsapp_service.send_order_status_update(
        order.customer_whatsapp,
        order_id,
        status_update.status
    )
    
    return updated_order

@app.delete("/orders/{order_id}", tags=["Orders"])
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    """
    Cancel an order and send WhatsApp notification
    """
    order = db_handler.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status in ["delivered", "cancelled"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel order with status: {order.status}"
        )
    
    # Cancel order
    cancelled_order = db_handler.cancel_order(db, order_id)
    
    # Send WhatsApp notification
    whatsapp_service.send_order_cancellation(order.customer_whatsapp, order_id)
    
    return {"message": f"Order #{order_id} cancelled successfully"}

# ==================== WHATSAPP WEBHOOK ====================

@app.post("/webhook/whatsapp", tags=["WhatsApp"])
async def whatsapp_webhook(request: Request):
    """
    Webhook endpoint for receiving WhatsApp messages from Twilio
    
    Twilio will POST to this endpoint when a customer sends a message
    """
    try:
        # Parse form data from Twilio
        form_data = await request.form()
        
        # Extract relevant fields
        from_number = form_data.get("From", "").replace("whatsapp:", "")
        message_body = form_data.get("Body", "")
        
        print(f"📨 Received message from {from_number}: {message_body}")
        
        # Process the message through conversation handler
        conversation_handler.handle_incoming_message(from_number, message_body)
        
        # Twilio expects a 200 OK response
        return JSONResponse(
            content={"status": "success"},
            status_code=200
        )
    
    except Exception as e:
        print(f"❌ Error processing webhook: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=500
        )

# ==================== HEALTH CHECK ====================

@app.get("/", tags=["Health"])
def root():
    """
    Health check endpoint
    """
    return {
        "status": "online",
        "service": "Food Ordering System API",
        "version": "2.0.0",
        "database": "SQLite"
    }

# ==================== STARTUP EVENT ====================

@app.on_event("startup")
def startup_event():
    """Initialize database on startup"""
    init_db()
    initialize_sample_data()
    print("✅ Food Ordering System API started successfully!")
    print("📝 Access API docs at: http://localhost:8000/docs")
    print("📋 OpenAPI spec at: http://localhost:8000/openapi.json")
    print("💾 Database: SQLite (food_ordering.db)")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)