import React, { useState, useEffect } from 'react';
import { motion } from "framer-motion";
import { FaCheckCircle, FaComment } from 'react-icons/fa';
import NotificationCard from '../components/NotificationCard';
import './Notificationss.css';
import NavBar from '../components/Navbar/UserNavbar';
import Footer from '../components/Footer';
import io from 'socket.io-client';
import axios from 'axios';

const token = localStorage.getItem('access_token')?.replace('Bearer ', '');
console.log('Token being sent to SocketIO:', token);
const socket = io('http://localhost:5000', {
  auth: {
    token: token
  }
});

const Notifications = () => {
  const [filter, setFilter] = useState('All');
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('newest');
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        const response = await axios.get('http://localhost:5000/notifications', {
          headers: { Authorization: `Bearer ${token}` }
        });
        const fetchedNotifications = response.data.items.map(notif => ({
          id: notif.id,
          type: notif.type,
          message: notif.message,
          subMessage: notif.subMessage,
          time: new Date(notif.time).toISOString(),
          icon: <FaCheckCircle style={{ color: '#11203A' }} />,
          read: notif.read
        }));
        setNotifications(fetchedNotifications);
      } catch (err) {
        console.error('Failed to fetch notifications:', err);
      }
    };

    if (token) {
      fetchNotifications();

      socket.on('new_notification', (notification) => {
        console.log('Received new notification:', notification); // Debug log
        setNotifications(prev => [{
          id: notification.id,
          type: notification.type,
          message: notification.message,
          subMessage: notification.subMessage,
          time: new Date(notification.time).toISOString(),
          icon: notification.type === 'Comment' ? <FaComment style={{ color: '#11203A' }} /> : <FaCheckCircle style={{ color: '#11203A' }} />,
          read: notification.read
        }, ...prev]);
      });

      socket.emit('connect_notification', { token });

      return () => {
        socket.off('new_notification');
      };
    } else {
      console.error('No token found in localStorage');
    }
  }, []);

  const toggleRead = async (id) => {
    try {
      await axios.post(`http://localhost:5000/notifications/${id}/read`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setNotifications(notifications.map(notif =>
        notif.id === id ? { ...notif, read: true } : notif
      ));
    } catch (err) {
      console.error('Failed to mark notification as read:', err);
    }
  };

  const filteredNotifications = notifications
    .filter(notification => {
      const matchesFilter = filter === 'All' || notification.type === filter;
      const matchesSearch = notification.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           notification.subMessage.toLowerCase().includes(searchTerm.toLowerCase());
      return matchesFilter && matchesSearch;
    })
    .sort((a, b) => {
      const timeA = new Date(a.time);
      const timeB = new Date(b.time);
      return sortBy === 'newest' ? timeB - timeA : timeA - timeB;
    });

  const unreadCount = notifications.filter(n => !n.read).length;
  const categories = ['All', 'Video', 'Article', 'Comment', 'System'];
  const sortOptions = ['newest', 'oldest'];

  return (
    <div>
      <NavBar />
      <div style={{ backgroundColor: '#f6f6f6', minHeight: '100vh', padding: '2rem', color: '#11203A' }}>
        <motion.h1
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          style={{ fontSize: '2.5rem', marginBottom: '1.5rem', fontWeight: 700, textTransform: 'capitalize', position: 'relative' }}
        >
          Notifications
          {unreadCount > 0 && (
            <span className="badge">{unreadCount}</span>
          )}
           <p style={{ color: '#11203A', marginBottom: '1.5rem', fontSize: '1.1rem', fontWeight: 'normal' }}>Stay updated with content & interactions</p>
        </motion.h1>
        <div className="controls">
            <div className="filter-section">
              {categories.map(category => (
                <button
                  key={category}
                  className={`filter-btn ${filter === category ? 'active' : ''}`}
                  onClick={() => setFilter(category)}
                >
                  {category}
                </button>
              ))}
            </div>
            <div className="sort-section">
              <select value={sortBy} onChange={(e) => setSortBy(e.target.value)} className="sort-select">
                {sortOptions.map(option => (
                  <option key={option} value={option}>{option.charAt(0).toUpperCase() + option.slice(1)}</option>
                ))}
              </select>
            </div>
            <div className="search-bar1">
              <input
                type="text"
                placeholder="Search Notifications"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="search-input"
              />
            </div>
        </div>

        <div className="notifications-container">
          <div className="notifications-grid">
            {filteredNotifications.length > 0 ? (
              filteredNotifications.map((notif) => (
                <motion.div
                  key={notif.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5 }}
                  className="notification-wrapper"
                >
                  <NotificationCard
                    icon={notif.icon}
                    message={notif.message}
                    subMessage={notif.subMessage}
                    time={new Date(notif.time).toLocaleTimeString()}
                    read={notif.read}
                    onToggleRead={() => toggleRead(notif.id)}
                    actionLabel={notif.subMessage.match(/\[(.*?)\]/)?.[1] || 'View'}
                    onActionClick={() => alert(`Navigating to ${notif.subMessage.match(/\[(.*?)\]/)?.[1] || 'details'}`)}
                  />
                </motion.div>
              ))
            ) : (
              <p className="no-notifications">No notifications found.</p>
            )}
          </div>
          <button className="clear-btn" onClick={() => setNotifications([])}>Clear All</button>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default Notifications;