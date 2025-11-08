@echo off
REM ============================================
REM Python SDK Generation Script
REM ============================================

echo.
echo === Generating Python SDK from OpenAPI Spec ===
echo.

REM Activate virtual environment
if not exist venv (
    echo [ERROR] Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)
call venv\Scripts\activate.bat

REM Check if backend is running
echo Checking if FastAPI backend is running...
curl -s http://localhost:8000/openapi.json >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Backend is not running. Please start it first with run.bat
    echo.
    echo Alternative: Start backend manually:
    echo   venv\Scripts\activate
    echo   python -m uvicorn main:app --reload
    pause
    exit /b 1
)
echo [OK] Backend is accessible
echo.

REM Download OpenAPI spec
echo Downloading OpenAPI specification...
curl -s http://localhost:8000/openapi.json -o openapi.json
if %errorlevel% neq 0 (
    echo [ERROR] Failed to download OpenAPI spec
    pause
    exit /b 1
)
echo [OK] OpenAPI spec saved to openapi.json
echo.

REM Remove old SDK if exists
if exist whatsapp_food_sdk (
    echo Removing old SDK...
    rmdir /s /q whatsapp_food_sdk
)

REM Generate Python SDK
echo Generating Python SDK...
call npx @openapitools/openapi-generator-cli generate -i openapi.json -g python -o whatsapp_food_sdk --additional-properties=packageName=whatsapp_food_sdk,projectName=whatsapp-food-sdk,packageVersion=1.0.0

if not exist whatsapp_food_sdk (
    echo [ERROR] SDK generation failed
    pause
    exit /b 1
)
echo [OK] SDK generated successfully
echo.

REM Install the SDK
echo Installing generated SDK...
cd whatsapp_food_sdk
pip install -e . --quiet
cd ..
echo [OK] SDK installed
echo.

REM Create example usage script
echo Creating SDK example script...
(
    echo """
    echo WhatsApp Food Ordering SDK - Example Usage
    echo """
    echo from whatsapp_food_sdk import ApiClient, Configuration
    echo from whatsapp_food_sdk.api import default_api
    echo import json
    echo.
    echo # Configure API client
    echo config = Configuration^(^)
    echo config.host = "http://localhost:8000"
    echo client = ApiClient^(configuration=config^)
    echo api = default_api.DefaultApi^(client^)
    echo.
    echo def main^(^):
    echo     print^("=== WhatsApp Food Ordering SDK Examples ===\n"^)
    echo.    
    echo     # Example 1: Add a menu item
    echo     print^("1. Adding a new menu item..."^)
    echo     try:
    echo         menu_item = {
    echo             "id": "item_001",
    echo             "name": "Margherita Pizza",
    echo             "description": "Classic pizza with tomato sauce and mozzarella",
    echo             "price": 12.99,
    echo             "category": "Pizza",
    echo             "available": True,
    echo             "image_url": "https://example.com/pizza.jpg"
    echo         }
    echo         # Note: Adjust method names based on your actual API endpoints
    echo         # response = api.add_menu_item^(menu_item^)
    echo         # print^(f"✓ Menu item added: {response}"^)
    echo         print^("  ^(Uncomment and adjust method name based on your API^)"^)
    echo     except Exception as e:
    echo         print^(f"✗ Error: {e}"^)
    echo.    
    echo     print^(^)
    echo.    
    echo     # Example 2: Place an order
    echo     print^("2. Placing a food order..."^)
    echo     try:
    echo         order = {
    echo             "customer_id": "customer_123",
    echo             "items": [
    echo                 {"menu_item_id": "item_001", "quantity": 2}
    echo             ],
    echo             "delivery_address": "123 Main St",
    echo             "phone_number": "+1234567890"
    echo         }
    echo         # response = api.place_order^(order^)
    echo         # print^(f"✓ Order placed: {response}"^)
    echo         print^("  ^(Uncomment and adjust method name based on your API^)"^)
    echo     except Exception as e:
    echo         print^(f"✗ Error: {e}"^)
    echo.    
    echo     print^(^)
    echo.    
    echo     # Example 3: List all orders
    echo     print^("3. Retrieving all orders..."^)
    echo     try:
    echo         # orders = api.list_orders^(^)
    echo         # print^(f"✓ Found {len^(orders^)} orders"^)
    echo         # for order in orders:
    echo         #     print^(f"  - Order ID: {order.id}, Status: {order.status}"^)
    echo         print^("  ^(Uncomment and adjust method name based on your API^)"^)
    echo     except Exception as e:
    echo         print^(f"✗ Error: {e}"^)
    echo.
    echo if __name__ == "__main__":
    echo     main^(^)
) > sdk_example.py
echo [OK] Example script created: sdk_example.py
echo.

REM Create SDK documentation
echo Creating SDK documentation...
(
    echo # WhatsApp Food Ordering System - Python SDK
    echo.
    echo ## Installation
    echo.
    echo The SDK has been automatically installed in your virtual environment.
    echo.
    echo ## Configuration
    echo.
    echo ```python
    echo from whatsapp_food_sdk import ApiClient, Configuration
    echo.
    echo config = Configuration^(^)
    echo config.host = "http://localhost:8000"
    echo client = ApiClient^(configuration=config^)
    echo ```
    echo.
    echo ## Available Methods
    echo.
    echo Based on your FastAPI application, the SDK should support:
    echo.
    echo ### Menu Management
    echo - **add_menu_item^(^)** - Add a new menu item
    echo - **list_menu_items^(^)** - Get all menu items
    echo - **get_menu_item^(item_id^)** - Get specific menu item
    echo - **update_menu_item^(item_id, data^)** - Update menu item
    echo - **delete_menu_item^(item_id^)** - Delete menu item
    echo.
    echo ### Order Management
    echo - **place_order^(order_data^)** - Place a new order
    echo - **list_orders^(^)** - Get all orders
    echo - **get_order_by_id^(order_id^)** - Get specific order
    echo - **update_order_status^(order_id, status^)** - Update order status
    echo.
    echo ## Usage Example
    echo.
    echo See **sdk_example.py** for detailed usage examples.
    echo.
    echo Run the example:
    echo ```bash
    echo python sdk_example.py
    echo ```
    echo.
    echo ## API Documentation
    echo.
    echo For complete API documentation, visit:
    echo - Interactive Docs: http://localhost:8000/docs
    echo - OpenAPI Spec: http://localhost:8000/openapi.json
) > SDK_README.md
echo [OK] SDK documentation created: SDK_README.md
echo.

REM Summary
echo === SDK Generation Complete ===
echo.
echo Generated files:
echo - whatsapp_food_sdk/  ^(SDK package^)
echo - openapi.json        ^(OpenAPI specification^)
echo - sdk_example.py      ^(Usage examples^)
echo - SDK_README.md       ^(Documentation^)
echo.
echo Next steps:
echo 1. Review SDK_README.md for usage instructions
echo 2. Run 'python sdk_example.py' to test the SDK
echo 3. Import and use the SDK in your scripts
echo.
pause