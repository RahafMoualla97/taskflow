import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

const AuthCallback = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get('token');
    const authToken = params.get('auth_token');
    
    const finalToken = token || authToken;

    if (finalToken) {
      localStorage.setItem('token', finalToken);
      
      const redirectUrl = localStorage.getItem('redirectAfterLogin');
      
      if (redirectUrl) {
        localStorage.removeItem('redirectAfterLogin');
        window.location.href = redirectUrl;
      } else {
        window.location.href = '/';
      }
    } else {
      toast.error('Authentication failed');
      navigate('/login');
    }
  }, [navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Logging you in...</p>
      </div>
    </div>
  );
};

export default AuthCallback;