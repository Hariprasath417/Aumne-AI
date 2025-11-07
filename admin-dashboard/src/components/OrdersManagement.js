import React, { useState, useEffect } from 'react';
import { ordersAPI, menuAPI } from '../services/api';
import './OrdersManagement.css';

const OrdersManagement = () => {
  const [orders, setOrders] = useState([]);
  const [menuItems, setMenuItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [statusFilter, setStatusFilter] = useState('all');

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [ordersData, menuData] = await Promise.all([
        ordersAPI.getAll(),
        menuAPI.getAll(),
      ]);
      setOrders(ordersData);
      setMenuItems(menuData);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (orderId, newStatus) => {
    try {
      await ordersAPI.updateStatus(orderId, newStatus);
      fetchData();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleCancel = async (orderId) => {
    if (window.confirm('Are you sure you want to cancel this order?')) {
      try {
        await ordersAPI.cancel(orderId);
        fetchData();
      } catch (err) {
        setError(err.message);
      }
    }
  };

  const getMenuItemName = (menuItemId) => {
    const item = menuItems.find((m) => m.id === menuItemId);
    return item ? item.name : `Item #${menuItemId}`;
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: '#ff9800',
      preparing: '#2196f3',
      'out-for-delivery': '#9c27b0',
      delivered: '#4caf50',
      cancelled: '#f44336',
    };
    return colors[status] || '#757575';
  };

  const filteredOrders = statusFilter === 'all' 
    ? orders 
    : orders.filter((order) => order.status === statusFilter);

  const statusCounts = {
    all: orders.length,
    pending: orders.filter((o) => o.status === 'pending').length,
    preparing: orders.filter((o) => o.status === 'preparing').length,
    'out-for-delivery': orders.filter((o) => o.status === 'out-for-delivery').length,
    delivered: orders.filter((o) => o.status === 'delivered').length,
    cancelled: orders.filter((o) => o.status === 'cancelled').length,
  };

  if (loading && orders.length === 0) {
    return <div className="loading">Loading orders...</div>;
  }

  return (
    <div className="orders-management">
      <div className="orders-header">
        <h2>Orders Management</h2>
        <button className="btn btn-secondary" onClick={fetchData}>
          Refresh
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="status-filters">
        {Object.entries(statusCounts).map(([status, count]) => (
          <button
            key={status}
            className={`status-filter-btn ${statusFilter === status ? 'active' : ''}`}
            onClick={() => setStatusFilter(status)}
          >
            {status.charAt(0).toUpperCase() + status.slice(1).replace('-', ' ')} ({count})
          </button>
        ))}
      </div>

      <div className="orders-list">
        {filteredOrders.length === 0 ? (
          <div className="empty-state">No orders found.</div>
        ) : (
          filteredOrders.map((order) => (
            <div key={order.id} className="order-card">
              <div className="order-header">
                <div className="order-info">
                  <h3>Order #{order.id}</h3>
                  <span
                    className="status-badge"
                    style={{ backgroundColor: getStatusColor(order.status) }}
                  >
                    {order.status.charAt(0).toUpperCase() + order.status.slice(1).replace('-', ' ')}
                  </span>
                </div>
                <div className="order-meta">
                  <p><strong>Customer:</strong> {order.customer_name || 'N/A'}</p>
                  <p><strong>WhatsApp:</strong> {order.customer_whatsapp}</p>
                  <p><strong>Total:</strong> ₹{order.total_price.toFixed(2)}</p>
                  <p><strong>Created:</strong> {new Date(order.created_at).toLocaleString()}</p>
                </div>
              </div>

              <div className="order-items">
                <h4>Items:</h4>
                <ul>
                  {order.items.map((item, idx) => (
                    <li key={idx}>
                      {getMenuItemName(item.menu_item_id)} × {item.quantity}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="order-actions">
                {order.status === 'pending' && (
                  <>
                    <button
                      className="btn btn-primary"
                      onClick={() => handleStatusUpdate(order.id, 'preparing')}
                    >
                      Start Preparing
                    </button>
                    <button
                      className="btn btn-danger"
                      onClick={() => handleCancel(order.id)}
                    >
                      Cancel Order
                    </button>
                  </>
                )}
                {order.status === 'preparing' && (
                  <button
                    className="btn btn-primary"
                    onClick={() => handleStatusUpdate(order.id, 'out-for-delivery')}
                  >
                    Mark Out for Delivery
                  </button>
                )}
                {order.status === 'out-for-delivery' && (
                  <button
                    className="btn btn-success"
                    onClick={() => handleStatusUpdate(order.id, 'delivered')}
                  >
                    Mark Delivered
                  </button>
                )}
                {order.status === 'delivered' && (
                  <span className="completed-badge">Order Completed</span>
                )}
                {order.status === 'cancelled' && (
                  <span className="cancelled-badge">Order Cancelled</span>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default OrdersManagement;

