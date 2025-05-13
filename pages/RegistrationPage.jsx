import './RegistrationPage.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faEye, faEyeSlash } from '@fortawesome/free-solid-svg-icons';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { register, getUserProfile } from '../api';

function RegisterPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [role, setRole] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    if (!role) {
      setError('Please select a role');
      return;
    }
    try {
      const { data } = await register(name, email, phone, role, password);
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      localStorage.setItem('user_role', data.role);
      const profileResponse = await getUserProfile();
      localStorage.setItem('user_id', profileResponse.data.id);
      switch (data.role) {
        case 'Admin':
          navigate('/adminsdashboard');
          break;
        case 'TechWriter':
          navigate('/techwriterdashboard');
          break;
        case 'User':
          navigate('/usersdashboard');
          break;
        default:
          setError('Unknown role');
      }
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.response?.data?.message || 'Registration failed';
      if (err.response?.status === 409 && err.response?.data?.suggestion === 'login') {
        setError('Email already registered. Please log in or use a different email.');
        setTimeout(() => navigate('/login'), 3000);
      } else {
        setError(errorMessage);
      }
    }
  };
  const redirectToLogin = () => {
    navigate('/login');
  };

  const handleOAuthLogin = (provider) => {
    window.location.href = `http://localhost:5000/auth/login/${provider}`;
  };

  return (
    <div className='register-container'>
      <div className='left-panel'>
        <h1>Welcome Back to Moringa School daily.dev</h1>
        <p>Dive back into the world of verified tech insights, stories, and inspirations from your community. Log in to explore, learn, and grow</p>
        <button className='login-btn' onClick={redirectToLogin}>Log In</button>
      </div>
      <div className='right-panel'>
        <div className='form-card'>
          <h2>Register</h2>
          {error && <p className='error'>{error.toString()}</p>}
          <form onSubmit={handleSubmit}>
            <label>Full Name:</label>
            <input
              type="text"
              placeholder='Full Name'
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
            <label>Email:</label>
            <input
              type="email"
              placeholder='Email'
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <label>Phone:</label>
            <input
              type="tel"
              placeholder='Phone'
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
            />
            <label>Role:</label>
            <select value={role} onChange={(e) => setRole(e.target.value)} required>
              <option value="" disabled>Select your Role</option>
              <option value="Admin">Admin</option>
              <option value="TechWriter">Tech Writer</option>
              <option value="User">User</option>
            </select>
            <label>Password:</label>
            <div className='password-wrapper'>
              <input
                type={showPassword ? 'text' : 'password'}
                placeholder='Password'
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <FontAwesomeIcon
                icon={showPassword ? faEyeSlash : faEye}
                className='eye-icon'
                onClick={() => setShowPassword(!showPassword)}
              />
            </div>
            <label>Confirm Password:</label>
            <div className='password-wrapper'>
              <input
                type={showPassword ? 'text' : 'password'}
                placeholder='Confirm Password'
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
              />
              <FontAwesomeIcon
                icon={showConfirmPassword ? faEyeSlash : faEye}
                className='eye-icon'
                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              />
            </div>
            <button className='register-btn' type='submit'>Register</button>
            <div className='divider'>or register with</div>
            <div className='social-login'>
              <button
                type="button"
                className='social-btn google'
                onClick={() => handleOAuthLogin('google')}
              >
                <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/google/google-original.svg" alt="Google" className='icon'/>
              </button>
              <button
                type="button"
                className='social-btn github'
                onClick={() => handleOAuthLogin('github')}
              >
                <img src='https://cdn.jsdelivr.net/gh/devicons/devicon/icons/github/github-original.svg' alt='Github' className='icon' />
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default RegisterPage;