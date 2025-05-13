import React, {useState, useEffect} from 'react';
import {FaSearch} from 'react-icons/fa';
import {useNavigate} from 'react-router-dom';
import api from '../../utils/api';
import './CategoriesManagement.css';
import AdminNavbar from '../../components/Navbar/AdminNavbar';
import Footer from '../../components/Footer';
const SkeletonCategoryRow = () => (
  <div className="skeleton-category-row">
    <div className="skeleton skeleton-name"></div>
    <div className="skeleton skeleton-description"></div>
    <div className="skeleton skeleton-actions"></div>
  </div>
);
const AdminCategories = () => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading]         = useState(true);
  const [searchTerm, setSearchTerm]   = useState('');
  const [newCategory, setNewCategory] = useState({ name: '', description: '' });
  const [editId, setEditId]           = useState(null);
  const [showForm, setShowForm]       = useState(false);
  const navigate = useNavigate();
  useEffect(() => {
    const load = async () => {
      try {
        const res = await api.get('/admin/categories');
        setCategories(res.data);
      } catch (err) {
        console.error(err);
        alert('Could not fetch categories');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);
  const handleSave = async () => {
    if (!newCategory.name.trim()) return;
    try {
      if (editId) {
        await api.put(`/admin/categories/${editId}`, newCategory);
        setCategories(categories.map(c => c.id === editId ? { ...c, ...newCategory } : c));
      } else {
        const { data } = await api.post('/admin/categories', newCategory);
        setCategories([ ...categories, { id: data.id, ...newCategory } ]);
      }
      setShowForm(false);
      setEditId(null);
      setNewCategory({ name: '', description: '' });
    } catch (err) {
      console.error(err);
      alert(err.response?.data.error || 'Save failed');
    }
  };
  const handleDelete = async (id) => {
    if (!window.confirm('Delete this category?')) return;
    try {
      await api.delete(`/admin/categories/${id}`);
      setCategories(categories.filter(cat => cat.id !== id));
    } catch (err) {
      console.error(err);
      alert('Delete failed');
    }
  };
  const filtered = categories.filter(cat =>
    cat.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    cat.description.toLowerCase().includes(searchTerm.toLowerCase())
  );
  return (
    <div className="admin-categories-wrapper">
      <AdminNavbar />
      <header className="categories-header">
        <h1>Category Management</h1>
        <p>You have the ability to manage the categories in your system</p>
        <button onClick={() => setShowForm(true)}>+ Add Category</button>
      </header>
      {showForm && (
        <div className="category-form">
          <h3>{editId ? 'Edit' : 'New'} Category</h3>
          <input
            type="text"
            placeholder="Name"
            value={newCategory.name}
            onChange={e => setNewCategory({ ...newCategory, name: e.target.value })}
          />
          <input
            type="text"
            placeholder="Description"
            value={newCategory.description}
            onChange={e => setNewCategory({ ...newCategory, description: e.target.value })}
          />
          <div className="form-actions">
            <button onClick={() => { setShowForm(false); setEditId(null); }}>Cancel</button>
            <button onClick={handleSave}>{editId ? 'Update' : 'Create'}</button>
          </div>
        </div>
      )}
      <div className="search-bar-categories">
        <FaSearch className="search-icon" />
        <input
          type="text"
          placeholder="Search categories..."
          value={searchTerm}
          onChange={e => setSearchTerm(e.target.value)}
        />
      </div>
      <div className="categories-table">
        <div className="table-header">
          <span>Name</span>
          <span>Description</span>
          <span>Actions</span>
        </div>
        {loading
          ? Array(4).fill().map((_, i) => <SkeletonCategoryRow key={i} />)
          : filtered.map(cat => (
              <div key={cat.id} className="category-row">
                <span>{cat.name}</span>
                <span>{cat.description}</span>
                <div className="actions">
                  <button onClick={() => {
                    setEditId(cat.id);
                    setNewCategory({ name: cat.name, description: cat.description });
                    setShowForm(true);
                  }}>
                    Edit
                  </button>
                  <button onClick={() => handleDelete(cat.id)}>Delete</button>
                </div>
              </div>
            ))
        }
      </div>
      <Footer />
    </div>
  );
};
export default AdminCategories;