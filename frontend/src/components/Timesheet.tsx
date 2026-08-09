import { useState, useEffect } from 'react';
import apiClient from '../api/client';
import toast from 'react-hot-toast';
import { PlusIcon, TrashIcon, CalendarIcon, ClockIcon } from '@heroicons/react/24/outline';
import { useAuth } from '../context/AuthContext';

interface TimesheetEntry {
  id: number;
  task_id: number;
  user_id: number;
  user_name: string;
  date: string;
  hours: number;
  description?: string;
  created_at: string;
  updated_at?: string;
}

interface TimesheetProps {
  taskId: number;
  projectId: number;
}

const Timesheet: React.FC<TimesheetProps> = ({ taskId, projectId }) => {
  const { user } = useAuth();
  const [entries, setEntries] = useState<TimesheetEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [projectMembers, setProjectMembers] = useState<{ id: number; name: string }[]>([]);
  const [formData, setFormData] = useState({
    user_id: '',
    date: new Date().toISOString().split('T')[0],
    hours: 1,
    description: '',
  });

  useEffect(() => {
    fetchTimesheets();
    checkAdminRole();
    fetchProjectMembers();
  }, [taskId]);

  const fetchTimesheets = async () => {
    try {
      const res = await apiClient.get(`/timesheets/task/${taskId}`);
      setEntries(res.data);
    } catch (error) {
      toast.error('Failed to load timesheets');
    } finally {
      setLoading(false);
    }
  };

  const checkAdminRole = async () => {
    try {
      const res = await apiClient.get(`/projects/${projectId}/members`);
      const currentUser = res.data.find((m: any) => m.user_id === user?.id);
      if (currentUser && (currentUser.role === 'Owner' || currentUser.role === 'Admin')) {
        setIsAdmin(true);
      }
    } catch {
      setIsAdmin(false);
    }
  };

  const fetchProjectMembers = async () => {
    try {
      const res = await apiClient.get(`/projects/${projectId}/members`);
      setProjectMembers(res.data.map((m: any) => ({
        id: m.user_id,
        name: m.user_name
      })));
    } catch {
      setProjectMembers([]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.hours <= 0) {
      toast.error('Hours must be greater than 0');
      return;
    }

    try {
      await apiClient.post('/timesheets', {
        task_id: taskId,
        user_id: formData.user_id || user?.id,
        date: formData.date,
        hours: formData.hours,
        description: formData.description,
      });
      toast.success('Time logged successfully!');
      setShowForm(false);
      setFormData({
        user_id: '',
        date: new Date().toISOString().split('T')[0],
        hours: 1,
        description: '',
      });
      await fetchTimesheets();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to log time');
    }
  };

  const handleDelete = async (entryId: number) => {
    if (!window.confirm('Are you sure you want to delete this entry?')) return;
    try {
      await apiClient.delete(`/timesheets/${entryId}`);
      toast.success('Entry deleted!');
      await fetchTimesheets();
    } catch (error) {
      toast.error('Failed to delete entry');
    }
  };

  const totalHours = entries.reduce((sum, e) => sum + e.hours, 0);

  if (loading) {
    return <div className="text-center py-4">Loading timesheets...</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-4">
          <h3 className="text-lg font-semibold text-gray-900">⏱ Timesheet</h3>
          <span className="text-sm bg-blue-100 text-blue-700 px-3 py-1 rounded-full">
            Total: {totalHours.toFixed(1)}h
          </span>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-1 text-sm"
        >
          <PlusIcon className="w-4 h-4" />
          Log Time
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleSubmit} className="bg-gray-50 rounded-xl p-4 border border-gray-200">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
            {isAdmin && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">User</label>
                <select
                  value={formData.user_id}
                  onChange={(e) => setFormData({ ...formData, user_id: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select User</option>
                  {projectMembers.map((m) => (
                    <option key={m.id} value={m.id}>{m.name}</option>
                  ))}
                </select>
              </div>
            )}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Date</label>
              <input
                type="date"
                value={formData.date}
                onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Hours</label>
              <input
                type="number"
                min="0.5"
                step="0.5"
                max="24"
                value={formData.hours}
                onChange={(e) => setFormData({ ...formData, hours: parseFloat(e.target.value) || 0 })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
              <input
                type="text"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="What did you work on?"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
          <div className="flex justify-end gap-2 mt-3">
            <button
              type="button"
              onClick={() => setShowForm(false)}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
            >
              Save
            </button>
          </div>
        </form>
      )}

      {entries.length === 0 ? (
        <div className="text-center py-8 text-gray-400">
          <ClockIcon className="w-12 h-12 mx-auto mb-2 opacity-30" />
          <p className="text-sm">No time logged yet</p>
        </div>
      ) : (
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {entries.map((entry) => (
            <div
              key={entry.id}
              className="flex justify-between items-center p-3 bg-gray-50 rounded-lg border border-gray-100 hover:bg-gray-100 transition-colors"
            >
              <div className="flex items-start gap-3">
                <div className="bg-blue-100 rounded-full p-2">
                  <CalendarIcon className="w-4 h-4 text-blue-600" />
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">
                    {new Date(entry.date).toLocaleDateString()}
                  </p>
                  <p className="text-sm text-gray-600">
                    {entry.hours}h {entry.description && `· ${entry.description}`}
                  </p>
                  <p className="text-xs text-gray-400">
                    By <span className="font-medium text-gray-600">{entry.user_name}</span>
                  </p>
                </div>
              </div>
              <button
                onClick={() => handleDelete(entry.id)}
                className="text-red-400 hover:text-red-600 transition-colors p-1"
              >
                <TrashIcon className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Timesheet;