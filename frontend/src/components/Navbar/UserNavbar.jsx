import React from "react";
import { NavLink, useNavigate } from 'react-router-dom';
import './Navbar.css';
import { FaSignOutAlt } from "react-icons/fa";
import logo from '../../assets/logo.png';
import api from '../../api';

const Navbar = () => {
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await api.delete('/auth/logout', {
        headers: { Authorization: `Bearer ${localStorage.getItem('refresh_token')}` },
      });
    } catch (err) {
      console.error('Logout failed:', err);
    }
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="logo">
        <img src={logo} alt="Moringa school daily.dev logo" />
      </div>
      <ul className="nav-links">
        <li><NavLink to="/home" end className={({ isActive }) => isActive ? 'active' : ''}>Home</NavLink></li>
        <li><NavLink to="/feedpage" className={({ isActive }) => isActive ? 'active' : ''}>Feed</NavLink></li>
        <li><NavLink to="/category" className={({ isActive }) => isActive ? 'active' : ''}>Category</NavLink></li>
        <li><NavLink to="/notifications" className={({ isActive }) => isActive ? 'active' : ''}>Notifications</NavLink></li>
        <li><NavLink to="/profile" className={({ isActive }) => isActive ? 'active' : ''}>Profile</NavLink></li>
      </ul>
      <ul className="logout-link">
        <li>
          <NavLink to="/" onClick={handleLogout} className={({ isActive }) => isActive ? 'active' : ''}>
            <FaSignOutAlt style={{color: '#ffffff', fontSize: '20px'}} /> Logout
          </NavLink>
        </li>
      </ul>
    </nav>
  );
};

export default Navbar;