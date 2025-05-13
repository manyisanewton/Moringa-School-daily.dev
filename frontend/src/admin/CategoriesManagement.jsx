import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchCategories, addCategory, updateCategory, deleteCategory, addContent, addRecentActivity } from '../utils/MockData';
import './CategoriesManagement.css';
import AdminNavbar from '../components/Navbar/AdminNavbar';
import Footer from '../components/Footer';
import { FaSearch } from 'react-icons/fa';

const SkeletonCategoryRow = () => (
  <div className="skeleton-category-row">
    <div className="skeleton skeleton-name"></div>
    <div className="skeleton skeleton-description"></div>
    <div className="skeleton skeleton-posts"></div>
    <div className="skeleton skeleton-actions"></div>
  </div>
);

const AdminCategories = () => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [newCategory, setNewCategory] = useState({ name: '', description: '', posts: 0 });
  const [newContent, setNewContent] = useState({
    title: '',
    description: '',
    file: null,
    fileName: '',
    type: '',
  });
  const [showAddForm, setShowAddForm] = useState(false);
  const [editCategoryId, setEditCategoryId] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchCategories().then(data => {
      setCategories(data);
      setLoading(false);
    });
  }, []);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const allowedTypes = ['image/jpeg', 'image/png', 'application/pdf', 'video/mp4'];
      const maxSize = 50 * 1024 * 1024; // 50MB in bytes
      if (!allowedTypes.includes(file.type)) {
        alert('Only JPEG, PNG, PDF, and MP4 files are allowed.');
        return;
      }
      if (file.size > maxSize) {
        alert('File size exceeds 50MB.');
        return;
      }
      let contentType = '';
      if (file.type.startsWith('image')) contentType = 'Article'; // Treat images as articles for simplicity
      else if (file.type === 'application/pdf') contentType = 'PDF';
      else if (file.type === 'video/mp4') contentType = 'Video';

      setNewContent({
        ...newContent,
        file,
        fileName: file.name,
        type: contentType,
      });
    }
  };

  const handleAddCategory = () => {
    if (newCategory.name && newCategory.description) {
      const category = { ...newCategory };
      addCategory(category);
      addRecentActivity(`New Category "${newCategory.name}" Created`);
      setCategories([...categories, { id: categories.length + 1, ...category }]);

      // Add associated content if provided
      if (newContent.title && newContent.description && newContent.file) {
        const content = {
          type: newContent.type,
          title: newContent.title,
          author: 'Admin User', // Mock admin user
          category: newCategory.name,
          description: newContent.description,
          fileName: newContent.fileName,
        };
        addContent(content);
        addRecentActivity(`Content "${newContent.title}" submitted for category "${newCategory.name}" (Pending approval)`);
      }

      setNewCategory({ name: '', description: '', posts: 0 });
      setNewContent({ title: '', description: '', file: null, fileName: '', type: '' });
      setShowAddForm(false);
    }
  };

  const handleEditCategory = (category) => {
    setEditCategoryId(category.id);
    setNewCategory({ name: category.name, description: category.description, posts: category.posts });
    setShowAddForm(true);
  };

  const handleUpdateCategory = () => {
    updateCategory(editCategoryId, newCategory);
    setCategories(categories.map(cat => (cat.id === editCategoryId ? { ...cat, ...newCategory } : cat)));
    setEditCategoryId(null);
    setNewCategory({ name: '', description: '', posts: 0 });
    setNewContent({ title: '', description: '', file: null, fileName: '', type: '' });
    setShowAddForm(false);
  };

  const handleDeleteCategory = (id) => {
    deleteCategory(id);
    setCategories(categories.filter(cat => cat.id !== id));
    addRecentActivity(`Category "${categories.find(c => c.id === id).name}" Deleted`);
  };

  const filteredCategories = categories.filter(category =>
    category.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    category.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="admin-categories-wrapper">
      <div>
        <AdminNavbar />
      </div>
        <div className="categories-header">
            <h1>Category Management</h1>
            <p>You have the ability to manage the various categories in your system</p>
        </div>
        <div className="search-bar-categories">
          <input
            type="text"
            placeholder="Search for Categories"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <FaSearch className="search-icon" />
          {/* <button onClick={() => setShowAddForm(true)}>Add Category</button> */}
        </div>
        <div className="add-category-btn">
            <button onClick={() => setShowAddForm(true)}>Add Category</button>
        </div>
        {showAddForm && (
          <div className="add-category-form">
            <h3>{editCategoryId ? 'Edit Category' : 'Add New Category'}</h3>
            <label>Category Name:</label>
            <input
              type="text"
              placeholder="Category Name"
              value={newCategory.name}
              onChange={(e) => setNewCategory({ ...newCategory, name: e.target.value })}
            />
            <label>Description:</label>
            <input
              type="text"
              placeholder="Description"
              value={newCategory.description}
              onChange={(e) => setNewCategory({ ...newCategory, description: e.target.value })}
            />
            <label>Number of Posts:</label>
            <input
              type="number"
              placeholder="Number of Posts"
              value={newCategory.posts}
              onChange={(e) => setNewCategory({ ...newCategory, posts: parseInt(e.target.value) || 0 })}
            />
            {!editCategoryId && (
              <>
                <h4>Add Content to This Category</h4>
                <label>Title:</label>
                <input
                  type="text"
                  placeholder="Title"
                  value={newContent.title}
                  onChange={(e) => setNewContent({ ...newContent, title: e.target.value })}
                />
                <label>Category:</label>
                <select value={newCategory.name} disabled>
                  <option value={newCategory.name}>{newCategory.name}</option>
                </select>
                <label>Description:</label>
                <textarea
                  placeholder="Write the Description"
                  value={newContent.description}
                  onChange={(e) => setNewContent({ ...newContent, description: e.target.value })}
                />
                <label>Upload a File:</label>
                <div className="file-upload">
                  <div className="upload-area">
                    <span className="upload-icon">↻</span>
                    <p>
                      {newContent.fileName || 'Choose a file or drag & drop it here!'}<br />
                      JPEG, PNG, PDF, and MP4 formats, up to 50 MB.
                    </p>
                    <label htmlFor="file-upload" className="browse-btn">Browse File</label>
                    <input
                      id="file-upload"
                      type="file"
                      accept="image/jpeg,image/png,application/pdf,video/mp4"
                      onChange={handleFileChange}
                      style={{ display: 'none' }}
                    />
                  </div>
                </div>
              </>
            )}
            <div className="form-actions">
              <button onClick={() => setShowAddForm(false)}>Cancel</button>
              <button onClick={editCategoryId ? handleUpdateCategory : handleAddCategory}>
                {editCategoryId ? 'Update' : 'Add'}
              </button>
            </div>
          </div>
        )}
        <div className="categories-table">
          <div className="table-header">
            <span>Name</span>
            <span>Description</span>
            <span>Posts</span>
            <span>Actions</span>
          </div>
          {loading ? (
            Array(4).fill().map((_, index) => <SkeletonCategoryRow key={index} />)
          ) : (
            filteredCategories.map(category => (
              <div key={category.id} className="category-row">
                <span>{category.name}</span>
                <span>{category.description}</span>
                <span>{category.posts}</span>
                <div className="actions">
                  <button onClick={() => handleEditCategory(category)}>Edit</button>
                  <button onClick={() => handleDeleteCategory(category.id)}>Delete</button>
                </div>
              </div>
            ))
          )}
        </div>
        <Footer />
      </div>
  );
};

export default AdminCategories;

