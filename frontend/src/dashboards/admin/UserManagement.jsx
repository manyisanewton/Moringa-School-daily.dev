import React, {useState, useEffect} from 'react';
import {FaSearch} from 'react-icons/fa';
import {useNavigate} from 'react-router-dom';
import api from '../../utils/api';
import './UserManagement.css';
import AdminNavbar from '../../components/Navbar/AdminNavbar';
import Footer from '../../components/Footer';
const SkeletonUserRow = () => (
  <div className="skeleton-user-row">
    <div className="skeleton skeleton-name" />
    <div className="skeleton skeleton-email" />
    <div className="skeleton skeleton-role" />
    <div className="skeleton skeleton-actions" />
  </div>
);
const AdminUsers = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [newUser, setNewUser] = useState({
    name: '',
    email: '',
    role: 'User',
    password: '',
  });
  const [showForm, setShowForm] = useState(false);
  const [editUserId, setEditUserId] = useState(null);
  const navigate = useNavigate();
  const loadUsers = async () => {
    try {
      const res = await api.get('/admin/users');
      setUsers(res.data);
    } catch (err) {
      console.error(err);
      alert('Could not load users');
    } finally {
      setLoading(false);
    }
  };
  useEffect(() => {
    loadUsers();
  }, []);
  const handleSubmit = async () => {
    try {
      if (editUserId) {
        await api.post(`/admin/users/${editUserId}/promote/${newUser.role}`);
        alert('Role updated');
      } else {
        const payload = {
          email: newUser.email,
          password: newUser.password,
          roles: [newUser.role],
          name: newUser.name,
        };
        await api.post('/admin/users', payload);
        alert('User created');
      }
      setShowForm(false);
      setEditUserId(null);
      setNewUser({ name: '', email: '', role: 'User', password: '' });
      loadUsers();
    } catch (err) {
      console.error(err);
      const msg = err.response?.data.error || JSON.stringify(err.response?.data?.errors) || 'Save failed';
      alert(msg);
    }
  };
  const handleDeactivate = async (id) => {
    if (!window.confirm('Deactivate this user?')) return;
    try {
      await api.post(`/admin/users/${id}/deactivate`);
      alert('User deactivated');
      loadUsers();
    } catch (err) {
      console.error(err);
      alert('Deactivate failed');
    }
  };
  const handleActivate = async (id) => {
    if (!window.confirm('Reactivate this user?')) return;
    try {
      await api.post(`/admin/users/${id}/activate`);
      alert('User reactivated');
      loadUsers();
    } catch (err) {
      console.error(err);
      alert('Activate failed');
    }
  };
  const filtered = users.filter(u =>
    u.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    u.email.toLowerCase().includes(searchTerm.toLowerCase())
  );
  return (
    <div className="admin-users-wrapper">
      <AdminNavbar />
      <header className="user-header">
        <h1>User Management</h1>
        <p>You have the ability to manage the various users of your system</p>
        <button onClick={() => setShowForm(true)}>+ Add User</button>
      </header>
      {showForm && (
        <div className="add-user-form">
          <h3>{editUserId ? 'Edit User Role' : 'Add New User'}</h3>
          <input
            type="text"
            placeholder="Full Name"
            value={newUser.name}
            onChange={e => setNewUser({ ...newUser, name: e.target.value })}
          />
          <input
            type="email"
            placeholder="Email Address"
            value={newUser.email}
            onChange={e => setNewUser({ ...newUser, email: e.target.value })}
          />
          {!editUserId && (
            <input
              type="password"
              placeholder="Password"
              value={newUser.password}
              onChange={e => setNewUser({ ...newUser, password: e.target.value })}
            />
          )}
          <select
            value={newUser.role}
            onChange={e => setNewUser({ ...newUser, role: e.target.value })}
          >
            <option value="User">User</option>
            <option value="TechWriter">Tech Writer</option>
            <option value="Admin">Admin</option>
          </select>
          <div className="form-actions">
            <button onClick={() => {
              setShowForm(false);
              setEditUserId(null);
              setNewUser({ name: '', email: '', role: 'User', password: '' });
            }}>Cancel</button>
            <button onClick={handleSubmit}>
              {editUserId ? 'Update Role' : 'Create User'}
            </button>
          </div>
        </div>
      )}
      <div className="search-bar-admin">
        <FaSearch className="search-icon" />
        <input
          type="text"
          placeholder="Search for Users"
          value={searchTerm}
          onChange={e => setSearchTerm(e.target.value)}
        />
      </div>
      <div className="users-table">
        <div className="table-header">
          <span>Name</span>
          <span>Email</span>
          <span>Role</span>
          <span>Actions</span>
        </div>
        {loading
          ? Array(4).fill().map((_, i) => <SkeletonUserRow key={i} />)
          : filtered.map(user => (
              <div key={user.id} className="user-row">
                <span>{user.name}</span>
                <span>{user.email}</span>
                <span>{user.roles?.join(', ') || user.role}</span>
                <div className="actions">
                  <button
                    onClick={() => {
                      setEditUserId(user.id);
                      setNewUser({ name: user.name, email: user.email, role: user.roles?.[0] || 'User', password: '' });
                      setShowForm(true);
                    }}
                  >
                    Edit Role
                  </button>
                  {user.is_active
                    ? <button onClick={() => handleDeactivate(user.id)}>Deactivate</button>
                    : <button onClick={() => handleActivate(user.id)}>Activate</button>}
                </div>
              </div>
            ))
        }
      </div>
      <Footer />
    </div>
  );
};
export default AdminUsers;