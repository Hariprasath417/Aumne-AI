import React, { useState } from 'react';
import MenuManagement from './components/MenuManagement';
import OrdersManagement from './components/OrdersManagement';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('orders');

  return (
    <div className="App">
      <header className="app-header">
        <h1>WhatsApp Order Admin Dashboard</h1>
        <nav className="nav-tabs">
          <button
            className={`nav-tab ${activeTab === 'orders' ? 'active' : ''}`}
            onClick={() => setActiveTab('orders')}
          >
            Orders
          </button>
          <button
            className={`nav-tab ${activeTab === 'menu' ? 'active' : ''}`}
            onClick={() => setActiveTab('menu')}
          >
            Menu
          </button>
        </nav>
      </header>
      <main className="app-main">
        {activeTab === 'orders' && <OrdersManagement />}
        {activeTab === 'menu' && <MenuManagement />}
      </main>
    </div>
  );
}

export default App;
