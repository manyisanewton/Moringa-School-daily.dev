import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchUsers, addUser, updateUser, deactivateUser, activateUser, addRecentActivity } from '../utils/MockData';
import './UserManagement.css';
import AdminNavbar from '../components/Navbar/AdminNavbar';
import Footer from '../components/Footer';
import { FaSearch } from 'react-icons/fa';

const SkeletonUserRow = () => (
  <div className="skeleton-user-row">
    <div className="skeleton skeleton-name"></div>
    <div className="skeleton skeleton-email"></div>
    <div className="skeleton skeleton-role"></div>
    <div className="skeleton skeleton-actions"></div>
  </div>
);

const AdminUsers = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [newUser, setNewUser] = useState({ name: '', email: '', role: 'User' });
  const [showAddForm, setShowAddForm] = useState(false);
  const [editUserId, setEditUserId] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchUsers().then(data => {
      setUsers(data);
      setLoading(false);
    });
  }, []);

  const handleAddUser = () => {
    if (newUser.name && newUser.email) {
      addUser(newUser);
      addRecentActivity(`New User "${newUser.email}" Created`);
      setUsers([...users, { id: users.length + 1, ...newUser, active: true }]);
      setNewUser({ name: '', email: '', role: 'User' });
      setShowAddForm(false);
    }
  };

  const handleEditUser = (user) => {
    setEditUserId(user.id);
    setNewUser({ name: user.name, email: user.email, role: user.role });
    setShowAddForm(true);
  };

  const handleUpdateUser = () => {
    updateUser(editUserId, newUser);
    setUsers(users.map(user => (user.id === editUserId ? { ...user, ...newUser } : user)));
    setEditUserId(null);
    setNewUser({ name: '', email: '', role: 'User' });
    setShowAddForm(false);
  };

  const handleDeactivateUser = (id) => {
    deactivateUser(id);
    setUsers(users.map(user => (user.id === id ? { ...user, active: false } : user)));
    addRecentActivity(`User "${users.find(u => u.id === id).email}" Deactivated`);
  };

  const handleActivateUser = (id) => {
    activateUser(id);
    setUsers(users.map(user => (user.id === id ? { ...user, active: true } : user)));
    addRecentActivity(`User "${users.find(u => u.id === id).email}" Activated`);
  };

  const filteredUsers = users.filter(user =>
    user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="admin-users-wrapper">
      <div>
        <AdminNavbar />
      </div>
      <div>
        <div className='user-header'>            
            <h1>User Management</h1>
            <p>You have the ability to manage the various users of your system</p>
        </div>
        <div className="search-bar-admin">
          <input
            type="text"
            placeholder="Search for Users"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <FaSearch className="search-icon" />
          {/* <button onClick={() => setShowAddForm(true)}>Add User</button> */}
        </div>
        <div className="add-user-btn">
            <button onClick={() => setShowAddForm(true)}>Add User</button>
        </div>
        {showAddForm && (
          <div className="add-user-form">
            <h3>{editUserId ? 'Edit User' : 'Add New User'}</h3>
            <input
              type="text"
              placeholder="Full Name"
              value={newUser.name}
              onChange={(e) => setNewUser({ ...newUser, name: e.target.value })}
            />
            <input
              type="email"
              placeholder="Email Address"
              value={newUser.email}
              onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
            />
            <select
              value={newUser.role}
              onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
            >
              <option value="User">User</option>
              <option value="Tech Writer">Tech Writer</option>
              <option value="Admin">Admin</option>
            </select>
            <div className="form-actions">
              <button onClick={() => setShowAddForm(false)}>Cancel</button>
              <button onClick={editUserId ? handleUpdateUser : handleAddUser}>
                {editUserId ? 'Update' : 'Add'}
              </button>
            </div>
          </div>
        )}
        <div className="users-table">
          <div className="table-header">
            <span>Name</span>
            <span>Email</span>
            <span>Role</span>
            <span>Actions</span>
          </div>
          {loading ? (
            Array(4).fill().map((_, index) => <SkeletonUserRow key={index} />)
          ) : (
            filteredUsers.map(user => (
              <div key={user.id} className="user-row">
                <span>{user.name}</span>
                <span>{user.email}</span>
                <span>{user.role}</span>
                <div className="actions">
                  <button onClick={() => handleEditUser(user)} disabled={!user.active}>Edit</button>
                  {user.active ? (
                    <button onClick={() => handleDeactivateUser(user.id)}>Deactivate</button>
                  ) : (
                    <button onClick={() => handleActivateUser(user.id)} className="activate-btn">
                      Activate
                    </button>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default AdminUsers;
