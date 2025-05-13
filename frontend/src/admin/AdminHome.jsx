import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchUsers, fetchContent, fetchCategories, fetchRecentActivity } from '../utils/MockData';
import './AdminHome.css';
import AdminNavbar from '../components/Navbar/AdminNavbar';
import Footer from '../components/Footer';

const SkeletonStatCard = () => (
  <div className="skeleton-stat-card">
    <div className="skeleton skeleton-title"></div>
    <div className="skeleton skeleton-number"></div>
  </div>
);

const SkeletonActivityRow = () => (
  <div className="skeleton-activity-row">
    <div className="skeleton skeleton-time"></div>
    <div className="skeleton skeleton-event"></div>
  </div>
);

const AdminDashboard = () => {
  const [stats, setStats] = useState({ totalPosts: 0, newUsers: 0, flaggedContent: 0, activeCategories: 0 });
  const [recentActivity, setRecentActivity] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const user = { name: 'Admin', role: 'Admin' }; // Mock admin user

  useEffect(() => {
    Promise.all([fetchUsers(), fetchContent(), fetchCategories(), fetchRecentActivity()])
      .then(([users, content, categories, activity]) => {
        setStats({
          totalPosts: content.length,
          newUsers: users.filter(u => u.role !== 'Admin').length,
          flaggedContent: content.filter(c => c.status === 'Flagged').length,
          activeCategories: categories.length,
        });
        setRecentActivity(activity);
        setLoading(false);
      });
  }, []);

  return (
    <div className="admin-dashboard-wrapper">
      <div>
        <AdminNavbar />
      </div>
      <div className="admin-content">
        <h1>Welcome, {user.name}</h1>
        <p>Here is what’s happening on daily.dev</p>
        <div className="quick-stats">
          <h2>Quick-Stats Cards</h2>
          <div className="stats-grid">
            {loading ? (
              Array(4).fill().map((_, index) => <SkeletonStatCard key={index} />)
            ) : (
              <>
                <div className="stat-card">
                  <h3>Total Posts</h3>
                  <p>{stats.totalPosts.toLocaleString()}</p>
                </div>
                <div className="stat-card">
                  <h3>New Users ({stats.newUsers})</h3>
                  <p>{stats.newUsers}</p>
                </div>
                <div className="stat-card">
                  <h3>Flagged Content</h3>
                  <p>{stats.flaggedContent}</p>
                </div>
                <div className="stat-card">
                  <h3>Active Categ.</h3>
                  <p>{stats.activeCategories}</p>
                </div>
              </>
            )}
          </div>
          <div className="quick-actions">
            <button onClick={() => navigate('/content-management')}>Approve Content</button>
            <button onClick={() => navigate('/content-management')}>Review Flags</button>
            <button onClick={() => navigate('/categories-management')}>Manage Categories</button>
            <button onClick={() => navigate('/user-management')}>Deactivate User</button>
          </div>
        </div>
        <div className="recent-activity">
          <h2>Recent Activity</h2>
          <div className="activity-table">
            <div className="table-header">
              <span>Time</span>
              <span>Event</span>
            </div>
            {loading ? (
              Array(3).fill().map((_, index) => <SkeletonActivityRow key={index} />)
            ) : (
              recentActivity.map((activity, index) => (
                <div key={index} className="activity-row">
                  <span>{activity.time}</span>
                  <span className={activity.status === 'Pending' ? 'pending' : ''}>{activity.event}</span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default AdminDashboard;