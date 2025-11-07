import os
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Twilio credentials
ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER')

# Initialize Twilio client
client = Client(ACCOUNT_SID, AUTH_TOKEN)

def send_whatsapp_message(to_number: str, message_body: str) -> bool:
    """
    Send a WhatsApp message to a customer
    
    Args:
        to_number: Customer's WhatsApp number (must include country code, e.g., +919876543210)
        message_body: The message text to send
    
    Returns:
        bool: True if message sent successfully, False otherwise
    """
    try:
        # Ensure the number has the whatsapp: prefix
        if not to_number.startswith('whatsapp:'):
            to_number = f'whatsapp:{to_number}'
        
        message = client.messages.create(
            from_=TWILIO_WHATSAPP_NUMBER,
            body=message_body,
            to=to_number
        )
        
        print(f"✅ Message sent to {to_number} - SID: {message.sid}")
        return True
    
    except Exception as e:
        print(f"❌ Error sending message to {to_number}: {str(e)}")
        return False

def send_order_confirmation(to_number: str, order_id: int, items_summary: str, total_price: float):
    """Send order confirmation message"""
    message = f"""✅ *Order Confirmed!*

Order ID: #{order_id}
{items_summary}
Total: ₹{total_price}

Status: Pending
We'll notify you with updates!

Reply *HI* anytime to see the main menu."""
    
    return send_whatsapp_message(to_number, message)

def send_order_status_update(to_number: str, order_id: int, status: str):
    """Send order status update message"""
    status_messages = {
        "pending": "⏳ Your order is pending",
        "preparing": "👨‍🍳 Your order is being prepared",
        "out-for-delivery": "🚚 Your order is out for delivery!",
        "delivered": "✅ Your order has been delivered!",
        "cancelled": "❌ Your order has been cancelled"
    }
    
    message = f"""📦 *Order Update*

Order ID: #{order_id}
Status: {status_messages.get(status, status)}

Reply *3* to check all your orders."""
    
    return send_whatsapp_message(to_number, message)

def send_order_cancellation(to_number: str, order_id: int):
    """Send order cancellation confirmation"""
    message = f"""❌ *Order Cancelled*

Order ID: #{order_id}
Your order has been cancelled successfully.

Reply *HI* to place a new order."""
    
    return send_whatsapp_message(to_number, message)