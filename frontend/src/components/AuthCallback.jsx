import { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { getUserProfile } from '../api';

function AuthCallback() {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const access_token = params.get('access_token');
    const refresh_token = params.get('refresh_token');
    const role = params.get('role');
    const redirect_url = params.get('redirect_url');
    const error = params.get('error');

    if (error) {
      navigate('/login', { state: { error } });
      return;
    }

    if (access_token && refresh_token && role && redirect_url) {
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      localStorage.setItem('user_role', role);
      getUserProfile().then((profileResponse) => {
        localStorage.setItem('user_id', profileResponse.data.id);
        navigate(redirect_url);
      }).catch(() => {
        navigate('/login', { state: { error: 'Failed to fetch user profile' } });
      });
    } else {
      navigate('/login', { state: { error: 'Authentication failed' } });
    }
  }, [navigate, location]);

  return <div>Loading...</div>;
}

export default AuthCallback;