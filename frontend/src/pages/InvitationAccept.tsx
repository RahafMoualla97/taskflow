import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import apiClient from '../api/client';
import toast from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';

interface InvitationData {
  valid: boolean;
  email: string;
  project_id: number;
  project_name?: string;
  task_id?: number;
  expires_at: string;
  inviter_name?: string;
}

const InvitationAccept = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { user, loading: authLoading } = useAuth();
  
  const [loading, setLoading] = useState(true);
  const [invitation, setInvitation] = useState<InvitationData | null>(null);
  const [error, setError] = useState('');
  const [accepting, setAccepting] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const urlToken = params.get('token');
    const authToken = params.get('auth_token');
    
    if (authToken) {
      localStorage.setItem('token', authToken);
      
      const newParams = new URLSearchParams(window.location.search);
      newParams.delete('auth_token');
      const newUrl = window.location.pathname + '?' + newParams.toString();
      window.location.href = newUrl;
      return;
    }
    
    if (!urlToken) {
      setError('Invalid invitation link. No token provided.');
      setLoading(false);
      return;
    }

    apiClient.get(`/invitations/check?token=${urlToken}`)
      .then(res => {
        setInvitation(res.data);
        setLoading(false);
      })
      .catch(err => {
        const errorMsg = err.response?.data?.detail || 'Invalid or expired invitation';
        setError(errorMsg);
        setLoading(false);
      });
  }, [searchParams]);

  useEffect(() => {
    if (user && invitation && !loading && !accepting) {
      handleAccept();
    }
  }, [user, invitation, loading]);

  const handleAccept = async () => {
    if (accepting) return;
    setAccepting(true);
    
    try {
      const urlToken = new URLSearchParams(window.location.search).get('token');
      
      const response = await apiClient.post(`/invitations/accept?token=${urlToken}`);
      
      toast.success('🎉 Invitation accepted successfully!');
      
      const projectId = response.data?.project_id || invitation?.project_id;
      if (projectId) {
        window.location.href = `/projects/${projectId}`;
      } else {
        window.location.href = '/';
      }
      
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || 'Failed to accept invitation';
      toast.error(errorMsg);
      setError(errorMsg);
      setAccepting(false);
    }
  };

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
        <div className="bg-white p-8 rounded-lg shadow max-w-md w-full text-center">
          <div className="text-red-500 text-5xl mb-4">❌</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Invitation Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          {user && (
            <button
              onClick={() => {
                localStorage.removeItem('token');
                window.location.reload();
              }}
              className="text-blue-600 hover:underline"
            >
              Log out and try again
            </button>
          )}
          <div className="mt-4">
            <Link to="/" className="text-blue-600 hover:underline">
              Go to Dashboard
            </Link>
          </div>
        </div>
      </div>
    );
  }

  if (loading || authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    const urlToken = new URLSearchParams(window.location.search).get('token');
    
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
        <div className="bg-white p-8 rounded-lg shadow max-w-md w-full">
          <div className="text-center mb-6">
            <div className="text-4xl mb-2">📧</div>
            <h2 className="text-2xl font-bold text-gray-800">You're Invited!</h2>
            <p className="text-gray-600 mt-1">Join "{invitation?.project_name || 'a project'}" on TaskFlow</p>
          </div>

          <div className="bg-gray-50 p-4 rounded-lg mb-6">
            <p className="text-sm text-gray-500">Invitation for:</p>
            <p className="font-medium text-gray-800">{invitation?.email}</p>
            {invitation?.inviter_name && (
              <>
                <p className="text-sm text-gray-500 mt-2">Invited by:</p>
                <p className="font-medium text-blue-800">{invitation.inviter_name}</p>
              </>
            )}
          </div>

          <p className="text-sm text-gray-600 text-center mb-4">
            To accept this invitation, please create an account or sign in.
          </p>

          <div className="space-y-3">
            <button
              onClick={() => {
                const currentPath = `/invitations/accept?token=${urlToken}`;
                navigate(`/register?return_url=${encodeURIComponent(currentPath)}`);
              }}
              className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition-colors text-lg font-semibold"
            >
              🚀 Create account to accept
            </button>

            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">or</span>
              </div>
            </div>

            <button
              onClick={() => {
                const currentPath = `/invitations/accept?token=${urlToken}`;
                navigate(`/login?return_url=${encodeURIComponent(currentPath)}`);
              }}
              className="w-full border border-gray-300 text-gray-700 py-3 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Already have an account? Sign in
            </button>
          </div>

          <p className="text-xs text-gray-400 text-center mt-6">
            This invitation will expire on {invitation?.expires_at ? new Date(invitation.expires_at).toLocaleDateString() : 'N/A'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
      <div className="bg-white p-8 rounded-lg shadow max-w-md w-full text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Accepting invitation...</p>
      </div>
    </div>
  );
};

export default InvitationAccept;