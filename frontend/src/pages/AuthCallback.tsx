// frontend/src/pages/AuthCallback.tsx
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

const AuthCallback = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get('token');
    const authToken = params.get('auth_token');  // ✅ أضيفي هذا
    
    console.log('🔑 AuthCallback - Token:', token);
    console.log('🔑 AuthCallback - Auth Token:', authToken);
    
    // ✅ طباعة كل الـ localStorage للتحقق
    console.log('📦 All localStorage items:', { ...localStorage });

    // ✅ استخدمي auth_token إذا كان موجوداً
    const finalToken = token || authToken;

    if (finalToken) {
      // حفظ التوكن
      localStorage.setItem('token', finalToken);
      console.log('✅ Token saved to localStorage');
      
      // ✅ التحقق من وجود redirect بعد تسجيل الدخول
      const redirectUrl = localStorage.getItem('redirectAfterLogin');
      console.log('🔗 Redirect after login:', redirectUrl);
      
      if (redirectUrl) {
        localStorage.removeItem('redirectAfterLogin');
        console.log('✅ Redirecting to:', redirectUrl);
        window.location.href = redirectUrl;
      } else {
        console.log('ℹ️ No redirect URL, going to dashboard');
        window.location.href = '/';
      }
    } else {
      console.error('❌ No token found in URL');
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