import React, { useState, useEffect } from 'react';
import { menuAPI } from '../services/api';
import './MenuManagement.css';

const MenuManagement = () => {
  const [menuItems, setMenuItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price: '',
    is_available: true,
  });

  useEffect(() => {
    fetchMenuItems();
  }, []);

  const fetchMenuItems = async () => {
    try {
      setLoading(true);
      const items = await menuAPI.getAll();
      setMenuItems(items);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const itemData = {
        ...formData,
        price: parseFloat(formData.price),
      };

      if (editingItem) {
        await menuAPI.update(editingItem.id, itemData);
      } else {
        await menuAPI.create(itemData);
      }

      setShowModal(false);
      setEditingItem(null);
      setFormData({
        name: '',
        description: '',
        price: '',
        is_available: true,
      });
      fetchMenuItems();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleEdit = (item) => {
    setEditingItem(item);
    setFormData({
      name: item.name,
      description: item.description,
      price: item.price.toString(),
      is_available: item.is_available,
    });
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingItem(null);
    setFormData({
      name: '',
      description: '',
      price: '',
      is_available: true,
    });
  };

  const toggleAvailability = async (item) => {
    try {
      await menuAPI.update(item.id, { is_available: !item.is_available });
      fetchMenuItems();
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) {
    return <div className="loading">Loading menu items...</div>;
  }

  return (
    <div className="menu-management">
      <div className="menu-header">
        <h2>Menu Management</h2>
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>
          + Add Menu Item
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="menu-grid">
        {menuItems.length === 0 ? (
          <div className="empty-state">No menu items found. Add your first item!</div>
        ) : (
          menuItems.map((item) => (
            <div key={item.id} className={`menu-card ${!item.is_available ? 'unavailable' : ''}`}>
              <div className="menu-card-header">
                <h3>{item.name}</h3>
                <span className={`status-badge ${item.is_available ? 'available' : 'unavailable'}`}>
                  {item.is_available ? 'Available' : 'Unavailable'}
                </span>
              </div>
              <p className="menu-description">{item.description}</p>
              <div className="menu-card-footer">
                <span className="menu-price">₹{item.price.toFixed(2)}</span>
                <div className="menu-actions">
                  <button
                    className="btn btn-secondary"
                    onClick={() => handleEdit(item)}
                  >
                    Edit
                  </button>
                  <button
                    className={`btn ${item.is_available ? 'btn-warning' : 'btn-success'}`}
                    onClick={() => toggleAvailability(item)}
                  >
                    {item.is_available ? 'Mark Unavailable' : 'Mark Available'}
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={handleCloseModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{editingItem ? 'Edit Menu Item' : 'Add Menu Item'}</h3>
              <button className="close-btn" onClick={handleCloseModal}>×</button>
            </div>
            <form onSubmit={handleSubmit} className="menu-form">
              <div className="form-group">
                <label>Name *</label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="form-group">
                <label>Description *</label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  required
                  rows="3"
                />
              </div>
              <div className="form-group">
                <label>Price (₹) *</label>
                <input
                  type="number"
                  name="price"
                  value={formData.price}
                  onChange={handleInputChange}
                  required
                  min="0"
                  step="0.01"
                />
              </div>
              <div className="form-group checkbox-group">
                <label>
                  <input
                    type="checkbox"
                    name="is_available"
                    checked={formData.is_available}
                    onChange={handleInputChange}
                  />
                  Available
                </label>
              </div>
              <div className="form-actions">
                <button type="button" className="btn btn-secondary" onClick={handleCloseModal}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  {editingItem ? 'Update' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default MenuManagement;

