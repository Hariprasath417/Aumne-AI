const API_BASE_URL = 'http://localhost:8000';

// Menu API
export const menuAPI = {
  getAll: async () => {
    const response = await fetch(`${API_BASE_URL}/menu/`);
    if (!response.ok) throw new Error('Failed to fetch menu items');
    return response.json();
  },

  create: async (item) => {
    const response = await fetch(`${API_BASE_URL}/menu/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(item),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to create menu item');
    }
    return response.json();
  },

  update: async (itemId, updates) => {
    const response = await fetch(`${API_BASE_URL}/menu/${itemId}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updates),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update menu item');
    }
    return response.json();
  },
};

// Orders API
export const ordersAPI = {
  getAll: async () => {
    const response = await fetch(`${API_BASE_URL}/orders/`);
    if (!response.ok) throw new Error('Failed to fetch orders');
    return response.json();
  },

  updateStatus: async (orderId, status) => {
    const response = await fetch(`${API_BASE_URL}/orders/${orderId}`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ status }),
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to update order status');
    }
    return response.json();
  },

  cancel: async (orderId) => {
    const response = await fetch(`${API_BASE_URL}/orders/${orderId}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to cancel order');
    }
    return response.json();
  },
};

