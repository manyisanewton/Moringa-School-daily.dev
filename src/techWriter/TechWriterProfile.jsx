import React, { useState, useEffect } from 'react';
import { motion } from "framer-motion";
import { FaCamera, FaUserAlt } from 'react-icons/fa';
import axios from 'axios';
import TechNavbar from '../components/Navbar/TechNavbar.jsx';
import FormInput from '../components/FormInput.jsx';
import Footer from '../components/Footer.jsx'
import './TechWriterProfile.css';

const TechWriterProfile = () => {
  const [previewImage, setPreviewImage] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    avatar: null
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const profileResponse = await axios.get('http://localhost:5000/profiles/me', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`
          }
        });
        const userResponse = await axios.get('http://localhost:5000/auth/me', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`
          }
        });
        setFormData({
          name: profileResponse.data.name || userResponse.data.name || '',
          email: userResponse.data.email || '',
          password: '',
          avatar: null
        });
        setPreviewImage(profileResponse.data.avatar_url);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching profile:', error);
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      const imageUrl = URL.createObjectURL(file);
      setPreviewImage(imageUrl);
      setFormData({ ...formData, avatar: file });
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const data = new FormData();
    data.append('name', formData.name);
    if (formData.password) {
      data.append('password', formData.password);
    }
    if (formData.avatar) {
      data.append('avatar', formData.avatar);
    }

    try {
      await axios.patch('http://localhost:5000/profiles/me', data, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'multipart/form-data'
        }
      });
      alert('Profile updated successfully!');
    } catch (error) {
      console.error('Error updating profile:', error);
      alert('Failed to update profile.');
    }
  };

  const handleCancel = () => {
    navigate('/tech-writer-dashboard');
  };

  if (loading) return <p>Loading...</p>;

  return (
    <div className="profile-page">
      <TechNavbar />
      <div className='head-content'>
        <h2>Profile</h2>
      </div>
      <div style={{ backgroundColor: '#ffffff', minHeight: '100vh', padding: '1rem', color: '#FFF' }}>
        <div className="profile-container">
          <h3>Edit your profile...</h3>
          <div className="profile-image-section">
            <div className="profile-image">
              {previewImage ? (
                <img src={previewImage} alt="Profile" style={{ width: '150px', height: '150px' }} />
              ) : (
                <FaUserAlt className='img' style={{ fontSize: '100px', color: '#ececec', width: '150px', height: '150px' }} />
              )}
            </div>
            <label htmlFor="photo-upload" className="upload-btn">
              <FaCamera /> Upload Photo
              <input id="photo-upload" type="file" style={{ display: 'none' }} onChange={handleImageUpload} />
            </label>
          </div>
          <form className="form-section" onSubmit={handleSubmit}>
            <FormInput
              placeholder="Full Name"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
            />
            <FormInput
              placeholder="Email Address"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              disabled
            />
            <FormInput
              placeholder="Password"
              type="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
            />
            <p style={{ color: '#F8510B', margin: '1rem 0', fontSize: '1rem', alignContent: 'center' }}>
              Please note that to delete your account will be checked with our admin
            </p>
            <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem', justifyContent: 'center' }}>
              <button
                type="button"
                className="btn-profile"
                style={{ backgroundColor: '#ffffff', color: '#11203a', border: '1px solid #11203a', padding: '0.8rem 1.3rem', borderRadius: '7px', fontSize: '15px' }}
                onClick={handleCancel}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn-profile"
                style={{ backgroundColor: '#11203a', color: '#FFF', border: '1px solid #11203a', padding: '0.8rem 1.3rem', borderRadius: '7px', fontSize: '15px' }}
              >
                Save
              </button>
            </div>
          </form>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default TechWriterProfile;