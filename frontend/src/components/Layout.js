import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import '../styles/Layout.css';

function Layout({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="layout">
      <header className="navbar">
        <div className="navbar-content">
          <div className="navbar-brand">
            <Link to="/">Sistema de Gestão de Casos TI</Link>
          </div>

          <nav className="navbar-menu">
            <Link to="/" className="nav-link">Dashboard</Link>
            <Link to="/cases/new" className="nav-link">Novo Caso</Link>
            <Link to="/sprints" className="nav-link">Sprints</Link>
          </nav>

          <div className="navbar-user">
            {user && <span className="user-name">{user.username}</span>}
            <button onClick={handleLogout} className="btn-logout">
              Sair
            </button>
          </div>
        </div>
      </header>

      <main className="main-content">
        {children}
      </main>

      <footer className="footer">
        <p>Sistema de Gestão de Casos TI - Baseado em ITIL &copy; 2024</p>
      </footer>
    </div>
  );
}

export default Layout;
