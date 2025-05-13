import React from 'react';

const ContentTable = ({ contents }) => {
  return (
    <table className="content-table">
      <thead>
        <tr>
          <th>Type</th>
          <th>Title</th>
          <th>Status</th>
          <th>Created At</th>
        </tr>
      </thead>
      <tbody>
        {contents.length > 0 ? (
          contents.map(item => (
            <tr key={item.id}>
              <td>{item.content_type}</td>
              <td>{item.title}</td>
              <td>{item.status}</td>
              <td>{new Date(item.created_at).toLocaleDateString()}</td>
            </tr>
          ))
        ) : (
          <tr>
            <td colSpan="4">No content found.</td>
          </tr>
        )}
      </tbody>
    </table>
  );
};

export default ContentTable;