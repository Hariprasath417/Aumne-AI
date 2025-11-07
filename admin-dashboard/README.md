# WhatsApp Order Admin Dashboard

A modern React admin dashboard for managing menu items and orders in the WhatsApp-based food ordering system.

## Features

### Menu Management
- View all menu items in a responsive grid layout
- Create new menu items with name, description, price, and availability
- Edit existing menu items
- Toggle item availability (available/unavailable)
- Visual indicators for item status

### Orders Management
- View all orders with real-time updates (auto-refreshes every 5 seconds)
- Filter orders by status (All, Pending, Preparing, Out for Delivery, Delivered, Cancelled)
- Update order status with one-click actions:
  - Start Preparing (from Pending)
  - Mark Out for Delivery (from Preparing)
  - Mark Delivered (from Out for Delivery)
- Cancel orders (from Pending status)
- View order details including:
  - Customer name and WhatsApp number
  - Order items with quantities
  - Total price
  - Creation timestamp
  - Current status

## Getting Started

### Prerequisites
- Node.js (v14 or higher)
- npm or yarn
- Backend API running on `http://localhost:8000`

### Installation

1. Navigate to the admin dashboard directory:
```bash
cd admin-dashboard
```

2. Install dependencies (if not already installed):
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The dashboard will open at `http://localhost:3000` in your browser.

### Building for Production

To create a production build:
```bash
npm run build
```

This creates an optimized production build in the `build` folder.

## API Configuration

The dashboard is configured to connect to the backend API at `http://localhost:8000`. 

To change the API URL, edit `src/services/api.js` and update the `API_BASE_URL` constant.

## Project Structure

```
admin-dashboard/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── MenuManagement.js      # Menu management component
│   │   ├── MenuManagement.css     # Menu component styles
│   │   ├── OrdersManagement.js    # Orders management component
│   │   └── OrdersManagement.css   # Orders component styles
│   ├── services/
│   │   └── api.js                 # API service layer
│   ├── App.js                      # Main app component
│   ├── App.css                     # App styles
│   ├── index.js                    # Entry point
│   └── index.css                   # Global styles
└── package.json
```

## Usage

### Menu Management Tab
1. Click the "Menu" tab in the navigation
2. Click "+ Add Menu Item" to create a new item
3. Fill in the form (name, description, price, availability)
4. Click "Create" to save
5. Use "Edit" button on any card to modify an item
6. Use "Mark Available/Unavailable" to toggle item status

### Orders Management Tab
1. Click the "Orders" tab in the navigation
2. View all orders or filter by status using the filter buttons
3. Use action buttons to update order status:
   - **Start Preparing**: Move order from Pending to Preparing
   - **Mark Out for Delivery**: Move order from Preparing to Out for Delivery
   - **Mark Delivered**: Complete the order
   - **Cancel Order**: Cancel a pending order
4. Orders automatically refresh every 5 seconds

## Technologies Used

- React 18
- Create React App
- CSS3 (Modern styling with gradients and animations)
- Fetch API (for HTTP requests)

## Notes

- The dashboard requires the backend API to be running
- CORS must be enabled on the backend for the frontend to make requests
- Order status updates trigger WhatsApp notifications automatically via the backend
