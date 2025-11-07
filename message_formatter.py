from typing import List
from models import MenuItem, Order, OrderItem
import json_handler

def format_main_menu() -> str:
    """Format the main menu message"""
    return """🍕 *Welcome to Food Paradise!*

Please choose an option:
1️⃣ View Menu
2️⃣ Place Order
3️⃣ Check Order Status
4️⃣ Cancel Order

Reply with *1*, *2*, *3*, or *4*"""

def format_menu(menu_items: List[MenuItem]) -> str:
    """Format the menu display message"""
    message = "📋 *Our Menu:*\n\n"
    
    for item in menu_items:
        if item.is_available:
            status = "✅"
        else:
            status = "❌ Sold Out"
        
        message += f"{item.id}. *{item.name}* - ₹{item.price} {status}\n"
        message += f"   _{item.description}_\n\n"
    
    message += "\nReply *ORDER* to place an order"
    message += "\nReply *BACK* for main menu"
    
    return message

def format_order_instructions() -> str:
    """Format order placement instructions"""
    return """🛒 *Ready to Order!*

Send me item numbers and quantities like this:
*1x2, 3x1*
(2 Pizzas and 1 Coke)

Example formats:
• 1x2 (2 of item 1)
• 1x1, 3x2 (1 of item 1, 2 of item 3)
• 2x1, 4x1, 3x2 (multiple items)

Reply *BACK* to return to menu"""

def format_order_summary(cart_items: List[OrderItem]) -> str:
    """Format order summary for confirmation"""
    message = "🛒 *Order Summary:*\n\n"
    total = 0.0
    
    menu = json_handler.read_menu()
    menu_dict = {item.id: item for item in menu}
    
    for cart_item in cart_items:
        menu_item = menu_dict.get(cart_item.menu_item_id)
        if menu_item:
            item_total = menu_item.price * cart_item.quantity
            total += item_total
            message += f"• {cart_item.quantity}x *{menu_item.name}* - ₹{item_total}\n"
    
    message += f"\n💰 *Total: ₹{total}*\n"
    message += "\nReply *CONFIRM* to place order"
    message += "\nReply *CANCEL* to start over"
    
    return message

def format_order_status(orders: List[Order]) -> str:
    """Format order status message"""
    if not orders:
        return """📦 *Your Orders*

You have no orders yet.

Reply *2* to place a new order!"""
    
    active_orders = [o for o in orders if o.status not in ["delivered", "cancelled"]]
    past_orders = [o for o in orders if o.status in ["delivered", "cancelled"]]
    
    message = "📦 *Your Orders*\n\n"
    
    if active_orders:
        message += "🟢 *Active Orders:*\n"
        for order in active_orders[-5:]:  # Show last 5 active orders
            status_emoji = {
                "pending": "⏳",
                "preparing": "👨‍🍳",
                "out-for-delivery": "🚚"
            }.get(order.status, "📦")
            
            message += f"{status_emoji} #{order.id} - {order.status.replace('-', ' ').title()} - ₹{order.total_price}\n"
        message += "\n"
    
    if past_orders:
        message += "📜 *Past Orders:*\n"
        for order in past_orders[-3:]:  # Show last 3 past orders
            status_emoji = "✅" if order.status == "delivered" else "❌"
            message += f"{status_emoji} #{order.id} - {order.status.title()} - ₹{order.total_price}\n"
    
    message += "\nReply *BACK* for main menu"
    
    return message

def format_cancel_confirmation(order: Order) -> str:
    """Format order cancellation confirmation request"""
    if not order:
        return """❌ *No Active Orders*

You have no active orders to cancel.

Reply *BACK* for main menu"""
    
    message = f"""⚠️ *Cancel Order?*

Order ID: #{order.id}
Status: {order.status.replace('-', ' ').title()}
Total: ₹{order.total_price}

Items:
"""
    
    menu = json_handler.read_menu()
    menu_dict = {item.id: item for item in menu}
    
    for order_item in order.items:
        menu_item = menu_dict.get(order_item.menu_item_id)
        if menu_item:
            message += f"• {order_item.quantity}x {menu_item.name}\n"
    
    message += "\nReply *YES* to cancel this order"
    message += "\nReply *NO* to keep it"
    
    return message

def format_error_message(error_type: str = "general") -> str:
    """Format error messages"""
    errors = {
        "invalid_option": """❌ *Invalid Option*

Please reply with *1*, *2*, *3*, or *4*

Or reply *HI* to see the main menu""",
        
        "invalid_order": """❌ *Invalid Order Format*

Please send items like: *1x2, 3x1*

Example: 1x2 (2 of item 1)

Reply *BACK* to return""",
        
        "item_unavailable": """❌ *Item Unavailable*

Some items you selected are not available.
Please check the menu and try again.

Reply *1* to view menu""",
        
        "general": """❌ *Oops!*

Something went wrong. Please try again.

Reply *HI* for main menu"""
    }
    
    return errors.get(error_type, errors["general"])

def format_items_summary(items: List[OrderItem]) -> str:
    """Format items for order confirmation"""
    menu = json_handler.read_menu()
    menu_dict = {item.id: item for item in menu}
    
    summary = ""
    for order_item in items:
        menu_item = menu_dict.get(order_item.menu_item_id)
        if menu_item:
            summary += f"• {order_item.quantity}x {menu_item.name}\n"
    
    return summary.strip()