import React from 'react';
import { NavLink } from 'react-router-dom';
import './Navbar.css';
import { FaSignOutAlt } from "react-icons/fa";
import logo from '../../assets/logo.png'; 

const TechNavbar = () => {
  return (
    <nav className="navbar">
      <div className="logo">
        <img src={logo} alt="Moringa School daily.dev logo" />
      </div>
      <ul className="nav-links">
        <li><NavLink to="/techhome" end className={({ isActive }) => isActive ? 'active' : ''}>Home</NavLink></li>
        <li><NavLink to="/my-posts" className={({ isActive }) => isActive ? 'active' : ''}>My Posts</NavLink></li>
        <li><NavLink to="/content" className={({ isActive }) => isActive ? 'active' : ''}>Content</NavLink></li>
        <li><NavLink to="/tech-writer-flagged" className={({ isActive }) => isActive ? 'active' : ''}>Notifications</NavLink></li>
        <li><NavLink to="/tech-writer-profile" className={({ isActive }) => isActive ? 'active' : ''}>My Profile</NavLink></li>
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

export default TechNavbar;
