# Quick Start Guide

## Prerequisites
1. Make sure your FastAPI backend is running on `http://localhost:8000`
2. Node.js and npm should be installed

## Steps to Run

### 1. Start the Backend
In your main project directory, run:
```bash
python main.py
```
Or if using uvicorn directly:
```bash
uvicorn main:app --reload
```

### 2. Start the Admin Dashboard
Open a new terminal and navigate to the admin dashboard:
```bash
cd admin-dashboard
npm start
```

The React app will automatically open in your browser at `http://localhost:3000`

## Features Overview

### Menu Tab
- **View Menu**: See all menu items in a card-based layout
- **Add Item**: Click "+ Add Menu Item" button
- **Edit Item**: Click "Edit" on any menu card
- **Toggle Availability**: Use "Mark Available/Unavailable" button

### Orders Tab
- **View Orders**: See all orders with details
- **Filter by Status**: Use filter buttons at the top
- **Update Status**: 
  - Pending → Click "Start Preparing"
  - Preparing → Click "Mark Out for Delivery"
  - Out for Delivery → Click "Mark Delivered"
- **Cancel Order**: Click "Cancel Order" on pending orders
- **Auto-refresh**: Orders refresh every 5 seconds automatically

## Troubleshooting

### CORS Errors
If you see CORS errors, make sure:
1. The backend has CORS middleware configured (already added in main.py)
2. Backend is running on port 8000
3. Frontend is running on port 3000

### API Connection Issues
- Verify backend is running: Visit `http://localhost:8000/docs`
- Check browser console for error messages
- Ensure API_BASE_URL in `src/services/api.js` matches your backend URL

### Port Already in Use
If port 3000 is in use:
- React will prompt to use a different port
- Or manually set: `PORT=3001 npm start`

