import re
from typing import List
import db_handler
import whatsapp_service
import message_formatter
from models import OrderItem, Order

def parse_order_message(message: str) -> List[OrderItem]:
    """
    Parse order message in format: 1x2, 3x1
    Returns list of OrderItem objects
    """
    items = []
    
    # Remove extra spaces and make lowercase
    message = message.strip().lower()
    
    # Pattern: number x number (e.g., 1x2, 3x1)
    pattern = r'(\d+)x(\d+)'
    matches = re.findall(pattern, message)
    
    for match in matches:
        item_id = int(match[0])
        quantity = int(match[1])
        items.append(OrderItem(menu_item_id=item_id, quantity=quantity))
    
    return items

def validate_order_items(items: List[OrderItem]) -> tuple[bool, str]:
    """
    Validate that all items exist and are available
    Returns (is_valid, error_message)
    """
    if not items:
        return False, "No valid items found"
    
    db = db_handler.get_db_session()
    try:
        menu = db_handler.read_menu(db)
        menu_dict = {item.id: item for item in menu}
        
        for order_item in items:
            menu_item = menu_dict.get(order_item.menu_item_id)
            
            if not menu_item:
                return False, f"Item #{order_item.menu_item_id} does not exist"
            
            if not menu_item.is_available:
                return False, f"{menu_item.name} is currently unavailable"
        
        return True, ""
    finally:
        db.close()

def calculate_order_total(items: List[OrderItem]) -> float:
    """Calculate total price for order items"""
    db = db_handler.get_db_session()
    try:
        menu = db_handler.read_menu(db)
        menu_dict = {item.id: item for item in menu}
        
        total = 0.0
        for order_item in items:
            menu_item = menu_dict.get(order_item.menu_item_id)
            if menu_item:
                total += menu_item.price * order_item.quantity
        
        return total
    finally:
        db.close()

def handle_incoming_message(phone_number: str, message_body: str):
    """
    Main conversation handler - processes incoming WhatsApp messages
    """
    # Normalize phone number
    if not phone_number.startswith('+'):
        phone_number = f'+{phone_number}'
    
    db = db_handler.get_db_session()
    try:
        # Get or create customer session
        session = db_handler.get_customer_session(db, phone_number)
        
        # Normalize message
        message = message_body.strip()
        message_upper = message.upper()
        
        # Handle HI/HELLO/START - Always go to main menu
        if message_upper in ['HI', 'HELLO', 'START', 'MENU']:
            session.state = "main_menu"
            db_handler.update_customer_session(db, phone_number, session)
            whatsapp_service.send_whatsapp_message(
                phone_number,
                message_formatter.format_main_menu()
            )
            return
        
        # Handle BACK - Always go to main menu
        if message_upper == 'BACK':
            session.state = "main_menu"
            db_handler.update_customer_session(db, phone_number, session)
            whatsapp_service.send_whatsapp_message(
                phone_number,
                message_formatter.format_main_menu()
            )
            return
        
        # State machine logic
        if session.state == "main_menu":
            handle_main_menu(db, phone_number, message, session)
        
        elif session.state == "viewing_menu":
            handle_viewing_menu(db, phone_number, message_upper, session)
        
        elif session.state == "placing_order":
            handle_placing_order(db, phone_number, message, session)
        
        elif session.state == "confirming_order":
            handle_confirming_order(db, phone_number, message_upper, session)
        
        elif session.state == "canceling_order":
            handle_canceling_order(db, phone_number, message_upper, session)
        
        else:
            # Unknown state - reset to main menu
            session.state = "main_menu"
            db_handler.update_customer_session(db, phone_number, session)
            whatsapp_service.send_whatsapp_message(
                phone_number,
                message_formatter.format_main_menu()
            )
    finally:
        db.close()

def handle_main_menu(db, phone_number: str, message: str, session):
    """Handle main menu selection"""
    
    if message == "1":
        # View Menu
        menu = db_handler.read_menu(db)
        session.state = "viewing_menu"
        db_handler.update_customer_session(db, phone_number, session)
        whatsapp_service.send_whatsapp_message(
            phone_number,
            message_formatter.format_menu(menu)
        )
    
    elif message == "2":
        # Place Order - Go directly to order instructions
        session.state = "placing_order"
        db_handler.update_customer_session(db, phone_number, session)
        
        # First show menu
        menu = db_handler.read_menu(db)
        whatsapp_service.send_whatsapp_message(
            phone_number,
            message_formatter.format_menu(menu)
        )
        
        # Then show order instructions
        whatsapp_service.send_whatsapp_message(
            phone_number,
            message_formatter.format_order_instructions()
        )
    
    elif message == "3":
        # Check Order Status
        orders = db_handler.get_customer_orders(db, phone_number)
        whatsapp_service.send_whatsapp_message(
            phone_number,
            message_formatter.format_order_status(orders)
        )
        # Stay in main menu state
    
    elif message == "4":
        # Cancel Order
        active_orders = db_handler.get_customer_active_orders(db, phone_number)
        
        if not active_orders:
            whatsapp_service.send_whatsapp_message(
                phone_number,
                message_formatter.format_cancel_confirmation(None)
            )
        else:
            # Get most recent active order
            most_recent = active_orders[-1]
            session.state = "canceling_order"
            session.cart = [OrderItem(menu_item_id=most_recent.id, quantity=1)]  # Store order ID temporarily
            db_handler.update_customer_session(db, phone_number, session)
            
            whatsapp_service.send_whatsapp_message(
                phone_number,
                message_formatter.format_cancel_confirmation(most_recent)
            )
    
    else:
        # Invalid option
        whatsapp_service.send_whatsapp_message(
            phone_number,
            message_formatter.format_error_message("invalid_option")
        )

