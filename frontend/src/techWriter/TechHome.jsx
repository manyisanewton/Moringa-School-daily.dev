import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import TechNavbar from '../components/Navbar/TechNavbar';
import Footer from '../components/Footer';

import './TechHome.css';

const TechWriterDashboard = () => {
  const [stats, setStats] = useState({ totalPosts: 0, postsPending: 0, likes: 0, comments: 0 });
  const [userName, setUserName] = useState('Tech Writer');
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch user info
        const userResponse = await axios.get('http://localhost:5000/auth/me', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`
          }
        });
        setUserName(userResponse.data.name || 'Tech Writer');

        // Fetch stats
        const statsResponse = await axios.get('http://localhost:5000/content/stats', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`
          }
        });
        setStats(statsResponse.data);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching data:', error);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <div>
      <TechNavbar />
      <div className="techwriter-content">
        <h1>Welcome Back, {userName}</h1>
        <p>Here’s a snapshot of your content activity!!</p>
        <div className="stats-section">
          {loading ? (
            <div className="stats-loading">
              <div className="spinner"></div>
            </div>
          ) : (
            <>
              <div className="stat-card">
                <h3>Total Posts</h3>
                <p id='orange'>{stats.totalPosts}</p>
              </div>
              <div className="stat-card">
                <h3>Posts Pending</h3>
                <p id='orange'>{stats.postsPending}</p>
              </div>
              <div className="stat-card">
                <h3>Likes & Comments</h3>
                <p>
                  <span className='span-value'>{stats.likes}</span>
                  <span className='span-label'>Likes</span>
                  <br />
                  <span className='span-value'>{stats.comments}</span>
                  <span className='span-label'>Comments</span>
                </p>
              </div>
            </>
          )}
        </div>
        <div className="actions-section">
          <button onClick={() => navigate('/my-posts')}>Create New Content</button>
          <button onClick={() => navigate('/content')}>Review Posts</button>
          <button onClick={() => navigate('/tech-writer-profile')}>Edit Profile</button>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default TechWriterDashboard;