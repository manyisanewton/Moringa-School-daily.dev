import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './AdminProfile.css';
import AdminNavbar from '../components/Navbar/AdminNavbar';
import Footer from '../components/Footer';

const AdminProfile = () => {
  const [profile, setProfile] = useState({
    name: 'Admin User',
    email: 'admin@example.com',
    password: '',
    phone: '',
    photo: null, // Store the profile photo URL or File object
  });
  const navigate = useNavigate();

  const handlePhotoChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const photoURL = URL.createObjectURL(file); // Create a temporary URL for preview
      setProfile({ ...profile, photo: photoURL });
    }
  };

  const handleSave = () => {
    // In a real app, save to backend, including uploading the photo file
    alert('Profile updated successfully!');
    if (profile.photo) {
      // Clean up the temporary URL to avoid memory leaks
      URL.revokeObjectURL(profile.photo);
    }
  };

  return (
    <div className="admin-settings-wrapper">
      <div>
        <AdminNavbar />
      </div>
      <div className='profile-header'>
        <h1>Profile</h1>
        <p>Edit your profile, name, etc</p>
     </div>
        <div className="profile-form">
          <div className="profile-photo-section">
            <div className="photo-preview">
              {profile.photo ? (
                <img src={profile.photo} alt="Profile Preview" className="profile-photo" />
              ) : (
                <div className="photo-placeholder">No Photo</div>
              )}
            </div>
            <label id='upload' htmlFor="photo-upload" className="upload-btn">
              Upload Photo
            </label>
            <input
              id="photo-upload"
              type="file"
              accept="image/*"
              onChange={handlePhotoChange}
              style={{ display: 'none' }}
            />
          </div>
          <label>Your Name:</label>
          <input
            type="text"
            value={profile.name}
            onChange={(e) => setProfile({ ...profile, name: e.target.value })}
            placeholder="Full Name"
          />
          <label>Email Address:</label>
          <input
            type="email"
            value={profile.email}
            onChange={(e) => setProfile({ ...profile, email: e.target.value })}
            placeholder="Email"
          />
          <label>Password:</label>
          <input
            type="password"
            value={profile.password}
            onChange={(e) => setProfile({ ...profile, password: e.target.value })}
            placeholder="Password"
          />
        
     
          <button className="update-btn">Update Profile</button>
          <p className="delete-note">Delete your account<br />Please note that all albums you have created will be permanently erased</p>
          <div className="form-actions">
            <button onClick={() => navigate('/admin/dashboard')}>Cancel</button>
            <button onClick={handleSave}>Save</button>
          </div>
        </div>
      <Footer />
    </div>
  );
};

export default AdminProfile;