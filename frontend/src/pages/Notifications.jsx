import React, { useState, useEffect } from 'react';
import { motion } from "framer-motion";
import { FaCheckCircle, FaComment, FaEye, FaEyeSlash, FaTimes } from 'react-icons/fa';
import NotificationCard from '../components/NotificationCard';
import './Notifications.css';
import NavBar from '../components/Navbar/UserNavbar';
import Footer from '../components/Footer';
import axios from 'axios';

const Notifications = () => {
  const [filter, setFilter] = useState('All');
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('newest');
  const [notifications, setNotifications] = useState([]);
  const [selectedVideo, setSelectedVideo] = useState(null);

  const RSS2JSON_API_KEY = 'qaroytlfmvhtdcvktht1hraeubbedie4ggiogmaz'; // Replace with your RSS2JSON API key if needed
  const VIDEO_API = `https://api.rss2json.com/v1/api.json?rss_url=https://www.youtube.com/feeds/videos.xml?channel_id=UCWv7vMbMWH4-V0ZXdmDpPBA&api_key=${RSS2JSON_API_KEY}`;
  const ARTICLE_API = 'https://dev.to/api/articles?tag=softwareengineering';

  // Helper function to check if a URL is a YouTube link
  const isYouTubeUrl = (url) => {
    return url && (url.includes('youtube.com') || url.includes('youtu.be'));
  };

  // Helper function to extract YouTube video ID
  const getYouTubeVideoId = (url) => {
    const regex = /(?:v=|\/)([0-9A-Za-z_-]{11})/;
    const match = url.match(regex);
    return match ? match[1] : null;
  };

  // Helper function to calculate time difference
  const getTimeAgo = (dateString) => {
    const now = new Date();
    const date = new Date(dateString);
    const diffInMs = now - date;
    const diffInMinutes = Math.floor(diffInMs / (1000 * 60));
    if (diffInMinutes < 60) {
      return `${diffInMinutes}m ago`;
    } else {
      const diffInHours = Math.floor(diffInMinutes / 60);
      return `${diffInHours} hour${diffInHours > 1 ? 's' : ''} ago`;
    }
  };

  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        // Fetch videos from YouTube via RSS2JSON
        const videoResponse = await axios.get(VIDEO_API);
        const videos = videoResponse.data.items || [];

        // Fetch articles from Dev.to
        const articleResponse = await axios.get(ARTICLE_API);
        const articles = articleResponse.data || [];

        // Map API data to notifications
        const videoNotifications = videos.slice(0, 3).map((video, index) => ({
          id: `video-${index + 1}`,
          type: 'Video',
          message: 'New Video posted in "Full-Stack Development"',
          subMessage: `"${video.title}" by ${video.author} [Watch Now]`,
          time: getTimeAgo(video.pubDate),
          icon: <FaCheckCircle style={{ color: '#11203A' }} />,
          read: false,
          url: video.link,
        }));

        const articleNotifications = articles.slice(0, 3).map((article, index) => ({
          id: `article-${index + 1}`,
          type: 'Article',
          message: 'New article in your followed category "DevOps"',
          subMessage: `"${article.title}" by ${article.user?.name} [Read Article]`,
          time: getTimeAgo(article.published_at),
          icon: <FaCheckCircle style={{ color: '#11203A' }} />,
          read: false,
          url: article.url,
        }));

        // Combine notifications (you can add comments manually or fetch from another source if needed)
        const commentNotification = {
          id: 'comment-1',
          type: 'Comment',
          message: 'Newton Manyisa replied to your comment on "Tech Careers"',
          subMessage: '"Totally agree with your point about mentorship!" [View Thread]',
          time: '20m ago',
          icon: <FaComment style={{ color: '#11203A' }} />,
          read: false,
          url: '#', // Placeholder for comment thread link
        };

        const fetchedNotifications = [
          ...videoNotifications,
          ...articleNotifications,
          commentNotification,
        ];

        setNotifications(fetchedNotifications);
      } catch (err) {
        console.error('Failed to fetch notifications:', err);
        // Fallback to placeholder notifications if API fails
        setNotifications([
          {
            id: 1,
            type: 'Video',
            message: 'New Video posted in "Full-Stack Development"',
            subMessage: '"Mastering APIs with Django" by Jane Mwangi [Watch Now]',
            time: '5m ago',
            icon: <FaCheckCircle style={{ color: '#11203A' }} />,
            read: false,
            url: '#',
          },
          {
            id: 2,
            type: 'Article',
            message: 'New article in your followed category "DevOps"',
            subMessage: '"CI/CD Done Right: Real Use Cases" [Read Article]',
            time: '1 hour ago',
            icon: <FaCheckCircle style={{ color: '#11203A' }} />,
            read: false,
            url: '#',
          },
          {
            id: 3,
            type: 'Comment',
            message: 'Newton Manyisa replied to your comment on "Tech Careers"',
            subMessage: '"Totally agree with your point about mentorship!" [View Thread]',
            time: '20m ago',
            icon: <FaComment style={{ color: '#11203A' }} />,
            read: false,
            url: '#',
          },
        ]);
      }
    };

    fetchNotifications();
  }, []);

  const toggleRead = (id) => {
    setNotifications(notifications.map(notif =>
      notif.id === id ? { ...notif, read: !notif.read } : notif
    ));
  };

  const filteredNotifications = notifications
    .filter(notification => {
      const matchesFilter = filter === 'All' || notification.type === filter;
      const matchesSearch = notification.message.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           notification.subMessage.toLowerCase().includes(searchTerm.toLowerCase());
      return matchesFilter && matchesSearch;
    })
    .sort((a, b) => {
      const timeA = new Date(`2025-05-13T${a.time.replace('m ago', 'minutes ago').replace('hour ago', 'hours ago')}`);
      const timeB = new Date(`2025-05-13T${b.time.replace('m ago', 'minutes ago').replace('hour ago', 'hours ago')}`);
      return sortBy === 'newest' ? timeB - timeA : timeA - timeB;
    });

  const unreadCount = notifications.filter(n => !n.read).length;
  const categories = ['All', 'Video', 'Article', 'Comment'];
  const sortOptions = ['newest', 'oldest'];

  const handleActionClick = (notification) => {
    if (notification.type === 'Video' && notification.url) {
      setSelectedVideo(notification);
    } else if (notification.type === 'Article' && notification.url) {
      window.open(notification.url, '_blank', 'noopener,noreferrer');
    } else {
      alert(`Navigating to ${notification.subMessage.match(/\[(.*?)\]/)[1]}`);
    }
  };

  const closeModal = () => setSelectedVideo(null);

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
          <p style={{ color: '#11203A', marginBottom: '1.5rem', fontSize: '1.1rem', fontWeight: 'normal' }}>
            Stay updated with content & interactions
          </p>
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
                    time={notif.time}
                    read={notif.read}
                    onToggleRead={() => toggleRead(notif.id)}
                    actionLabel={notif.subMessage.match(/\[(.*?)\]/)[1]}
                    onActionClick={() => handleActionClick(notif)}
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
      {selectedVideo && (
        <div className="modal" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="close-btn" onClick={closeModal}>
              <FaTimes />
            </button>
            <h3>{selectedVideo.subMessage.replace(/\[(.*?)\]/, '').trim()}</h3>
            {selectedVideo.url && isYouTubeUrl(selectedVideo.url) ? (
              <iframe
                width="600"
                height="338"
                src={`https://www.youtube.com/embed/${getYouTubeVideoId(selectedVideo.url)}`}
                title={selectedVideo.subMessage.replace(/\[(.*?)\]/, '').trim()}
                frameBorder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              ></iframe>
            ) : (
              <p>
                <a href={selectedVideo.url} target="_blank" rel="noopener noreferrer">
                  Watch the video here
                </a>
              </p>
            )}
          </div>
        </div>
      )}
      <Footer />
    </div>
  );
};

export default Notifications;