def handle_viewing_menu(db, phone_number: str, message: str, session):
    """Handle viewing menu state"""
    
    if message == "ORDER":
        session.state = "placing_order"
        db_handler.update_customer_session(db, phone_number, session)
        whatsapp_service.send_whatsapp_message(
            phone_number,
            message_formatter.format_order_instructions()
        )
    
    else:
        # Invalid input while viewing menu
        whatsapp_service.send_whatsapp_message(
            phone_number,
            message_formatter.format_error_message("invalid_option")
        )

def handle_placing_order(db, phone_number: str, message: str, session):
    """Handle order placement"""
    
    # Parse order message
    items = parse_order_message(message)
    
    if not items:
        whatsapp_service.send_whatsapp_message(
            phone_number,
            message_formatter.format_error_message("invalid_order")
        )
        return
    
    # Validate items
    is_valid, error_msg = validate_order_items(items)
    
    if not is_valid:
        whatsapp_service.send_whatsapp_message(
            phone_number,
            message_formatter.format_error_message("item_unavailable")
        )
        return
    
    # Add to cart and show summary
    db_handler.add_to_cart(db, phone_number, items)
    session.state = "confirming_order"
    db_handler.update_customer_session(db, phone_number, session)
    
    whatsapp_service.send_whatsapp_message(
        phone_number,
        message_formatter.format_order_summary(items)
    )

def handle_confirming_order(db, phone_number: str, message: str, session):
    """Handle order confirmation"""
    
    if message == "CONFIRM":
        try:
            # Get fresh session data
            session = db_handler.get_customer_session(db, phone_number)
            
            if not session.cart:
                whatsapp_service.send_whatsapp_message(
                    phone_number,
                    "❌ Your cart is empty! Reply *HI* to start over."
                )
                return
            
            # Calculate total
            total = calculate_order_total(session.cart)
            
            # Create order
            order = Order(
                id=0,  # Will be set by add_order
                customer_whatsapp=phone_number,
                items=session.cart,
                status="pending",
                total_price=total,
                created_at=""  # Will be set by add_order
            )
            
            created_order = db_handler.add_order(db, order)
            
            # Send confirmation
            items_summary = message_formatter.format_items_summary(session.cart)
            whatsapp_service.send_order_confirmation(
                phone_number,
                created_order.id,
                items_summary,
                created_order.total_price
            )
            
            # Clear cart and reset state
            db_handler.clear_customer_cart(db, phone_number)
            session.state = "main_menu"
            db_handler.update_customer_session(db, phone_number, session)
            
        except Exception as e:
            print(f"❌ Error confirming order: {str(e)}")
            import traceback
            traceback.print_exc()
            whatsapp_service.send_whatsapp_message(
                phone_number,
                message_formatter.format_error_message("general")
            )
            return
    
    elif message == "CANCEL":
        # Cancel order creation
        db_handler.clear_customer_cart(db, phone_number)
        session.state = "main_menu"
        db_handler.update_customer_session(db, phone_number, session)
        
        whatsapp_service.send_whatsapp_message(
            phone_number,
            message_formatter.format_main_menu()
        )
    
    else:
        # Invalid input
        whatsapp_service.send_whatsapp_message(
            phone_number,
            message_formatter.format_error_message("invalid_option")
        )

def handle_canceling_order(db, phone_number: str, message: str, session):
    """Handle order cancellation"""
    
    if message == "YES":
        # Get order ID from cart (we stored it there temporarily)
        if session.cart and len(session.cart) > 0:
            order_id = session.cart[0].menu_item_id  # We stored order_id here
            
            # Cancel the order
            cancelled_order = db_handler.cancel_order(db, order_id)
            
            if cancelled_order:
                whatsapp_service.send_order_cancellation(phone_number, order_id)
        
        # Reset state
        session.cart = []
        session.state = "main_menu"
        db_handler.update_customer_session(db, phone_number, session)
    
    elif message == "NO":
        # Don't cancel - go back to main menu
        session.cart = []
        session.state = "main_menu"
        db_handler.update_customer_session(db, phone_number, session)
        
        whatsapp_service.send_whatsapp_message(
            phone_number,
            message_formatter.format_main_menu()
        )
    
    else:
        # Invalid input
        whatsapp_service.send_whatsapp_message(
            phone_number,
            message_formatter.format_error_message("invalid_option")
        )