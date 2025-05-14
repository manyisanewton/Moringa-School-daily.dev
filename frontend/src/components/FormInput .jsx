import React from 'react';

const FormInput = ({ type = 'text', placeholder, value, onChange }) => {
  return (
    <input
      type={type}
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      style={{
        width: '90%',
        padding: '1rem',
        marginBottom: '1rem',
        border: '1.5px solid #11203A',
        borderRadius: '10px',
        boxShadow: '0 4px 8px rgba(0, 0, 0, 0.1)',
      }}
    />
  );
};

export default FormInput;