import React from "react";
import { Link } from "react-router-dom";
import './Footer.css';
import { FaFacebookF, FaTwitter, FaLinkedinIn, FaInstagram } from 'react-icons/fa';
import logo from '../assets/logo.png';

const Footer = () => {
    return (
        <footer className="footer">
            <div className="footer-section-left">
                <div className="logo">
                    <img src={logo} alt="Moringa School Daily.dev logo" />
                    <p>Authentic tech insights from the <br /> Moringa Community</p>
                </div>
            </div>

            <div className="footer-section-center">
                <h4>Quick Links</h4>
                <ul>
                    <li><Link to="/">Home</Link></li>
                    <li><Link to="/feed">Feed</Link></li>
                    <li><Link to="/category">Category</Link></li>
                    <li><Link to="/notifications">Notifications</Link></li>
                </ul>
                <p className="copyright">©2025 TechTitans</p>
            </div>

            <div className="footer-section-right">
                <h4>Stay Connected</h4>
                <div className="social-icons">
                    <a href="https://www.facebook.com/moringaschool/" target="_blank" rel="noopener noreferrer">
                        <FaFacebookF />
                    </a>
                    <a href="https://x.com/moringaschool/status/1745768613095547181" target="_blank" rel="noopener noreferrer">
                        <FaTwitter />
                    </a>
                    <a href="https://www.linkedin.com" target="_blank" rel="noopener noreferrer">
                        <FaLinkedinIn />
                    </a>
                    <a href="https://www.instagram.com/moringaschool/?hl=en" target="_blank" rel="noopener noreferrer">
                        <FaInstagram />
                    </a>
                </div>
            </div>
        </footer>
    );
};

export default Footer;