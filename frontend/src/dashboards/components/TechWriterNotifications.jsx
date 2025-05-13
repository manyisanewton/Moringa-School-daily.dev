import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import io from 'socket.io-client';
import './TechWriterNotifications.css';

const socket = io('http://localhost:5000', {
  auth: (cb) => {
    const token = localStorage.getItem('access_token');
    cb({ token });
  },
});

const SkeletonNotificationRow = () => (
  <div className="skeleton-notification-row">
    <div className="skeleton skeleton-time"></div>
    <div className="skeleton skeleton-event"></div>
  </div>
);

const TechWriterNotifications = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [perPage] = useState(20);
  const [total, setTotal] = useState(0);
  const navigate = useNavigate();

  useEffect(() => {
    // Fetch initial notifications
    const fetchNotificationsData = async () => {
      try {
        const response = await axios.get('http://localhost:5000/notifications', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          },
          params: { page, per_page: perPage },
        });
        setNotifications(response.data.items || []);
        setTotal(response.data.total || 0);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching notifications:', error);
        setLoading(false);
      }
    };
    fetchNotificationsData();

    // Set up WebSocket listeners
    socket.on('connect', () => {
      console.log('Connected to WebSocket server');
      socket.emit('connect_notification', { token: localStorage.getItem('access_token') });
    });

    socket.on('new_notification', (notification) => {
      setNotifications((prev) => [notification, ...prev].slice(0, perPage)); // Limit to perPage
    });

    socket.on('disconnect', () => {
      console.log('Disconnected from WebSocket server');
    });

    return () => {
      socket.off('new_notification');
      socket.off('connect');
      socket.off('disconnect');
      socket.disconnect();
    };
  }, [page, perPage]);

  const handleMarkRead = async (id) => {
    try {
      await axios.post(`http://localhost:5000/notifications/${id}/read`, {}, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      setNotifications((prev) =>
        prev.map((notif) =>
          notif.id === id ? { ...notif, read: true } : notif
        )
      );
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  const handleLoadMore = () => {
    setPage((prev) => prev + 1);
    fetchMoreNotifications();
  };

  const fetchMoreNotifications = async () => {
    try {
      const response = await axios.get('http://localhost:5000/notifications', {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
        params: { page: page + 1, per_page: perPage },
      });
      setNotifications((prev) => [...prev, ...response.data.items]);
      setTotal(response.data.total);
    } catch (error) {
      console.error('Error fetching more notifications:', error);
    }
  };

  return (
    <div className="techwriter-content">
      <div className='intro-notification'>
        <h1>Notifications</h1>
        <p>View recent activity and updates on the platform</p>
      </div>
      <div className="notifications-content">
        <table className='notifications-table'>
          <thead className='notifications-table-head'>
            <tr>
              <th>Time</th>
              <th>Event</th>
              <th>Read</th>  
            </tr>
          </thead>
          <tbody>
            {loading ? (
              Array(3).fill().map((_, index) => <SkeletonNotificationRow key={index} />)
            ) : notifications.length > 0 ? (
              notifications.map((notification) => (
                <tr key={notification.id} className="notification-row">
                  <td>{new Date(notification.time).toLocaleString()}</td>
                  <td>{notification.message}</td>
                  <td>
                    <input
                      type="checkbox"
                      checked={notification.read || false}
                      onChange={() => handleMarkRead(notification.id)}
                      disabled={notification.read}
                    />
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="3">No notifications found.</td>
              </tr>
            )}
          </tbody>
        </table>
        {notifications.length < total && (
          <button onClick={handleLoadMore} disabled={loading}>
            Load More
          </button>
        )}
      </div>
    </div>
  );
};

export default TechWriterNotifications;