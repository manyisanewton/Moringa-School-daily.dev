import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Swal from 'sweetalert2';
import { FaUpload } from 'react-icons/fa';
import './TechWriterPosts.css';
import TechNavbar from '../components/Navbar/TechNavbar';
import Footer from '../components/Footer';

const TechWriterCreateContent = () => {
  const [formData, setFormData] = useState({
    title: '',
    category: '',
    description: '',
    file: null,
    fileName: '',
    type: '',
  });
  const navigate = useNavigate();

  // Hardcoded categories
  const categories = [
    { id: 1, name: 'Fullstack Development' },
    { id: 2, name: 'Cyber Security' },
    { id: 3, name: 'Data Science' },
    { id: 4, name: 'Mobile Development' },
    { id: 5, name: 'Artificial Intelligence' },
  ];

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const allowedTypes = ['image/jpeg', 'image/png', 'application/pdf', 'video/mp4'];
      const maxSize = 50 * 1024 * 1024; // 50MB in bytes
      if (!allowedTypes.includes(file.type)) {
        Swal.fire('Error', 'Only JPEG, PNG, PDF, and MP4 files are allowed.', 'error');
        return;
      }
      if (file.size > maxSize) {
        Swal.fire('Error', 'File size exceeds 50MB.', 'error');
        return;
      }
      let contentType = '';
      if (file.type.startsWith('image')) contentType = 'article';
      else if (file.type === 'application/pdf') contentType = 'article';
      else if (file.type === 'video/mp4') contentType = 'video';
      setFormData({ ...formData, file, fileName: file.name, type: contentType });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.title || !formData.category || !formData.description || !formData.file) {
      Swal.fire('Error', 'Please fill in all fields and upload a file.', 'error');
      return;
    }

    const category = categories.find(cat => cat.name === formData.category);
    if (!category) {
      Swal.fire('Error', 'Invalid category selected.', 'error');
      return;
    }

    const data = new FormData();
    data.append('title', formData.title);
    data.append('body', formData.description);
    data.append('content_type', formData.type);
    data.append('category', formData.category);  // Send category name instead of ID
    data.append('file', formData.file);

    try {
      const response = await axios.post('http://localhost:5000/content', data, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'multipart/form-data'
        }
      });
      Swal.fire('Success', 'Content submitted for approval!', 'success');
      navigate('/content');
    } catch (error) {
      console.error('Error submitting content:', error);
      Swal.fire('Error', 'Failed to submit content.', 'error');
    }
  };

  return (
    <div className="techwriter-create-content-wrapper">
      <div className="techwriter-header">
        <TechNavbar />
      </div>
      <div className="techwriter-content">
        <div className='greeting'>
            <h1>Create New Content</h1>
            <p>Share Knowledge with the Moringa Community!</p>
        </div>
        
        <form className="create-form" onSubmit={handleSubmit}>
          <label>Title:</label>
          <input
            type="text"
            name='title'
            placeholder="Title"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            required
          />
          <label>Category:</label>
          <select
            name='category'
            value={formData.category}
            onChange={(e) => setFormData({ ...formData, category: e.target.value })}
            required
          >
            <option value="">Select the Category</option>
            {categories.map(cat => (
              <option key={cat.id} value={cat.name}>{cat.name}</option>
            ))}
          </select>
          <label>Description:</label>
          <textarea
            name='description'
            placeholder="Write the Description"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            required
          />
          <label>Upload a File:</label>
          <div className="file-upload">
            <div className="upload-area">
              <FaUpload className="upload-icon" />
              <p>
                {formData.fileName || 'Choose a file or drag & drop it here!'}<br />
                JPEG, PNG, PDF, and MP4 formats, up to 50 MB.
              </p>
              <label htmlFor="file-upload" className="browse-btn" id="browse-btn">Browse File</label>
              <input
                id="file-upload"
                type="file"
                accept="image/jpeg,image/png,application/pdf,video/mp4"
                onChange={handleFileChange}
                style={{ display: 'none' }}
              />
            </div>
          </div>
          <button type="submit">Submit for Approval</button>
        </form>
      </div>
      <Footer />
    </div>
  );
};

export default TechWriterCreateContent;