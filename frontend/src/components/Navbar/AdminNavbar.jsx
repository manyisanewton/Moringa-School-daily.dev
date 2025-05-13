import React from 'react';
import { NavLink } from 'react-router-dom';
import './Navbar.css';
import { FaSignOutAlt } from "react-icons/fa";
import logo from '../../assets/logo.png'; 

const AdminNavbar = () => {
  return (
    <nav className="navbar">
      <div className="logo">
        <img src={logo} alt="Moringa School daily.dev logo" />
      </div>
      <ul className="nav-links">
        <li><NavLink to="/admin-home" end className={({ isActive }) => isActive ? 'active' : ''}>Home</NavLink></li>
        <li><NavLink to="/user-management" className={({ isActive }) => isActive ? 'active' : ''}>Users</NavLink></li>
        <li><NavLink to="/content-management" className={({ isActive }) => isActive ? 'active' : ''}>Content</NavLink></li>
        <li><NavLink to="/categories-management" className={({ isActive }) => isActive ? 'active' : ''}>Categories</NavLink></li>
        <li><NavLink to="/admin-profile" className={({ isActive }) => isActive ? 'active' : ''}>Profile</NavLink></li>
      </ul>
      <ul className='logout-link'> 
        <li>
          <NavLink to="/" className={({ isActive }) => isActive ? 'active' : ''}>
            <FaSignOutAlt style={{ color: '#ffffff', fontSize: '20px' }} /> Logout
          </NavLink>
        </li>
      </ul>
    </nav>
  );
};

export default AdminNavbar;