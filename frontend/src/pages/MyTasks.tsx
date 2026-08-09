import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import apiClient from '../api/client';
import toast from 'react-hot-toast';
import { MagnifyingGlassIcon, FunnelIcon, XMarkIcon } from '@heroicons/react/24/outline';

interface Task {
  id: number;
  title: string;
  description?: string;
  status: 'ToDo' | 'InProgress' | 'Done';
  priority: 'Low' | 'Medium' | 'High';
  project_id: number;
  assignee_id?: number;
  reporter_id: number;
  due_date?: string;
  estimated_hours?: number;
  logged_hours: number;
  created_at: string;
  updated_at?: string;
  assignee_name?: string;
  reporter_name?: string;
  project_name?: string;
}

const MyTasks = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [filteredTasks, setFilteredTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [priorityFilter, setPriorityFilter] = useState('all');
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    fetchTasks();
  }, []);

  useEffect(() => {
    let filtered = [...tasks];
    
    if (searchTerm.trim()) {
      filtered = filtered.filter(t =>
        t.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        t.description?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    if (statusFilter !== 'all') {
      filtered = filtered.filter(t => t.status === statusFilter);
    }
    
    if (priorityFilter !== 'all') {
      filtered = filtered.filter(t => t.priority === priorityFilter);
    }
    
    setFilteredTasks(filtered);
  }, [searchTerm, statusFilter, priorityFilter, tasks]);

  const fetchTasks = async () => {
    try {
      const response = await apiClient.get('/dashboard/tasks/my');
      setTasks(response.data);
      setFilteredTasks(response.data);
    } catch (error: any) {
      toast.error('Failed to load tasks');
    } finally {
      setLoading(false);
    }
  };

  const clearFilters = () => {
    setSearchTerm('');
    setStatusFilter('all');
    setPriorityFilter('all');
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Done': return 'bg-green-100 text-green-800';
      case 'InProgress': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'High': return 'bg-red-100 text-red-700 border-red-200';
      case 'Medium': return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      case 'Low': return 'bg-green-100 text-green-700 border-green-200';
      default: return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex flex-wrap justify-between items-center gap-4 mb-6">
        <h1 className="text-2xl font-bold text-gray-900">📋 My Tasks</h1>
        
        <div className="flex items-center gap-3 flex-wrap">
          <div className="relative">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search tasks..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-9 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent w-40 sm:w-56"
            />
          </div>
          
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`px-3 py-2 rounded-lg border transition-colors flex items-center gap-2 ${
              showFilters || statusFilter !== 'all' || priorityFilter !== 'all'
                ? 'bg-blue-50 border-blue-300 text-blue-600'
                : 'border-gray-300 text-gray-600 hover:bg-gray-50'
            }`}
          >
            <FunnelIcon className="w-4 h-4" />
            Filters
            {(statusFilter !== 'all' || priorityFilter !== 'all') && (
              <span className="w-2 h-2 rounded-full bg-blue-600"></span>
            )}
          </button>
          
          {(searchTerm || statusFilter !== 'all' || priorityFilter !== 'all') && (
            <button
              onClick={clearFilters}
              className="text-sm text-gray-500 hover:text-gray-700 flex items-center gap-1"
            >
              <XMarkIcon className="w-4 h-4" />
              Clear
            </button>
          )}
        </div>
      </div>

      {showFilters && (
        <div className="mb-4 p-4 bg-gray-50 rounded-lg grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Statuses</option>
              <option value="ToDo">📋 To Do</option>
              <option value="InProgress">🔄 In Progress</option>
              <option value="Done">✅ Done</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
            <select
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Priorities</option>
              <option value="High">🔴 High</option>
              <option value="Medium">🟡 Medium</option>
              <option value="Low">🟢 Low</option>
            </select>
          </div>
        </div>
      )}

      <p className="text-sm text-gray-500 mb-4">
        {filteredTasks.length} task{filteredTasks.length !== 1 ? 's' : ''}
        {searchTerm && ` matching "${searchTerm}"`}
      </p>

      {filteredTasks.length === 0 ? (
        <p className="text-gray-500 text-center py-8">
          {searchTerm || statusFilter !== 'all' || priorityFilter !== 'all'
            ? 'No tasks match your filters.'
            : 'No tasks assigned to you.'}
        </p>
      ) : (
        <div className="space-y-3">
          {filteredTasks.map((task) => (
            <Link
              key={task.id}
              to={`/tasks/${task.id}`}
              className="block p-4 border rounded-lg hover:shadow-md transition-shadow"
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h3 className="font-medium text-gray-900">{task.title}</h3>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${getStatusColor(task.status)}`}>
                      {task.status}
                    </span>
                    <span className={`text-xs px-2 py-0.5 rounded-full border ${getPriorityColor(task.priority)}`}>
                      {task.priority}
                    </span>
                  </div>
                  {task.description && (
                    <p className="text-sm text-gray-600 mt-1 line-clamp-2">{task.description}</p>
                  )}
                  <div className="flex items-center gap-3 mt-2 text-sm text-gray-500">
                    {task.project_name && <span>📁 {task.project_name}</span>}
                    {task.due_date && (
                      <span>📅 {new Date(task.due_date).toLocaleDateString()}</span>
                    )}
                    {task.estimated_hours && (
                      <span>⏱ {task.estimated_hours}h</span>
                    )}
                  </div>
                </div>
                <span className="text-xs text-gray-400 whitespace-nowrap ml-4">
                  {new Date(task.created_at).toLocaleDateString()}
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};

export default MyTasks;