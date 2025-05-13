import React, {useState, useEffect} from 'react';
import {useNavigate} from 'react-router-dom';
import api from '../../utils/api';
import './AdminHome.css';
import AdminNavbar from '../../components/Navbar/AdminNavbar';
import Footer from '../../components/Footer';
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
  const [stats, setStats] = useState({
    totalPosts: 0,
    newUsers: 0,
    flaggedContent: 0,
    activeCategories: 0
  });
  const [recentActivity, setRecentActivity] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  useEffect(() => {
    const loadStats = async () => {
      try {
        const usersRes = await api.get('/admin/users');
        const contentRes = await api.get('/content?page=1&per_page=1000');
        const catsRes = await api.get('/categories');
        const auditRes = await api.get('/audit?limit=5');
        const users = usersRes.data;                   
        const content = contentRes.data.items;         
        const categories = catsRes.data;          
        const activity = auditRes.data.items;     
        setStats({
          totalPosts: content.length,
          newUsers: users.filter(u => !u.roles.includes('Admin')).length,
          flaggedContent: content.filter(c => c.status === 'Flagged').length,
          activeCategories: categories.length
        });
        setRecentActivity(activity);
        setLoading(false);
      } catch (err) {
        console.error('Failed loading admin dashboard data', err);
      }
    };
    loadStats();
  }, []);
  return (
    <div className="admin-dashboard-wrapper">
      <AdminNavbar />
      <div className="admin-content">
        <h1>Welcome, Admin</h1>
        <p>Here’s what’s happening on daily.dev</p>
        <section className="quick-stats">
          <h2>Quick-Stats</h2>
          <div className="stats-grid">
            {loading
              ? Array(4).fill().map((_, i) => <SkeletonStatCard key={i} />)
              : (
                <>
                  <div className="stat-card">
                    <h3>Total Posts</h3>
                    <p>{stats.totalPosts.toLocaleString()}</p>
                  </div>
                  <div className="stat-card">
                    <h3>New Users</h3>
                    <p>{stats.newUsers}</p>
                  </div>
                  <div className="stat-card">
                    <h3>Flagged Content</h3>
                    <p>{stats.flaggedContent}</p>
                  </div>
                  <div className="stat-card">
                    <h3>Active Categories</h3>
                    <p>{stats.activeCategories}</p>
                  </div>
                </>
              )
            }
          </div>
          <div className="quick-actions">
            <button onClick={() => navigate('/admin/content')}>Manage Content</button>
            <button onClick={() => navigate('/admin/categories')}>Manage Categories</button>
            <button onClick={() => navigate('/admin/users')}>Manage Users</button>
          </div>
        </section>
        <section className="recent-activity">
          <h2>Recent Activity</h2>
          <div className="activity-table">
            <div className="table-header">
              <span>Time</span>
              <span>Action</span>
            </div>
            {loading
              ? Array(3).fill().map((_, i) => <SkeletonActivityRow key={i} />)
              : recentActivity.map((act, i) => (
                  <div key={i} className="activity-row">
                    <span>{new Date(act.timestamp).toLocaleString()}</span>
                    <span>{act.action}</span>
                  </div>
                ))
            }
          </div>
        </section>
      </div>
      <Footer />
    </div>
  );
};
export default AdminDashboard;