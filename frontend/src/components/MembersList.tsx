import { useState, useEffect } from 'react';
import apiClient from '../api/client';
import toast from 'react-hot-toast';

interface Member {
  user_id: number;
  user_name: string;
  user_email: string;
  role: string;
  joined_at: string;
}

const MembersList = ({ projectId }: { projectId: number }) => {
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);
  const [showInviteForm, setShowInviteForm] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState('Member');
  const [isSending, setIsSending] = useState(false);

  useEffect(() => {
    fetchMembers();
  }, [projectId]);

  const fetchMembers = async () => {
    try {
      const response = await apiClient.get(`/projects/${projectId}/members`);
      setMembers(response.data);
    } catch (error: any) {
      toast.error('Failed to load members');
    } finally {
      setLoading(false);
    }
  };

  const sendInvitation = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inviteEmail) {
      toast.error('Please enter an email address');
      return;
    }

    setIsSending(true);

    try {
      const response = await apiClient.post('/invitations/', {
        email: inviteEmail,
        project_id: projectId,
        role: inviteRole,
      });
      
      toast.success(`Invitation sent to ${inviteEmail}`);
      setInviteEmail('');
      setShowInviteForm(false);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to send invitation');
    } finally {
      setIsSending(false);
    }
  };

  const removeMember = async (userId: number) => {
    if (!window.confirm('Are you sure you want to remove this member?')) return;
    try {
      await apiClient.delete(`/projects/${projectId}/members/${userId}`);
      toast.success('Member removed!');
      fetchMembers();
    } catch (error: any) {
      toast.error('Failed to remove member');
    }
  };

  if (loading) {
    return <div className="text-center py-4">Loading members...</div>;
  }

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Members</h3>
        <button
          onClick={() => setShowInviteForm(!showInviteForm)}
          className="text-sm bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700"
        >
          {showInviteForm ? 'Cancel' : '+ Invite Member'}
        </button>
      </div>

      {showInviteForm && (
        <form onSubmit={sendInvitation} className="mb-4 p-3 bg-gray-50 rounded">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
            <input
              type="email"
              placeholder="Email"
              value={inviteEmail}
              onChange={(e) => setInviteEmail(e.target.value)}
              className="px-3 py-1 border rounded"
              required
              disabled={isSending}
            />
            <select
              value={inviteRole}
              onChange={(e) => setInviteRole(e.target.value)}
              className="px-3 py-1 border rounded"
              disabled={isSending}
            >
              <option value="Member">Member</option>
              <option value="Admin">Admin</option>
              <option value="Viewer">Viewer</option>
            </select>
            <button
              type="submit"
              disabled={isSending}
              className={`px-3 py-1 rounded text-white transition-colors ${
                isSending 
                  ? 'bg-gray-400 cursor-not-allowed' 
                  : 'bg-green-600 hover:bg-green-700'
              }`}
            >
              {isSending ? 'Sending...' : 'Send Invite'}
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            The invitation will expire in <strong>7 days</strong>.
          </p>
        </form>
      )}

      <div className="space-y-2">
        {members.map((member) => (
          <div key={member.user_id} className="flex justify-between items-center p-2 border-b">
            <div>
              <p className="font-medium">{member.user_name}</p>
              <p className="text-sm text-gray-500">{member.user_email}</p>
              <span className="text-xs px-2 py-0.5 bg-gray-200 rounded-full">
                {member.role}
              </span>
            </div>
            <button
              onClick={() => removeMember(member.user_id)}
              className="text-red-500 hover:text-red-700 text-sm"
            >
              ✕
            </button>
          </div>
        ))}
        {members.length === 0 && (
          <p className="text-gray-500 text-sm py-4 text-center">No members yet</p>
        )}
      </div>
    </div>
  );
};

export default MembersList;