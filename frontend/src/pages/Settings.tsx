import { useState } from 'react';
import apiClient from '../api/client';
import toast from 'react-hot-toast';

const Settings = () => {
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);

  /**
   * Calculate password strength score
   */
  const getPasswordStrength = (pass: string) => {
    let score = 0;
    if (pass.length >= 8) score++;
    if (/[A-Z]/.test(pass)) score++;
    if (/[a-z]/.test(pass)) score++;
    if (/[0-9]/.test(pass)) score++;
    if (/[^A-Za-z0-9]/.test(pass)) score++;
    return score;
  };

  /**
   * Get color based on password strength
   */
  const getStrengthColor = (score: number) => {
    if (score <= 2) return 'bg-red-500';
    if (score === 3) return 'bg-yellow-500';
    if (score === 4) return 'bg-blue-500';
    return 'bg-green-500';
  };

  /**
   * Get text label based on password strength
   */
  const getStrengthText = (score: number) => {
    if (score <= 2) return 'Weak';
    if (score === 3) return 'Fair';
    if (score === 4) return 'Good';
    return 'Strong';
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate password match
    if (newPassword !== confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    // Validate minimum length
    if (newPassword.length < 8) {
      toast.error('Password must be at least 8 characters');
      return;
    }

    // Validate uppercase letter
    if (!/[A-Z]/.test(newPassword)) {
      toast.error('Password must contain at least one uppercase letter');
      return;
    }

    // Validate lowercase letter
    if (!/[a-z]/.test(newPassword)) {
      toast.error('Password must contain at least one lowercase letter');
      return;
    }

    // Validate number
    if (!/[0-9]/.test(newPassword)) {
      toast.error('Password must contain at least one number');
      return;
    }

    // Validate special character
    if (!/[^A-Za-z0-9]/.test(newPassword)) {
      toast.error('Password must contain at least one special character');
      return;
    }

    setLoading(true);
    try {
      await apiClient.post('/auth/change-password', {
        current_password: currentPassword,
        new_password: newPassword,
      });
      toast.success('Password changed successfully!');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to change password');
    } finally {
      setLoading(false);
    }
  };

  const passwordScore = getPasswordStrength(newPassword);

  return (
    <div className="bg-white rounded-lg shadow p-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">⚙️ Settings</h1>
      
      <div className="max-w-md">
        <h2 className="text-lg font-semibold mb-3">🔑 Change Password</h2>
        <form onSubmit={handleChangePassword} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Current Password
            </label>
            <input
              type="password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
              placeholder="Enter current password"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              New Password
            </label>
            <input
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
              placeholder="Enter new password (min 8 chars)"
            />
          </div>

          {/* Password Strength Indicator */}
          {newPassword && (
            <div>
              <div className="flex items-center gap-2 mb-1">
                <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div 
                    className={`h-full transition-all duration-300 ${getStrengthColor(passwordScore)}`}
                    style={{ width: `${(passwordScore / 5) * 100}%` }}
                  />
                </div>
                <span className={`text-xs font-medium ${
                  passwordScore <= 2 ? 'text-red-500' :
                  passwordScore === 3 ? 'text-yellow-500' :
                  passwordScore === 4 ? 'text-blue-500' :
                  'text-green-500'
                }`}>
                  {getStrengthText(passwordScore)}
                </span>
              </div>
              <p className="text-xs text-gray-500">
                Requirements: 8+ characters, uppercase, lowercase, number, special character
              </p>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Confirm New Password
            </label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
              placeholder="Confirm new password"
            />
            {confirmPassword && newPassword !== confirmPassword && (
              <p className="text-xs text-red-500 mt-1">Passwords do not match</p>
            )}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center gap-2"
          >
            {loading ? (
              <>
                <span className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
                Changing...
              </>
            ) : (
              'Change Password'
            )}
          </button>
        </form>

        <div className="mt-6 pt-6 border-t border-gray-200">
          <p className="text-xs text-gray-400">
            For security, your password must be at least 8 characters and include uppercase, lowercase, number, and special character.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Settings;