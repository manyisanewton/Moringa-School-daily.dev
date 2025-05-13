import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../utils/api';
import './AdminProfile.css';
import AdminNavbar from '../../components/Navbar/AdminNavbar';
import Footer from '../../components/Footer';
const AdminProfile = () => {
  const [user, setUser] = useState({ email: '' });
  const [profile, setProfile] = useState({
    name: '',
    bio: '',
    avatar_url: '',
    social_links: '',
  });
  const [photoFile, setPhotoFile] = useState(null);
  const navigate = useNavigate();
  useEffect(() => {
    const load = async () => {
      try {
        const me = await api.get('/auth/me');
        setUser({ email: me.data.email });
        const p = await api.get('/profiles/me');
        setProfile({
          name: p.data.name || '',
          bio: p.data.bio || '',
          avatar_url: p.data.avatar_url || '',
          social_links: p.data.social_links || '',
        });
      } catch (err) {
        console.error(err);
        alert('Could not load profile');
      }
    };
    load();
  }, []);
  const handlePhotoChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setPhotoFile(file);
    setProfile(p => ({
      ...p,
      avatar_url: URL.createObjectURL(file),
    }));
  };

  const handleSave = async () => {
    try {
      let avatar_url = profile.avatar_url;
      if (photoFile) {
        const form = new FormData();
        form.append('file', photoFile);
        const upload = await api.post('/upload', form, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        avatar_url = upload.data.url;
      }

      const payload = {
        name: profile.name,
        bio: profile.bio,
        avatar_url,
        social_links: profile.social_links,
      };
      await api.patch('/profiles/me', payload);

      alert('Profile updated successfully!');
      if (photoFile) URL.revokeObjectURL(profile.avatar_url);
      navigate('/admin/dashboard');
    } catch (err) {
      console.error(err);
      alert('Update failed');
    }
  };
  return (
    <div className="admin-settings-wrapper">
      <AdminNavbar />

      <div className="profile-header">
        <h1>Profile</h1>
        <p>Edit your profile information</p>
      </div>

      <div className="profile-form">
        <div className="profile-photo-section">
          <div className="photo-preview">
            {profile.avatar_url
              ? <img src={profile.avatar_url} alt="Profile" className="profile-photo" />
              : <div className="photo-placeholder">No Photo</div>}
          </div>
          <label htmlFor="photo-upload" className="upload-btn">Upload Photo</label>
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
          onChange={e => setProfile(p => ({ ...p, name: e.target.value }))}
          placeholder="Full Name"
        />

        <label>Bio:</label>
        <textarea
          value={profile.bio}
          onChange={e => setProfile(p => ({ ...p, bio: e.target.value }))}
          placeholder="A short bio"
        />

        <label>Website / Social:</label>
        <input
          type="text"
          value={profile.social_links}
          onChange={e => setProfile(p => ({ ...p, social_links: e.target.value }))}
          placeholder="http://..."
        />

        <label>Email (read-only):</label>
        <input type="email" value={user.email} readOnly />

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