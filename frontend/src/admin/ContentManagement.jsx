import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchContent, updateContent, deleteContent, addRecentActivity } from '../utils/MockData';
import './ContentManagement.css';
import AdminNavbar from '../components/Navbar/AdminNavbar';
import Footer from '../components/Footer';

const SkeletonContentRow = () => (
  <div className="skeleton-content-row">
    <div className="skeleton skeleton-type"></div>
    <div className="skeleton skeleton-title"></div>
    <div className="skeleton skeleton-author"></div>
    <div className="skeleton skeleton-status"></div>
    <div className="skeleton skeleton-actions"></div>
  </div>
);

const AdminContent = () => {
  const [content, setContent] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [statusFilter, setStatusFilter] = useState('All');
  const [typeFilter, setTypeFilter] = useState('All');
  const [sortBy, setSortBy] = useState('Newest');
  const navigate = useNavigate();

  useEffect(() => {
    fetchContent().then(data => {
      setContent(data);
      setLoading(false);
    });
  }, []);

  const handleApprove = (id) => {
    updateContent(id, { status: 'Approved' });
    setContent(content.map(item => (item.id === id ? { ...item, status: 'Approved' } : item)));
    addRecentActivity(`Content "${content.find(c => c.id === id).title}" Approved`);
  };

  const handleFlag = (id) => {
    updateContent(id, { status: 'Flagged' });
    setContent(content.map(item => (item.id === id ? { ...item, status: 'Flagged' } : item)));
    addRecentActivity(`Content "${content.find(c => c.id === id).title}" Flagged`);
  };

  const handleRemove = (id) => {
    deleteContent(id);
    setContent(content.filter(item => item.id !== id));
    addRecentActivity(`Content "${content.find(c => c.id === id).title}" Removed`);
  };

  const filteredContent = content
    .filter(item =>
      (categoryFilter === 'All' || item.category === categoryFilter) &&
      (statusFilter === 'All' || item.status === statusFilter) &&
      (typeFilter === 'All' || item.type === typeFilter) &&
      (item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
       item.author.toLowerCase().includes(searchTerm.toLowerCase()))
    )
    .sort((a, b) => sortBy === 'Newest' ? b.id - a.id : a.id - b.id);

  const categories = [...new Set(content.map(item => item.category))];
  const statuses = ['All', 'Pending', 'Approved', 'Flagged'];
  const types = ['All', 'Article', 'Video', 'Audio'];

  return (
    <div className="admin-content-wrapper">
      <div>
        <AdminNavbar />
      </div>
        <div className='content-header'>
            <h1>Content Management</h1>
            <p>Manage, approve, Reject contents posted by users before it goes up</p>
        </div>
        <div className="filters">
          <select value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)}>
            <option value="All">Category</option>
            {categories.map(cat => <option key={cat} value={cat}>{cat}</option>)}
          </select>
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            {statuses.map(status => <option key={status} value={status}>{status}</option>)}
          </select>
          <select value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
            {types.map(type => <option key={type} value={type}>{type}</option>)}
          </select>
          <select id='filter-select' value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
            <option value="Newest">Sort by: Newest</option>
            <option value="Oldest">Sort by: Oldest</option>
          </select>
          <input
            type="text"
            placeholder="Search for Content"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="content-table">
          <div className="table-header">
            <span>Type</span>
            <span>Title</span>
            <span>Author</span>
            <span>Status</span>
            <span>Actions</span>
          </div>
          {loading ? (
            Array(4).fill().map((_, index) => <SkeletonContentRow key={index} />)
          ) : (
            filteredContent.map(item => (
              <div key={item.id} className="content-row">
                <span>{item.type}</span>
                <span>{item.title}</span>
                <span>{item.author}</span>
                <span className={item.status.toLowerCase()}>{item.status}</span>
                <div className="actions">
                  {item.status !== 'Approved' && (
                    <button onClick={() => handleApprove(item.id)}>App</button>
                  )}
                  {item.status !== 'Flagged' && (
                    <button onClick={() => handleFlag(item.id)}>Flag</button>
                  )}
                  <button onClick={() => handleRemove(item.id)}>Rem</button>
                </div>
              </div>
            ))
          )}
        </div>
      <Footer />
    </div>
  );
};

export default AdminContent;

