import { useState, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import { CameraIcon } from '@heroicons/react/24/outline';

const Profile = () => {
  const { user, updateUser } = useAuth();
  const [name, setName] = useState(user?.name || '');
  const [avatarUrl, setAvatarUrl] = useState(user?.avatar_url || '');
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!name.trim()) {
      toast.error('Name is required');
      return;
    }

    setLoading(true);
    try {
      await updateUser({ 
        name: name.trim(),
        avatar_url: avatarUrl || undefined
      });
      toast.success('Profile updated successfully!');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > 5 * 1024 * 1024) {
      toast.error('Image size must be less than 5MB');
      return;
    }

    if (!file.type.startsWith('image/')) {
      toast.error('Please upload an image file');
      return;
    }

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('image', file);

      const response = await fetch('https://api.imgbb.com/1/upload?key=YOUR_IMGBB_API_KEY', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      
      if (data.success) {
        const imageUrl = data.data.url;
        setAvatarUrl(imageUrl);
        toast.success('Image uploaded successfully!');
      } else {
        throw new Error('Upload failed');
      }
    } catch (error) {
      toast.error('Failed to upload image');
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">👤 Profile</h1>
      
      <div className="flex flex-col items-center gap-4 mb-8">
        <div className="relative">
          <img
            src={avatarUrl || `https://ui-avatars.com/api/?name=${user?.name}&size=128&background=4a90e2&color=fff`}
            alt={user?.name}
            className="w-32 h-32 rounded-full object-cover border-4 border-gray-200"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            className="absolute bottom-0 right-0 bg-blue-600 text-white p-2 rounded-full hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            <CameraIcon className="w-5 h-5" />
          </button>
        </div>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleImageUpload}
          className="hidden"
        />
        {uploading && (
          <p className="text-sm text-gray-500">Uploading image...</p>
        )}
        <p className="text-sm text-gray-500">
          Click the camera icon to change your profile picture
        </p>
      </div>

      <div className="space-y-4 mb-6 p-4 bg-gray-50 rounded-lg">
        <div>
          <p className="text-sm font-medium text-gray-500">Email</p>
          <p className="text-gray-900">{user?.email}</p>
        </div>
        <div>
          <p className="text-sm font-medium text-gray-500">Joined</p>
          <p className="text-gray-900">
            {user?.created_at ? new Date(user.created_at).toLocaleDateString('en-US', {
              year: 'numeric',
              month: 'long',
              day: 'numeric'
            }) : 'N/A'}
          </p>
        </div>
      </div>

      <form onSubmit={handleUpdateProfile} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Full Name *
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Enter your full name"
            required
          />
        </div>

        <div className="flex gap-3 pt-2">
          <button
            type="submit"
            disabled={loading || uploading}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center gap-2"
          >
            {loading ? (
              <>
                <span className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
                Saving...
              </>
            ) : (
              'Update Profile'
            )}
          </button>
          
          {avatarUrl !== user?.avatar_url && (
            <button
              type="button"
              onClick={() => setAvatarUrl(user?.avatar_url || '')}
              className="px-6 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
            >
              Reset Avatar
            </button>
          )}
        </div>
      </form>

      <div className="mt-6 pt-6 border-t border-gray-200">
        <p className="text-xs text-gray-400">
          Your profile information is private and only visible to project members.
        </p>
      </div>
    </div>
  );
};

export default Profile;