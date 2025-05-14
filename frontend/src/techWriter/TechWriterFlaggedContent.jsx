import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Swal from 'sweetalert2';
import { FaEdit, FaTrash } from 'react-icons/fa';
import TechNavbar from '../components/Navbar/TechNavbar';
import Footer from '../components/Footer';
import './TechWriterFlaggedContent.css';
import TechWriterNotifications from '../components/TechWriterNotifications';

const SkeletonFlaggedRow = () => (
  <div className="skeleton-flagged-row">
    <div className="skeleton skeleton-type"></div>
    <div className="skeleton skeleton-title"></div>
    <div className="skeleton skeleton-reason"></div>
    <div className="skeleton skeleton-actions"></div>
  </div>
);

const TechWriterFlaggedContent = () => {
  const [flaggedContent, setFlaggedContent] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchFlaggedContent = async () => {
      try {
        const response = await axios.get('http://localhost:5000/content/flagged', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`
          }
        });
        setFlaggedContent(response.data.items);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching flagged content:', error);
        setLoading(false);
      }
    };
    fetchFlaggedContent();
  }, []);

  const handleDeleteContent = async (id, title) => {
    Swal.fire({
      title: 'Are you sure?',
      text: `You are about to delete "${title}". This action cannot be undone.`,
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#F8510B',
      cancelButtonColor: '#666',
      confirmButtonText: 'Yes, delete it!',
    }).then(async (result) => {
      if (result.isConfirmed) {
        try {
          await axios.delete(`http://localhost:5000/content/${id}`, {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('access_token')}`
            }
          });
          setFlaggedContent(flaggedContent.filter(item => item.id !== id));
          Swal.fire('Deleted!', 'Your flagged content has been deleted.', 'success');
        } catch (error) {
          console.error('Error deleting content:', error);
          Swal.fire('Error', 'Failed to delete content.', 'error');
        }
      }
    });
  };

  return (
    <div>
        <TechNavbar />
      <div className="techwriter-content">
        <TechWriterNotifications />
        <div className='techwriter-label-flagged'>
          <h1>Flagged Content</h1>
          <p>Review and take action on content that’s been flagged by users or other writers</p>
        </div>
        <div className="flagged-content">
          <table className='flagged-table'>
            <thead className='flagged-table-head'>
              <tr>
                <th>Type</th>
                <th>Title</th>
                <th>Flag Reason</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                Array(3).fill().map((_, index) => (
                  <tr key={index}>
                    <td colSpan="4">
                      <SkeletonFlaggedRow />
                    </td>
                  </tr>
                ))
              ) : flaggedContent.length > 0 ? (
                flaggedContent.map(item => (
                  <tr key={item.id}>
                    <td>{item.type}</td>
                    <td>{item.title}</td>
                    <td>{item.reason}</td>
                    <td className='actions'>
                      <button className='edit-btn' onClick={() => navigate(`/techwriter/edit/${item.id}`)}><FaEdit /> Edit</button>
                      <button className='del-btn' onClick={() => handleDeleteContent(item.id, item.title)}><FaTrash /> Delete</button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="4" className="no-content">
                    <p>No flagged content found.</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default TechWriterFlaggedContent;