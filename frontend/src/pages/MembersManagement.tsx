import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import apiClient from '../api/client';
import toast from 'react-hot-toast';
import { UserPlusIcon, TrashIcon } from '@heroicons/react/24/outline';

interface Member {
  user_id: number;
  user_name: string;
  user_email: string;
  role: string;
  joined_at: string;
}

interface User {
  id: number;
  name: string;
  email: string;
}

const MembersManagement = () => {
  const { id } = useParams<{ id: string }>();
  const [members, setMembers] = useState<Member[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState('');
  const [selectedRole, setSelectedRole] = useState('Member');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchMembers();
    fetchUsers();
  }, [id]);

  const fetchMembers = async () => {
    try {
      const res = await apiClient.get(`/projects/${id}/members`);
      setMembers(res.data);
    } catch (error) {
      toast.error('Failed to load members');
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    try {
      const res = await apiClient.get('/users');
      setUsers(res.data);
    } catch (error) {
      console.error('Failed to load users:', error);
    }
  };

  const addMember = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedUser) {
      toast.error('Please select a user');
      return;
    }

    try {
      await apiClient.post(`/projects/${id}/members`, {
        user_id: parseInt(selectedUser),
        role: selectedRole,
      });
      toast.success('Member added successfully!');
      setShowAddModal(false);
      setSelectedUser('');
      setSelectedRole('Member');
      fetchMembers();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to add member');
    }
  };

  const removeMember = async (userId: number) => {
    if (!window.confirm('Are you sure you want to remove this member?')) return;
    try {
      await apiClient.delete(`/projects/${id}/members/${userId}`);
      toast.success('Member removed successfully!');
      fetchMembers();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to remove member');
    }
  };

  const updateRole = async (userId: number, newRole: string) => {
    try {
      await apiClient.put(`/projects/${id}/members/${userId}`, { role: newRole });
      toast.success('Role updated successfully!');
      fetchMembers();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to update role');
    }
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'Owner': return 'bg-purple-100 text-purple-800';
      case 'Admin': return 'bg-blue-100 text-blue-800';
      case 'Member': return 'bg-green-100 text-green-800';
      case 'Viewer': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredUsers = users.filter(u =>
    !members.some(m => m.user_id === u.id) &&
    (u.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
     u.email.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  if (loading) {
    return <div className="text-center py-8">Loading members...</div>;
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">👥 Team Members</h2>
          <p className="text-sm text-gray-500 mt-1">Manage your project team</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
        >
          <UserPlusIcon className="w-5 h-5" />
          Add Member
        </button>
      </div>

      {/* Members Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50 border-b">
            <tr>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Member</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Role</th>
              <th className="text-left py-3 px-4 text-sm font-medium text-gray-600">Joined</th>
              <th className="text-right py-3 px-4 text-sm font-medium text-gray-600">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {members.map((member) => (
              <tr key={member.user_id} className="hover:bg-gray-50 transition-colors">
                <td className="py-3 px-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold">
                      {member.user_name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{member.user_name}</p>
                      <p className="text-sm text-gray-500">{member.user_email}</p>
                    </div>
                  </div>
                </td>
                <td className="py-3 px-4">
                  <select
                    value={member.role}
                    onChange={(e) => updateRole(member.user_id, e.target.value)}
                    className={`px-3 py-1 rounded-full text-sm font-medium border-0 ${getRoleColor(member.role)} focus:outline-none focus:ring-2 focus:ring-blue-500`}
                  >
                    <option value="Owner">Owner</option>
                    <option value="Admin">Admin</option>
                    <option value="Member">Member</option>
                    <option value="Viewer">Viewer</option>
                  </select>
                </td>
                <td className="py-3 px-4 text-sm text-gray-500">
                  {new Date(member.joined_at).toLocaleDateString()}
                </td>
                <td className="py-3 px-4 text-right">
                  {member.role !== 'Owner' && (
                    <button
                      onClick={() => removeMember(member.user_id)}
                      className="text-red-500 hover:text-red-700 transition-colors p-1"
                    >
                      <TrashIcon className="w-5 h-5" />
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Add Member Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Add Team Member</h3>
            
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">Search User</label>
              <input
                type="text"
                placeholder="Search by name or email..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <form onSubmit={addMember}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">Select User</label>
                <select
                  value={selectedUser}
                  onChange={(e) => setSelectedUser(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="">Select a user...</option>
                  {filteredUsers.map((user) => (
                    <option key={user.id} value={user.id}>
                      {user.name} ({user.email})
                    </option>
                  ))}
                </select>
                {filteredUsers.length === 0 && (
                  <p className="text-sm text-gray-500 mt-1">No available users to add</p>
                )}
              </div>

              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
                <select
                  value={selectedRole}
                  onChange={(e) => setSelectedRole(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="Member">Member</option>
                  <option value="Admin">Admin</option>
                  <option value="Viewer">Viewer</option>
                </select>
              </div>

              <div className="flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => {
                    setShowAddModal(false);
                    setSelectedUser('');
                    setSearchTerm('');
                  }}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Add Member
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default MembersManagement;