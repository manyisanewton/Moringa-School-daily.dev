import React from 'react';
import { motion } from "framer-motion";
import { FaEye, FaEyeSlash } from "react-icons/fa";


const NotificationCard = ({ icon, message, subMessage, time, read, onToggleRead, actionLabel, onActionClick }) => {
  return (
    <motion.div
      className={`card ${!read ? 'unread' : ''}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="icon" style={{ marginRight: '1.5rem' }}>{icon}</div>
      <div className="content">
        <p>{message}</p>
        <p style={{ fontSize: '0.9rem', color: '#666' }}>{subMessage}</p>
        <small>{time}</small>

        {/* action button */}
        {actionLabel && (
          <button className="action-btn" onClick={onActionClick}>
            {actionLabel}
          </button>
        )}
      </div>
      {/* <button className="read-btn" onClick={onToggleRead}>
        {read ? <FaEyeSlash style={{ color: '#A3A3A3' }} /> : <FaEye style={{ color: '#F8510B' }} />}
      </button> */}
    </motion.div>
  );
};

export default NotificationCard;