// frontend/src/pages/NotificationsPage.tsx
import { useEffect, useState } from 'react';
import apiClient from '../api/client';
import { BellIcon, CheckCircleIcon } from '@heroicons/react/24/outline';

interface Notification {
  id: number;
  type: string;
  title: string;
  content: string;
  task_id?: number;
  project_id?: number;
  action_url?: string;
  created_at: string;
  read: boolean;
}

const NotificationsPage = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);

  // ✅ جلب الإشعارات باستخدام apiClient
  const fetchNotifications = async () => {
    try {
      const response = await apiClient.get('/notifications');
      console.log('📨 Notifications fetched:', response.data.length);
      setNotifications(response.data);
    } catch (error) {
      console.error('Error fetching notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotifications();
  }, []);

  const markAsRead = async (id: number) => {
    try {
      await apiClient.patch(`/notifications/${id}/read`);
      setNotifications(prev =>
        prev.map(n => n.id === id ? { ...n, read: true } : n)
      );
    } catch (error) {
      console.error('Failed to mark as read:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      await apiClient.patch('/notifications/read-all');
      setNotifications(prev =>
        prev.map(n => ({ ...n, read: true }))
      );
    } catch (error) {
      console.error('Failed to mark all as read:', error);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'TaskAssigned': return '📋';
      case 'StatusChanged': return '🔄';
      case 'CommentAdded': return '💬';
      case 'Mentioned': return '@';
      case 'DeadlineReminder': return '⏰';
      case 'CollaboratorAdded': return '👥';
      case 'WatcherAdded': return '👁';
      default: return '🔔';
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'TaskAssigned': return 'bg-blue-100 text-blue-600';
      case 'StatusChanged': return 'bg-yellow-100 text-yellow-600';
      case 'CommentAdded': return 'bg-green-100 text-green-600';
      case 'Mentioned': return 'bg-purple-100 text-purple-600';
      case 'DeadlineReminder': return 'bg-red-100 text-red-600';
      default: return 'bg-gray-100 text-gray-600';
    }
  };

  const unreadCount = notifications.filter(n => !n.read).length;

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-3">
          <BellIcon className="w-6 h-6 text-gray-600" />
          <h1 className="text-2xl font-bold text-gray-900">All Notifications</h1>
          {unreadCount > 0 && (
            <span className="bg-blue-100 text-blue-700 text-sm px-3 py-1 rounded-full">
              {unreadCount} unread
            </span>
          )}
        </div>
        {unreadCount > 0 && (
          <button
            onClick={markAllAsRead}
            className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <CheckCircleIcon className="w-4 h-4" />
            Mark all as read
          </button>
        )}
      </div>

      {notifications.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 text-gray-400">
          <BellIcon className="w-16 h-16 mb-4 opacity-30" />
          <p className="text-lg font-medium">No notifications</p>
          <p className="text-sm">You're all caught up!</p>
        </div>
      ) : (
        <div className="space-y-3">
          {notifications.map((notification) => (
            <div
              key={notification.id}
              className={`p-4 rounded-lg border transition-colors cursor-pointer hover:shadow-md ${
                !notification.read ? 'bg-blue-50 border-blue-200' : 'bg-white border-gray-200'
              }`}
              onClick={() => {
                markAsRead(notification.id);
                if (notification.action_url) {
                  window.location.href = notification.action_url;
                }
              }}
            >
              <div className="flex items-start gap-4">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${getTypeColor(notification.type)}`}>
                  <span className="text-lg">{getTypeIcon(notification.type)}</span>
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="font-semibold text-gray-900">{notification.title}</p>
                    {!notification.read && (
                      <span className="w-2 h-2 rounded-full bg-blue-600 flex-shrink-0"></span>
                    )}
                  </div>
                  <p className="text-gray-700 mt-1">{notification.content}</p>
                  <p className="text-sm text-gray-400 mt-2">{formatDate(notification.created_at)}</p>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    markAsRead(notification.id);
                  }}
                  className="text-sm text-blue-600 hover:text-blue-800 font-medium flex-shrink-0"
                >
                  {notification.read ? 'Read ✓' : 'Mark as read'}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default NotificationsPage;