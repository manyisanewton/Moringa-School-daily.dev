import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

function AuthCallback() {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const accessToken = params.get('access_token');
    const refreshToken = params.get('refresh_token');
    const error = params.get('error');

    if (error) {
      navigate('/login', { state: { error: error || 'OAuth login failed' } });
      return;
    }

    if (accessToken && refreshToken) {
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('refresh_token', refreshToken);
      navigate('/home');
    } else {
      navigate('/login', { state: { error: 'OAuth login failed: No tokens received' } });
    }
  }, [navigate, location]);

  return <div>Processing authentication...</div>;
}

export default AuthCallback;