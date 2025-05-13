import React, {useState, useEffect} from 'react';
import {FaSearch} from 'react-icons/fa';
import {useNavigate} from 'react-router-dom';
import api from '../../utils/api';
import './ContentManagement.css';
import AdminNavbar from '../../components/Navbar/AdminNavbar';
import Footer from '../../components/Footer';
const SkeletonContentRow = () => (
  <div className="skeleton-content-row">
    <div className="skeleton skeleton-type" />
    <div className="skeleton skeleton-title" />
    <div className="skeleton skeleton-author" />
    <div className="skeleton skeleton-status" />
    <div className="skeleton skeleton-actions" />
  </div>
);
const AdminContent = () => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [statusFilter, setStatusFilter]   = useState('All');
  const [typeFilter, setTypeFilter]       = useState('All');
  const [sortBy, setSortBy]               = useState('Newest');
  const navigate = useNavigate();
  useEffect(() => {
    const load = async () => {
      try {
        const res = await api.get('/content?page=1&per_page=100');
        setItems(res.data);
      } catch (err) {
        console.error(err);
        alert('Could not fetch content');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);
  const refreshLocal = (updater) => setItems(cur => updater(cur));
  const handleApprove = async (id) => {
    if (!window.confirm('Approve this content?')) return;
    try {
      await api.post(`/admin/contents/${id}/approve`);
      refreshLocal(list => list.map(c => c.id === id ? { ...c, status: 'Published' } : c));
    } catch (err) {
      console.error(err);
      alert('Approve failed');
    }
  };
  const handleFlag = async (id) => {
    if (!window.confirm('Flag this content?')) return;
    try {
      await api.post(`/admin/contents/${id}/flag`, { reason: 'Flagged by admin' });
      refreshLocal(list => list.map(c => c.id === id ? { ...c, status: 'Flagged' } : c));
    } catch (err) {
      console.error(err);
      alert('Flag failed');
    }
  };
  const handleRemove = async (id) => {
    if (!window.confirm('Delete this content?')) return;
    try {
      await api.delete(`/admin/contents/${id}`);
      refreshLocal(list => list.filter(c => c.id !== id));
    } catch (err) {
      console.error(err);
      alert('Delete failed');
    }
  };
  const categories = Array.from(new Set(items.map(c => c.category_id))).map(id => `Category ${id}`);
  const statuses  = ['All', 'Draft', 'Pending', 'Published', 'Flagged'];
  const types     = ['All', 'video', 'audio', 'article', 'quote'];
  const filtered = items
    .filter(c => 
      (categoryFilter === 'All' || c.category_id === Number(categoryFilter)) &&
      (statusFilter === 'All' || c.status === statusFilter) &&
      (typeFilter === 'All' || c.content_type === typeFilter) &&
      (c.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
       c.body?.toLowerCase().includes(searchTerm.toLowerCase()))
    )
    .sort((a, b) =>
      sortBy === 'Newest' ? b.id - a.id : a.id - b.id
    );
  return (
    <div className="admin-content-wrapper">
      <AdminNavbar />
      <header className="content-header">
        <h1>Content Management</h1>
        <p>Manage, approve, or reject user submissions</p>
      </header>
      <div className="filters">
        <select value={categoryFilter} onChange={e => setCategoryFilter(e.target.value)}>
          <option value="All">Category</option>
          {categories.map(cat => <option key={cat} value={cat === 'Category All' ? 'All' : cat.split(' ')[1]}>{cat}</option>)}
        </select>
        <select value={statusFilter} onChange={e => setStatusFilter(e.target.value)}>
          {statuses.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
        <select value={typeFilter} onChange={e => setTypeFilter(e.target.value)}>
          {types.map(t => <option key={t} value={t}>{t}</option>)}
        </select>
        <select value={sortBy} onChange={e => setSortBy(e.target.value)}>
          <option value="Newest">Sort by: Newest</option>
          <option value="Oldest">Sort by: Oldest</option>
        </select>
        <FaSearch className="search-icon" />
        <input
          type="text"
          placeholder="Search content..."
          value={searchTerm}
          onChange={e => setSearchTerm(e.target.value)}
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
        {loading
          ? Array(4).fill().map((_, i) => <SkeletonContentRow key={i} />)
          : filtered.map(item => (
              <div key={item.id} className="content-row">
                <span>{item.content_type}</span>
                <span>{item.title}</span>
                <span>{item.author_id}</span>
                <span className={item.status.toLowerCase()}>{item.status}</span>
                <div className="actions">
                  {item.status !== 'Published' && (
                    <button onClick={() => handleApprove(item.id)}>Approve</button>
                  )}
                  {item.status !== 'Flagged' && (
                    <button onClick={() => handleFlag(item.id)}>Flag</button>
                  )}
                  <button onClick={() => handleRemove(item.id)}>Delete</button>
                </div>
              </div>
            ))
        }
      </div>
      <Footer />
    </div>
  );
};
export default AdminContent;