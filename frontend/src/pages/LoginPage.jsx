import './LoginPage.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faEye, faEyeSlash } from '@fortawesome/free-solid-svg-icons';
import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { login, getUserProfile } from '../api';

function LoginPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    if (location.state?.error) {
      setError(location.state.error);
    }
  }, [location]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const { data } = await login(email, password);
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
      setError(err.response?.data?.error || 'Login failed');
    }
  };
  const handleRegisterRedirect = () => {
    navigate('/register');
  };

  const handleOAuthLogin = (provider) => {
    window.location.href = `http://localhost:5000/auth/login/${provider}`;
  };

  return (
    <div className='login-container'>
      <div className='left-panel'>
        <h1>Join Moringa School daily.dev</h1>
        <p>Verified content. Real voices. Your Tech journey starts here!</p>
        <button className='register-btn1' onClick={handleRegisterRedirect}>Register</button>
      </div>
      <div className='right-panel'>
        <div className='form-card'>
          <h2>Log In</h2>
          {error && <p className='error'>{error}</p>}
          <form onSubmit={handleSubmit}>
            <label>Email:</label>
            <input
              type="email"
              placeholder='Email'
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
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
            <button className='login-btn' type='submit'>Log In</button>
            <a href="/forgot-password" className='forgot-password'>Forgot your password?</a>
            <div className='divider'>or log in with</div>
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

export default LoginPage;