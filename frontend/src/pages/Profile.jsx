import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { FaCamera, FaUserAlt } from 'react-icons/fa';
import Navbar from '../components/Navbar/UserNavbar.jsx';
import FormInput from '../components/FormInput.jsx';
import Footer from '../components/Footer.jsx';
import './Profile.css';
import axios from 'axios';

const Profile = () => {
  const [previewImage, setPreviewImage] = useState(null);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [bio, setBio] = useState('');
  const [avatarFile, setAvatarFile] = useState(null);
  const [socialLinks, setSocialLinks] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  // Function to fetch profile data
  const fetchProfile = async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      setError('Please log in to view your profile.');
      return;
    }

    try {
      const response = await axios.get('http://localhost:5000/profiles/me', {
        headers: { Authorization: `Bearer ${token}` },
      });
      const { name, email, bio, avatar_url, social_links } = response.data;
      setName(name || '');
      setEmail(email || '');
      setBio(bio || '');
      console.log('Avatar URL received:', avatar_url); // Debug log
      setPreviewImage(avatar_url || null);
      setSocialLinks(social_links || '');
      setError('');
    } catch (err) {
      setError(err.response?.status === 401 ? 'Session expired. Please log in again.' : 'Failed to load profile');
      console.error('Fetch error:', err);
    }
  };

  // Fetch profile on mount
  useEffect(() => {
    fetchProfile();
  }, []);

  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      const imageUrl = URL.createObjectURL(file);
      setPreviewImage(imageUrl);
      setAvatarFile(file);
    }
  };

  const handleImageError = () => {
    console.error('Failed to load image at:', previewImage);
    setPreviewImage(null); // Fallback to default icon
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    setError('');

    const token = localStorage.getItem('access_token');
    if (!token) {
      setError('Please log in to update your profile.');
      return;
    }

    try {
      const formData = new FormData();
      formData.append('name', name || '');
      formData.append('bio', bio || '');
      formData.append('social_links', socialLinks || '');
      if (avatarFile) {
        formData.append('avatar', avatarFile);
      }

      const response = await axios.patch('http://localhost:5000/profiles/me', formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data',
        },
      });

      setMessage(response.data.message || 'Profile updated successfully');
      await fetchProfile();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to update profile');
      console.error('Update error:', err);
    }
  };

  return (
    <div className="profile-page">
      <Navbar />
      <div className="head-content">
        <h2>Profile</h2>
      </div>
      <div style={{ backgroundColor: '#ffffff', minHeight: '100vh', padding: '1rem', color: '#FFF' }}>
        <div className="profile-container">
          <h3>Edit your profile, info, etc</h3>
          <div className="profile-image-section">
            <div className="profile-image">
              {previewImage ? (
                <img
                  src={previewImage}
                  alt="Profile"
                  style={{ width: '150px', height: '150px' }}
                  onError={handleImageError}
                />
              ) : (
                <FaUserAlt className="img" style={{ fontSize: '100px', color: '#ececec', width: '150px', height: '150px' }} />
              )}
            </div>
            <label htmlFor="photo-upload" className="upload-btn">
              <FaCamera /> Upload Photo
              <input id="photo-upload" type="file" style={{ display: 'none' }} onChange={handleImageUpload} />
            </label>
          </div>
          <form onSubmit={handleSubmit} className="form-section">
            <FormInput
              placeholder="Full Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
            <FormInput
              placeholder="Email Address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled
            />
            <FormInput
              placeholder="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <FormInput
              placeholder="Bio"
              value={bio}
              onChange={(e) => setBio(e.target.value)}
            />
            <FormInput
              placeholder="Social Links"
              value={socialLinks}
              onChange={(e) => setSocialLinks(e.target.value)}
            />
            {message && <p style={{ color: 'green', textAlign: 'center' }}>{message}</p>}
            {error && <p style={{ color: 'red', textAlign: 'center' }}>{error}</p>}
            <p style={{ color: '#F8510B', margin: '1rem 0', fontSize: '1rem', textAlign: 'center' }}>
              Please note that to delete your account will be checked with our admin
            </p>
            <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem', justifyContent: 'center' }}>
              <button type="button" className="btn-profile" style={{ backgroundColor: '#ffffff', color: '#11203a', border: '1px solid #11203a', padding: '0.8rem 1.3rem', borderRadius: '7px', fontSize: '15px' }}>
                Cancel
              </button>
              <button type="submit" className="btn-profile" style={{ backgroundColor: '#11203a', color: '#FFF', border: '1px solid #11203a', padding: '0.8rem 1.3rem', borderRadius: '7px', fontSize: '15px' }}>
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

export default Profile;