import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import apiClient from '../api/client';
import toast from 'react-hot-toast';
import Select from 'react-select';
import { MentionsInput, Mention } from 'react-mentions';
import Timesheet from '../components/Timesheet';
import { 
  ArrowLeftIcon, 
  PencilIcon, 
  TrashIcon, 
  UserIcon, 
  CalendarIcon, 
  ClockIcon, 
  ChatBubbleLeftRightIcon,
  ListBulletIcon,
  UserGroupIcon,
  EyeIcon,
  PlusIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import { CheckCircleIcon as CheckCircleSolid } from '@heroicons/react/24/solid';

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
  collaborators?: Array<{ id: number; name: string; email: string }>;
  watchers?: Array<{ id: number; name: string; email: string }>;
}

interface Project {
  id: number;
  name: string;
  key: string;
}

interface Member {
  id: number;
  name: string;
  email: string;
}

interface Activity {
  id: number;
  user_name: string;
  action: string;
  created_at: string;
}

interface Comment {
  id: number;
  content: string;
  author_id: number;
  author_name: string;
  created_at: string;
  mentions?: number[];
}

const TaskDetails = () => {
  const { taskId } = useParams<{ taskId: string }>();
  const { user } = useAuth();
  const navigate = useNavigate();
  
  const [task, setTask] = useState<Task | null>(null);
  const [project, setProject] = useState<Project | null>(null);
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [activeTab, setActiveTab] = useState<'details' | 'comments' | 'activity' | 'timesheet'>('details');
  const [activities, setActivities] = useState<Activity[]>([]);
  const [comments, setComments] = useState<Comment[]>([]);
  const [newComment, setNewComment] = useState('');
  const [collaboratorEmail, setCollaboratorEmail] = useState('');
  const [watcherEmail, setWatcherEmail] = useState('');
  const [showCollaboratorInput, setShowCollaboratorInput] = useState(false);
  const [showWatcherInput, setShowWatcherInput] = useState(false);
  const commentsEndRef = useRef<HTMLDivElement>(null);

  
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    status: 'ToDo' as 'ToDo' | 'InProgress' | 'Done',
    priority: 'Medium' as 'Low' | 'Medium' | 'High',
    assignee_id: '',
    due_date: '',
    estimated_hours: '',
  });

  useEffect(() => {
    fetchTaskDetails();
  }, [taskId]);

  /**
   * Fetch all task details including project info, members, activities, and comments
   */
  const fetchTaskDetails = async () => {
    try {
      const taskRes = await apiClient.get(`/tasks/${taskId}`);
      const taskData = taskRes.data;
      setTask(taskData);
      
      const projectRes = await apiClient.get(`/projects/${taskData.project_id}`);
      setProject(projectRes.data);

      const membersRes = await apiClient.get(`/projects/${taskData.project_id}/members`);
      setMembers(membersRes.data.map((m: any) => ({
        id: m.user_id,
        name: m.user_name,
        email: m.user_email,
      })));
      
      setFormData({
        title: taskData.title,
        description: taskData.description || '',
        status: taskData.status,
        priority: taskData.priority,
        assignee_id: taskData.assignee_id ? String(taskData.assignee_id) : '',
        due_date: taskData.due_date ? taskData.due_date.slice(0, 16) : '',
        estimated_hours: taskData.estimated_hours ? String(taskData.estimated_hours) : '',
      });

      await fetchActivities(taskData.id);
      await fetchComments(taskData.id);
      
    } catch (error: any) {
      if (error.response?.status === 404) {
        toast.error('This task no longer exists or has been deleted.');
        navigate('/my-tasks');
      } else {
        toast.error('Failed to load task details');
        navigate('/');
      }
    } finally {
      setLoading(false);
    }
  };

  /**
   * Fetch activity logs for the task
   */
  const fetchActivities = async (taskId: number) => {
    try {
      const res = await apiClient.get(`/activities/task/${taskId}?limit=50`);
      setActivities(res.data);
    } catch (error) {
      // Silently handle activity fetch failure
    }
  };

  /**
   * Fetch comments for the task, sorted newest first
   */
  const fetchComments = async (taskId: number) => {
    try {
      const res = await apiClient.get(`/comments/task/${taskId}`);
      const sorted = res.data.sort((a: any, b: any) => 
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );
      setComments(sorted);
    } catch (error) {
      // Silently handle comment fetch failure
    }
  };

  /**
   * Format date string into human-readable relative time
   */
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  /**
   * Fetch users for mention suggestions in comments
   */
  const getMentionUsers = async (query: string, callback: any) => {
    try {
      const res = await apiClient.get(`/projects/${task?.project_id}/members`);
      const users = res.data.map((m: any) => ({
        id: m.user_id,
        display: m.user_name,
        email: m.user_email,
      }));
      
      const filtered = query 
        ? users.filter((u: any) => u.display.toLowerCase().includes(query.toLowerCase()) || u.email.toLowerCase().includes(query.toLowerCase()))
        : users;
      
      callback(filtered.slice(0, 10));
    } catch (error) {
      callback([]);
    }
  };

  /**
   * Render @mentions in comment text with special styling
   */
  const renderMentions = (text: string) => {
    return text.replace(
      /@\[([^\]]+)\]\((\d+)\)/g,
      '<span class="bg-blue-100 text-blue-700 px-1 rounded font-medium">@$1</span>'
    );
  };

  /**
   * Add a new comment to the task with mention support
   */
  const handleAddComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim()) {
      toast.error('Please enter a comment');
      return;
    }
    
    try {
      const mentionRegex = /@\[([^\]]+)\]\((\d+)\)/g;
      const mentions: number[] = [];
      let match;
      while ((match = mentionRegex.exec(newComment)) !== null) {
        mentions.push(parseInt(match[2]));
      }
      
      const commentData = {
        content: newComment,
        mentions: mentions,
      };
      
      const res = await apiClient.post(`/comments/task/${taskId}`, commentData);
      
      setComments([res.data, ...comments]);
      setNewComment('');
      
      toast.success('Comment added!');
      
      if (mentions.length > 0) {
        toast.success(`Mentioned ${mentions.length} user(s)`);
      }
      
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to add comment');
    }
  };

  /**
   * Delete a comment (author or admin only)
   */
  const deleteComment = async (commentId: number) => {
    if (!window.confirm('Are you sure you want to delete this comment?')) return;
    try {
      await apiClient.delete(`/comments/${commentId}`);
      setComments(comments.filter(c => c.id !== commentId));
      toast.success('Comment deleted');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to delete comment');
    }
  };

  /**
   * Render all comments with author avatars and mention highlighting
   */
  const renderComments = () => {
    if (comments.length === 0) {
      return (
        <div className="text-center py-12">
          <div className="text-4xl mb-3">💬</div>
          <p className="text-gray-500 text-sm">No comments yet. Start the conversation!</p>
        </div>
      );
    }
    
    return (
      <div className="space-y-3">
        {comments.map((comment) => (
          <div key={comment.id} className="bg-white rounded-xl p-4 border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-sm font-bold shadow-sm flex-shrink-0">
                  {comment.author_name?.charAt(0)?.toUpperCase() || 'U'}
                </div>
                <div>
                  <span className="font-semibold text-gray-800">{comment.author_name || 'Unknown'}</span>
                  <span className="text-xs text-gray-400 ml-2">{formatDate(comment.created_at)}</span>
                </div>
              </div>
              {comment.author_id === user?.id && (
                <button
                  onClick={() => deleteComment(comment.id)}
                  className="text-gray-400 hover:text-red-600 transition-colors"
                >
                  <TrashIcon className="w-4 h-4" />
                </button>
              )}
            </div>
            
            <p 
              className="text-gray-700 mt-2 text-sm whitespace-pre-wrap"
              dangerouslySetInnerHTML={{
                __html: renderMentions(comment.content)
              }}
            />
          </div>
        ))}
      </div>
    );
  };

  /**
   * Update task details
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await apiClient.put(`/tasks/${taskId}`, {
        title: formData.title,
        description: formData.description,
        status: formData.status,
        priority: formData.priority,
        assignee_id: formData.assignee_id ? Number(formData.assignee_id) : null,
        due_date: formData.due_date ? new Date(formData.due_date).toISOString() : null,
        estimated_hours: formData.estimated_hours ? Number(formData.estimated_hours) : null,
      });
      
      setTask(response.data);
      setEditing(false);
      toast.success('Task updated successfully!');
      await fetchTaskDetails();
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to update task';
      toast.error(typeof errorMessage === 'object' ? JSON.stringify(errorMessage) : errorMessage);
    }
  };

  /**
   * Update task status with validation
   */
  const handleStatusChange = async (newStatus: 'ToDo' | 'InProgress' | 'Done') => {
    try {
      const response = await apiClient.patch(`/tasks/${taskId}/status`, { status: newStatus });
      setTask(response.data);
      setFormData(prev => ({ ...prev, status: response.data.status }));
      toast.success(`Status updated to ${newStatus}!`);
      await fetchTaskDetails();
    } catch (error: any) {
      toast.error('Failed to update status');
    }
  };

  /**
   * Delete the task
   */
  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this task?')) return;
    try {
      await apiClient.delete(`/tasks/${taskId}`);
      toast.success('Task deleted!');
      navigate(`/projects/${task?.project_id}`);
    } catch (error: any) {
      toast.error('Failed to delete task');
    }
  };

  /**
   * Add a collaborator to the task
   */
  const handleAddCollaborator = async () => {
    if (!collaboratorEmail) {
      toast.error('Please enter an email address');
      return;
    }
    try {
      await apiClient.post(`/tasks/${taskId}/collaborators?email=${collaboratorEmail}`);
      toast.success(`Collaborator invitation sent to ${collaboratorEmail}`);
      setCollaboratorEmail('');
      setShowCollaboratorInput(false);
      await fetchTaskDetails();
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to add collaborator';
      toast.error(typeof errorMessage === 'object' ? JSON.stringify(errorMessage) : errorMessage);
    }
  };

  /**
   * Add a watcher to the task
   */
  const handleAddWatcher = async () => {
    if (!watcherEmail) {
      toast.error('Please enter an email address');
      return;
    }
    try {
      await apiClient.post(`/tasks/${taskId}/watchers?email=${watcherEmail}`);
      toast.success(`Watcher invitation sent to ${watcherEmail}`);
      setWatcherEmail('');
      setShowWatcherInput(false);
      await fetchTaskDetails();
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to add watcher';
      toast.error(typeof errorMessage === 'object' ? JSON.stringify(errorMessage) : errorMessage);
    }
  };

  /**
   * Get priority color for styling
   */
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'High': return 'bg-red-100 text-red-700 border-red-200';
      case 'Medium': return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      case 'Low': return 'bg-green-100 text-green-700 border-green-200';
      default: return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  /**
   * Get status color for styling
   */
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Done': return 'bg-green-100 text-green-800';
      case 'InProgress': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'Done': return '✅';
      case 'InProgress': return '🔄';
      default: return '📋';
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'High': return '🔴';
      case 'Medium': return '🟡';
      case 'Low': return '🟢';
      default: return '⚪';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-500">Loading task details...</p>
        </div>
      </div>
    );
  }

  if (!task || !project) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-50">
        <div className="text-center">
          <div className="text-6xl mb-4">🔍</div>
          <h2 className="text-2xl font-bold text-gray-800">Task not found</h2>
          <p className="text-gray-500 mt-2">The task you're looking for doesn't exist or you don't have access.</p>
          <Link to="/" className="mt-4 inline-block text-blue-600 hover:underline">
            Go to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-6">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Breadcrumb Navigation */}
        <div className="flex items-center gap-3 mb-6 text-sm">
          <Link
            to={`/projects/${task.project_id}`}
            className="flex items-center gap-1 text-gray-500 hover:text-blue-600 transition-colors"
          >
            <ArrowLeftIcon className="w-4 h-4" />
            Back to Project
          </Link>
          <span className="text-gray-300">/</span>
          <span className="text-gray-400">{project.key}-{task.id}</span>
          <span className="text-gray-300">/</span>
          <span className="text-gray-600 font-medium truncate max-w-[200px]">{task.title}</span>
        </div>

        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
          
          {/* Task Header */}
          <div className="px-6 py-5 border-b border-gray-100 bg-gradient-to-r from-blue-50 to-white">
            <div className="flex justify-between items-start flex-wrap gap-4">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-3 flex-wrap">
                  <h1 className="text-2xl font-bold text-gray-900 truncate">
                    {editing ? 'Edit Task' : task.title}
                  </h1>
                  <div className="flex items-center gap-2">
                    <span className={`text-xs px-3 py-1 rounded-full border ${getPriorityColor(task.priority)} font-medium`}>
                      {getPriorityIcon(task.priority)} {task.priority}
                    </span>
                    <span className={`text-xs px-3 py-1 rounded-full font-medium ${getStatusColor(task.status)}`}>
                      {getStatusIcon(task.status)} {task.status === 'ToDo' ? 'To Do' : task.status === 'InProgress' ? 'In Progress' : 'Done'}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-4 mt-1.5 text-sm text-gray-500">
                  <span>📁 {project.name}</span>
                  <span>•</span>
                  <span>🆔 {project.key}-{task.id}</span>
                  {task.created_at && (
                    <>
                      <span>•</span>
                      <span>Created {new Date(task.created_at).toLocaleDateString()}</span>
                    </>
                  )}
                </div>
              </div>
              <div className="flex gap-2 flex-shrink-0">
                <button
                  onClick={() => setEditing(!editing)}
                  className={`px-4 py-2 rounded-lg transition-all flex items-center gap-2 ${
                    editing 
                      ? 'bg-gray-100 text-gray-700 hover:bg-gray-200' 
                      : 'bg-blue-600 text-white hover:bg-blue-700 shadow-sm hover:shadow'
                  }`}
                >
                  {editing ? (
                    <>
                      <XMarkIcon className="w-4 h-4" />
                      Cancel
                    </>
                  ) : (
                    <>
                      <PencilIcon className="w-4 h-4" />
                      Edit
                    </>
                  )}
                </button>
                <button
                  onClick={handleDelete}
                  className="px-4 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-all flex items-center gap-2"
                >
                  <TrashIcon className="w-4 h-4" />
                  Delete
                </button>
              </div>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="border-b border-gray-200 bg-gray-50/50 px-6">
            <nav className="flex gap-1 -mb-px">
              {(['details', 'comments', 'activity', 'timesheet'] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-5 py-3 text-sm font-medium border-b-2 transition-all flex items-center gap-2 ${
                    activeTab === tab
                      ? 'border-blue-600 text-blue-600 bg-white -mb-px'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {tab === 'details' && <ListBulletIcon className="w-4 h-4" />}
                  {tab === 'comments' && <ChatBubbleLeftRightIcon className="w-4 h-4" />}
                  {tab === 'activity' && <ClockIcon className="w-4 h-4" />}
                  {tab === 'timesheet' && <ClockIcon className="w-4 h-4" />}
                  {tab === 'details' && 'Details'}
                  {tab === 'comments' && `Comments (${comments.length})`}
                  {tab === 'activity' && `Activity (${activities.length})`}
                  {tab === 'timesheet' && '⏱ Timesheet'}
                </button>
              ))}
            </nav>
          </div>

          {/* Content Area */}
          <div className="p-6">
            
            {/* Details Tab */}
            {activeTab === 'details' && (
              <>
                {editing ? (
                  <form onSubmit={handleSubmit} className="space-y-5">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1.5">Title *</label>
                      <input
                        type="text"
                        required
                        value={formData.title}
                        onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                        className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1.5">Description</label>
                      <textarea
                        value={formData.description}
                        onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                        rows={4}
                        className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                        placeholder="Add a detailed description..."
                      />
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1.5">Status</label>
                        <select
                          value={formData.status}
                          onChange={(e) => setFormData({ ...formData, status: e.target.value as 'ToDo' | 'InProgress' | 'Done' })}
                          className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all bg-white"
                        >
                          <option value="ToDo">📋 To Do</option>
                          <option value="InProgress">🔄 In Progress</option>
                          <option value="Done">✅ Done</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1.5">Priority</label>
                        <select
                          value={formData.priority}
                          onChange={(e) => setFormData({ ...formData, priority: e.target.value as 'Low' | 'Medium' | 'High' })}
                          className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all bg-white"
                        >
                          <option value="Low">🟢 Low</option>
                          <option value="Medium">🟡 Medium</option>
                          <option value="High">🔴 High</option>
                        </select>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1.5">Assignee</label>
                        <Select
                          options={members.map(m => ({ value: m.id, label: `${m.name} (${m.email})` }))}
                          value={formData.assignee_id ? {
                            value: Number(formData.assignee_id),
                            label: members.find(m => m.id === Number(formData.assignee_id))?.name || ''
                          } : null}
                          onChange={(option: any) => {
                            setFormData({ ...formData, assignee_id: option ? String(option.value) : '' });
                          }}
                          isClearable
                          placeholder="Select assignee..."
                          className="w-full"
                          classNamePrefix="react-select"
                          styles={{
                            control: (base) => ({
                              ...base,
                              padding: '4px 0',
                              borderColor: '#d1d5db',
                              borderRadius: '12px',
                              boxShadow: 'none',
                              '&:hover': { borderColor: '#3b82f6' },
                              minHeight: '44px',
                            }),
                          }}
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1.5">Due Date</label>
                        <input
                          type="datetime-local"
                          value={formData.due_date}
                          onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                          className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                        />
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1.5">Estimated Hours</label>
                        <input
                          type="number"
                          min="0"
                          step="0.5"
                          value={formData.estimated_hours}
                          onChange={(e) => setFormData({ ...formData, estimated_hours: e.target.value })}
                          className="w-full px-4 py-2.5 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                          placeholder="0"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1.5">Logged Hours</label>
                        <input
                          type="number"
                          min="0"
                          step="0.5"
                          value={task.logged_hours}
                          disabled
                          className="w-full px-4 py-2.5 border border-gray-300 rounded-xl bg-gray-100 cursor-not-allowed"
                        />
                        <p className="text-xs text-gray-400 mt-1">Log hours from the project board</p>
                      </div>
                    </div>

                    <div className="flex justify-end gap-3 pt-4">
                      <button
                        type="button"
                        onClick={() => setEditing(false)}
                        className="px-6 py-2.5 border border-gray-300 rounded-xl hover:bg-gray-50 transition-all"
                      >
                        Cancel
                      </button>
                      <button
                        type="submit"
                        className="px-6 py-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-all shadow-sm hover:shadow flex items-center gap-2"
                      >
                        <CheckCircleSolid className="w-4 h-4" />
                        Save Changes
                      </button>
                    </div>
                  </form>
                ) : (
                  <div className="space-y-6">
                    {/* Status and Priority */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="bg-gray-50 rounded-xl p-4">
                        <h3 className="text-sm font-medium text-gray-500 mb-2">Status</h3>
                        <div className="flex flex-wrap items-center gap-3">
                          <span className={`px-4 py-1.5 rounded-full text-sm font-medium ${getStatusColor(task.status)}`}>
                            {getStatusIcon(task.status)} {task.status === 'ToDo' ? 'To Do' : task.status === 'InProgress' ? 'In Progress' : 'Done'}
                          </span>
                          <div className="flex gap-1">
                            {task.status !== 'ToDo' && (
                              <button onClick={() => handleStatusChange('ToDo')} className="text-xs px-3 py-1 bg-gray-200 hover:bg-gray-300 rounded-full transition-colors">← To Do</button>
                            )}
                            {task.status !== 'InProgress' && task.status !== 'Done' && (
                              <button onClick={() => handleStatusChange('InProgress')} className="text-xs px-3 py-1 bg-blue-100 hover:bg-blue-200 rounded-full transition-colors">→ In Progress</button>
                            )}
                            {task.status === 'InProgress' && (
                              <button onClick={() => handleStatusChange('Done')} className="text-xs px-3 py-1 bg-green-100 hover:bg-green-200 rounded-full transition-colors">✅ Done</button>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="bg-gray-50 rounded-xl p-4">
                        <h3 className="text-sm font-medium text-gray-500 mb-2">Priority</h3>
                        <span className={`px-4 py-1.5 rounded-full text-sm font-medium border ${getPriorityColor(task.priority)}`}>
                          {getPriorityIcon(task.priority)} {task.priority}
                        </span>
                      </div>
                    </div>

                    {/* Description */}
                    {task.description && (
                      <div className="bg-gray-50 rounded-xl p-4">
                        <h3 className="text-sm font-medium text-gray-500 mb-2">Description</h3>
                        <p className="text-gray-700 whitespace-pre-wrap">{task.description}</p>
                      </div>
                    )}

                    {/* Assignee & Reporter */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="bg-gray-50 rounded-xl p-4">
                        <h3 className="text-sm font-medium text-gray-500 mb-2 flex items-center gap-1">
                          <UserIcon className="w-4 h-4" /> Assignee
                        </h3>
                        <p className="text-gray-800 font-medium">{task.assignee_name || 'Unassigned'}</p>
                      </div>
                      <div className="bg-gray-50 rounded-xl p-4">
                        <h3 className="text-sm font-medium text-gray-500 mb-2 flex items-center gap-1">
                          <UserIcon className="w-4 h-4" /> Reporter
                        </h3>
                        <p className="text-gray-800 font-medium">{task.reporter_name || 'Unknown'}</p>
                      </div>
                    </div>

                    {/* Time Tracking */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="bg-gray-50 rounded-xl p-4">
                        <h3 className="text-sm font-medium text-gray-500 mb-2 flex items-center gap-1">
                          <CalendarIcon className="w-4 h-4" /> Due Date
                        </h3>
                        <p className="text-gray-800">{task.due_date ? new Date(task.due_date).toLocaleString() : 'Not set'}</p>
                      </div>
                      <div className="bg-gray-50 rounded-xl p-4">
                        <h3 className="text-sm font-medium text-gray-500 mb-2 flex items-center gap-1">
                          <ClockIcon className="w-4 h-4" /> Estimated Hours
                        </h3>
                        <p className="text-gray-800">{task.estimated_hours ? `${task.estimated_hours}h` : 'Not set'}</p>
                      </div>
                      <div className="bg-gray-50 rounded-xl p-4">
                        <h3 className="text-sm font-medium text-gray-500 mb-2 flex items-center gap-1">
                          <ClockIcon className="w-4 h-4" /> Logged Hours
                        </h3>
                        <p className="text-gray-800">{task.logged_hours}h</p>
                      </div>
                    </div>

                    {/* Collaborators & Watchers */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="bg-gray-50 rounded-xl p-4">
                        <div className="flex justify-between items-center mb-2">
                          <h3 className="text-sm font-medium text-gray-500 flex items-center gap-1">
                            <UserGroupIcon className="w-4 h-4" /> Collaborators
                          </h3>
                          <button
                            onClick={() => setShowCollaboratorInput(!showCollaboratorInput)}
                            className="text-blue-600 hover:text-blue-800 text-sm flex items-center gap-1"
                          >
                            <PlusIcon className="w-4 h-4" /> Add
                          </button>
                        </div>
                        {showCollaboratorInput && (
                          <div className="flex gap-2 mb-2">
                            <input
                              type="email"
                              value={collaboratorEmail}
                              onChange={(e) => setCollaboratorEmail(e.target.value)}
                              placeholder="Enter email..."
                              className="flex-1 px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                            <button
                              onClick={handleAddCollaborator}
                              className="px-3 py-1.5 bg-green-600 text-white rounded-lg text-sm hover:bg-green-700"
                            >
                              Add
                            </button>
                          </div>
                        )}
                        <div className="flex flex-wrap gap-1.5 mt-1">
                          {task.collaborators && task.collaborators.length > 0 ? (
                            task.collaborators.map((c) => (
                              <span key={c.id} className="text-xs bg-white px-3 py-1 rounded-full border border-gray-200 shadow-sm">
                                {c.name || c.email}
                              </span>
                            ))
                          ) : (
                            <span className="text-sm text-gray-400">No collaborators</span>
                          )}
                        </div>
                      </div>
                      <div className="bg-gray-50 rounded-xl p-4">
                        <div className="flex justify-between items-center mb-2">
                          <h3 className="text-sm font-medium text-gray-500 flex items-center gap-1">
                            <EyeIcon className="w-4 h-4" /> Watchers
                          </h3>
                          <button
                            onClick={() => setShowWatcherInput(!showWatcherInput)}
                            className="text-blue-600 hover:text-blue-800 text-sm flex items-center gap-1"
                          >
                            <PlusIcon className="w-4 h-4" /> Add
                          </button>
                        </div>
                        {showWatcherInput && (
                          <div className="flex gap-2 mb-2">
                            <input
                              type="email"
                              value={watcherEmail}
                              onChange={(e) => setWatcherEmail(e.target.value)}
                              placeholder="Enter email..."
                              className="flex-1 px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                            <button
                              onClick={handleAddWatcher}
                              className="px-3 py-1.5 bg-purple-600 text-white rounded-lg text-sm hover:bg-purple-700"
                            >
                              Add
                            </button>
                          </div>
                        )}
                        <div className="flex flex-wrap gap-1.5 mt-1">
                          {task.watchers && task.watchers.length > 0 ? (
                            task.watchers.map((w) => (
                              <span key={w.id} className="text-xs bg-purple-50 text-purple-700 px-3 py-1 rounded-full border border-purple-200 shadow-sm">
                                👁 {w.name || w.email}
                              </span>
                            ))
                          ) : (
                            <span className="text-sm text-gray-400">No watchers</span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </>
            )}

            {/* Comments Tab */}
            {activeTab === 'comments' && (
              <div className="flex flex-col h-full">
                <div className="flex-shrink-0 mb-4 relative" style={{ overflow: 'visible' }}>
                  <form onSubmit={handleAddComment} style={{ overflow: 'visible' }}>
                    <div className="relative" style={{ overflow: 'visible' }}>
                      <MentionsInput
                        value={newComment}
                        onChange={(e) => setNewComment(e.target.value)}
                        placeholder="Write a comment... (use @ to mention someone)"
                        className="mentions-input w-full"
                        a11ySuggestionsListLabel="Suggested mentions"
                        style={{
                          input: {
                            padding: '12px 16px 52px 16px',
                            border: '2px solid #e5e7eb',
                            borderRadius: '16px',
                            fontSize: '14px',
                            minHeight: '70px',
                            maxHeight: '150px',
                            width: '100%',
                            outline: 'none',
                            backgroundColor: 'white',
                            fontFamily: 'inherit',
                            resize: 'vertical',
                            overflowY: 'auto',
                            transition: 'border-color 0.2s, box-shadow 0.2s',
                          },
                          suggestions: {
                            list: {
                              backgroundColor: 'white',
                              border: '1px solid #e5e7eb',
                              borderRadius: '12px',
                              boxShadow: '0 10px 25px -5px rgba(0,0,0,0.1)',
                              maxHeight: '200px',
                              overflowY: 'auto',
                              position: 'absolute',
                              bottom: 'calc(100% + 8px)',
                              left: 0,
                              right: 0,
                              zIndex: 999999,
                            },
                            item: {
                              padding: '10px 14px',
                              cursor: 'pointer',
                              fontSize: '14px',
                              '&focused': {
                                backgroundColor: '#eff6ff',
                              },
                            },
                          },
                        }}
                      >
                        <Mention
                          trigger="@"
                          data={getMentionUsers}
                          displayTransform={(_id: string, display: string) => `@${display}`}
                          markup="@[__display__](__id__)"
                        />
                      </MentionsInput>
                      
                      <div className="absolute bottom-2 right-2 flex gap-2 z-[9999]">
                        <button
                          type="submit"
                          className={`px-4 py-1 text-sm font-medium rounded-lg transition-all shadow-sm flex items-center gap-1.5 ${
                            newComment.trim()
                              ? 'bg-blue-600 text-white hover:bg-blue-700 shadow'
                              : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                          }`}
                          disabled={!newComment.trim()}
                        >
                          <ChatBubbleLeftRightIcon className="w-4 h-4" />
                          Post
                        </button>
                      </div>
                    </div>
                  </form>
                </div>
                
                <div className="flex-1 min-h-0">
                  <div className="bg-gray-50 rounded-xl p-4 max-h-[450px] overflow-y-auto">
                    {renderComments()}
                    <div ref={commentsEndRef} />
                  </div>
                </div>
                
              </div>
            )}

            {/* Activity Tab */}
            {activeTab === 'activity' && (
              <div className="space-y-3 max-h-[600px] overflow-y-auto pr-2">
                {activities.length === 0 ? (
                  <div className="text-center py-12">
                    <div className="text-4xl mb-3">📊</div>
                    <p className="text-gray-500 text-sm">No activity yet</p>
                  </div>
                ) : (
                  <div className="relative">
                    <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200"></div>
                    {activities.map((activity) => (
                      <div key={activity.id} className="flex gap-4 relative pl-12">
                        <div className="absolute left-0 top-1.5 w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-xs font-bold shadow-sm z-10">
                          {activity.user_name?.charAt(0)?.toUpperCase() || 'U'}
                        </div>
                        <div className="flex-1 bg-gray-50 rounded-xl p-4 hover:bg-gray-100 transition-colors">
                          <div className="flex justify-between items-start">
                            <p className="text-sm text-gray-800">
                              <span className="font-semibold">{activity.user_name}</span>
                              <span className="text-gray-600 ml-1">{activity.action}</span>
                            </p>
                            <span className="text-xs text-gray-400 whitespace-nowrap ml-4">
                              {formatDate(activity.created_at)}
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Timesheet Tab */}
            {activeTab === 'timesheet' && (
              <div>
                <Timesheet taskId={task.id} projectId={task.project_id} />
              </div>
            )}
            
          </div>
        </div>
      </div>
    </div>
  );
};

export default TaskDetails;