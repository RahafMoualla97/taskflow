import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import apiClient from '../api/client';
import toast from 'react-hot-toast';
import MembersList from '../components/MembersList';
import Select from 'react-select';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';
import { ArrowLeftIcon, TrashIcon, PlusIcon, UserGroupIcon } from '@heroicons/react/24/outline';

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
}

interface Project {
  id: number;
  name: string;
  key: string;
  description?: string;
  owner_id: number;
  created_at: string;
}

interface Member {
  id: number;
  name: string;
  email: string;
}

const ProjectBoard = () => {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const navigate = useNavigate();
  
  const [project, setProject] = useState<Project | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [members, setMembers] = useState<Member[]>([]);
  const [loading, setLoading] = useState(true);
  const [showTaskForm, setShowTaskForm] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    priority: 'Medium' as 'Low' | 'Medium' | 'High',
    assignee_id: '',
    due_date: '',
  });

  useEffect(() => {
    fetchProjectAndTasks();
  }, [id]);

  const fetchProjectAndTasks = async () => {
    try {
      const [projectRes, tasksRes, membersRes] = await Promise.all([
        apiClient.get(`/projects/${id}`),
        apiClient.get(`/tasks/project/${id}`),
        apiClient.get(`/projects/${id}/members`),
      ]);
      setProject(projectRes.data);
      setTasks(tasksRes.data);
      setMembers(membersRes.data.map((m: any) => ({
        id: m.user_id,
        name: m.user_name,
        email: m.user_email,
      })));
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to load project';
      toast.error(typeof errorMessage === 'object' ? JSON.stringify(errorMessage) : errorMessage);
      navigate('/projects');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteProject = async () => {
    if (!user || project?.owner_id !== user.id) {
      toast.error('Only the project owner can delete this project');
      return;
    }

    setIsDeleting(true);
    try {
      await apiClient.delete(`/projects/${id}`);
      toast.success('Project deleted successfully!');
      navigate('/projects');
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to delete project';
      toast.error(typeof errorMessage === 'object' ? JSON.stringify(errorMessage) : errorMessage);
    } finally {
      setIsDeleting(false);
      setShowDeleteModal(false);
    }
  };

  const onDragEnd = async (result: any) => {
    const { destination, source, draggableId } = result;
    
    if (!destination) return;
    
    if (
      destination.droppableId === source.droppableId &&
      destination.index === source.index
    ) {
      return;
    }

    const taskId = parseInt(draggableId);
    const newStatus = destination.droppableId as 'ToDo' | 'InProgress' | 'Done';

    // Optimistic UI update
    setTasks(prevTasks =>
      prevTasks.map(task =>
        task.id === taskId ? { ...task, status: newStatus } : task
      )
    );

    try {
      await apiClient.patch(`/tasks/${taskId}/status`, { status: newStatus });
      toast.success(`Task moved to ${newStatus}!`);
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to update status';
      toast.error(typeof errorMessage === 'object' ? JSON.stringify(errorMessage) : errorMessage);
      await fetchProjectAndTasks();
    }
  };

  const createTask = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await apiClient.post('/tasks', {
        title: newTask.title,
        description: newTask.description,
        priority: newTask.priority,
        project_id: Number(id),
        assignee_id: newTask.assignee_id ? Number(newTask.assignee_id) : null,
        due_date: newTask.due_date ? new Date(newTask.due_date).toISOString() : null,
      });
      
      setTasks([response.data, ...tasks]);
      setShowTaskForm(false);
      setNewTask({
        title: '',
        description: '',
        priority: 'Medium',
        assignee_id: '',
        due_date: '',
      });
      toast.success('Task created successfully!');
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to create task';
      toast.error(typeof errorMessage === 'object' ? JSON.stringify(errorMessage) : errorMessage);
    }
  };

  const deleteTask = async (taskId: number) => {
    if (!window.confirm('Are you sure you want to delete this task?')) return;
    try {
      await apiClient.delete(`/tasks/${taskId}`);
      setTasks(tasks.filter(task => task.id !== taskId));
      toast.success('Task deleted!');
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to delete task';
      toast.error(typeof errorMessage === 'object' ? JSON.stringify(errorMessage) : errorMessage);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!project) {
    return <div className="p-8 text-center text-red-600">Project not found</div>;
  }

  const tasksByStatus = {
    ToDo: tasks.filter(t => t.status === 'ToDo'),
    InProgress: tasks.filter(t => t.status === 'InProgress'),
    Done: tasks.filter(t => t.status === 'Done'),
  };

  const isOwner = user?.id === project.owner_id;

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'High': return 'bg-red-100 text-red-700 border-red-200';
      case 'Medium': return 'bg-yellow-100 text-yellow-700 border-yellow-200';
      case 'Low': return 'bg-green-100 text-green-700 border-green-200';
      default: return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Done': return 'bg-green-100 text-green-800';
      case 'InProgress': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Header with Navigation and Actions */}
        <div className="flex flex-wrap justify-between items-center gap-4 mb-6">
          <div className="flex items-center gap-3">
            <Link
              to="/projects"
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-full transition-colors"
              title="Back to projects"
            >
              <ArrowLeftIcon className="w-6 h-6" />
            </Link>
            
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{project.name}</h1>
              {project.description && (
                <p className="text-gray-600 mt-1">{project.description}</p>
              )}
              <p className="text-sm text-gray-500 mt-1">Key: {project.key}</p>
            </div>
          </div>
          
          <div className="flex items-center gap-2 flex-wrap">
            {isOwner && (
              <button
                onClick={() => setShowDeleteModal(true)}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 flex items-center gap-2 transition-colors"
              >
                <TrashIcon className="w-5 h-5" />
                Delete Project
              </button>
            )}
            
            <Link
              to={`/projects/${id}/members`}
              className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 transition-colors flex items-center gap-2"
            >
              <UserGroupIcon className="w-5 h-5" />
              Manage Members
            </Link>
            
            <button
              onClick={() => setShowTaskForm(!showTaskForm)}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 flex items-center gap-2 transition-colors"
            >
              <PlusIcon className="w-5 h-5" />
              {showTaskForm ? 'Cancel' : 'New Task'}
            </button>
          </div>
        </div>

        {/* Members List */}
        <div className="mb-6">
          <MembersList projectId={Number(id)} />
        </div>

        {/* Create Task Form */}
        {showTaskForm && (
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-xl font-semibold mb-4">Create New Task</h2>
            <form onSubmit={createTask} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Title *</label>
                <input
                  type="text"
                  required
                  value={newTask.title}
                  onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  value={newTask.description}
                  onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
                  <select
                    value={newTask.priority}
                    onChange={(e) => setNewTask({ ...newTask, priority: e.target.value as 'Low' | 'Medium' | 'High' })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="Low">Low</option>
                    <option value="Medium">Medium</option>
                    <option value="High">High</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Due Date</label>
                  <input
                    type="datetime-local"
                    value={newTask.due_date}
                    onChange={(e) => setNewTask({ ...newTask, due_date: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Assignee (optional)</label>
                <Select
                  options={members.map(m => ({
                    value: m.id,
                    label: `${m.name} (${m.email})`
                  }))}
                  value={newTask.assignee_id ? {
                    value: Number(newTask.assignee_id),
                    label: members.find(m => m.id === Number(newTask.assignee_id))?.name || ''
                  } : null}
                  onChange={(option: any) => {
                    setNewTask({ ...newTask, assignee_id: option ? String(option.value) : '' });
                  }}
                  isClearable
                  placeholder="Search for a member..."
                  className="w-full"
                  classNamePrefix="react-select"
                  styles={{
                    control: (base) => ({
                      ...base,
                      padding: '2px 0',
                      borderColor: '#d1d5db',
                      boxShadow: 'none',
                      '&:hover': { borderColor: '#3b82f6' },
                    }),
                  }}
                />
              </div>
              <button
                type="submit"
                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
              >
                Create Task
              </button>
            </form>
          </div>
        )}

        {/* Kanban Board with Drag & Drop */}
        <DragDropContext onDragEnd={onDragEnd}>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {(['ToDo', 'InProgress', 'Done'] as const).map((status) => (
              <Droppable key={status} droppableId={status}>
                {(provided, snapshot) => (
                  <div
                    ref={provided.innerRef}
                    {...provided.droppableProps}
                    className={`bg-gray-100 rounded-lg p-4 min-h-[400px] transition-colors ${
                      snapshot.isDraggingOver ? 'bg-blue-100' : ''
                    }`}
                  >
                    <h3 className="font-semibold text-gray-700 mb-4 flex justify-between">
                      <span>
                        {status === 'ToDo' && '📋 To Do'}
                        {status === 'InProgress' && '🔄 In Progress'}
                        {status === 'Done' && '✅ Done'}
                      </span>
                      <span className="bg-gray-300 text-gray-700 px-2 py-0.5 rounded-full text-sm">
                        {tasksByStatus[status].length}
                      </span>
                    </h3>
                    
                    <div className="space-y-3">
                      {tasksByStatus[status].map((task, index) => (
                        <Draggable
                          key={task.id}
                          draggableId={String(task.id)}
                          index={index}
                        >
                          {(provided, snapshot) => (
                            <div
                              ref={provided.innerRef}
                              {...provided.draggableProps}
                              {...provided.dragHandleProps}
                              className={`bg-white rounded-md shadow p-4 hover:shadow-md transition-shadow duration-200 ${
                                snapshot.isDragging ? 'shadow-lg ring-2 ring-blue-400' : ''
                              }`}
                            >
                              <Link
                                to={`/tasks/${task.id}`}
                                className="block hover:no-underline"
                              >
                                <div className="flex justify-between items-start">
                                  <h4 className="font-medium text-gray-900">{task.title}</h4>
                                  <button
                                    onClick={(e) => {
                                      e.preventDefault();
                                      e.stopPropagation();
                                      deleteTask(task.id);
                                    }}
                                    className="text-red-500 hover:text-red-700 text-sm"
                                  >
                                    ✕
                                  </button>
                                </div>
                                
                                {task.description && (
                                  <p className="text-sm text-gray-600 mt-1 line-clamp-2">{task.description}</p>
                                )}
                                
                                <div className="flex flex-wrap items-center gap-2 mt-2">
                                  <span className={`text-xs px-2 py-0.5 rounded-full border ${getPriorityColor(task.priority)}`}>
                                    {task.priority}
                                  </span>
                                  
                                  <span className={`text-xs px-2 py-0.5 rounded-full ${getStatusColor(task.status)}`}>
                                    {task.status}
                                  </span>
                                  
                                  {task.assignee_name && (
                                    <span className="text-xs text-gray-500">👤 {task.assignee_name}</span>
                                  )}
                                  
                                  {task.due_date && (
                                    <span className="text-xs text-gray-500">
                                      📅 {new Date(task.due_date).toLocaleDateString()}
                                    </span>
                                  )}
                                  
                                  {task.estimated_hours && (
                                    <span className="text-xs text-gray-500">⏱ {task.estimated_hours}h</span>
                                  )}
                                  
                                  {task.logged_hours > 0 && (
                                    <span className="text-xs text-blue-500">📊 {task.logged_hours}h logged</span>
                                  )}
                                </div>
                              </Link>
                            </div>
                          )}
                        </Draggable>
                      ))}
                      {provided.placeholder}
                      
                      {tasksByStatus[status].length === 0 && (
                        <div className="bg-white/50 rounded-md p-4 text-center text-gray-400 text-sm border-2 border-dashed border-gray-300">
                          No tasks
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </Droppable>
            ))}
          </div>
        </DragDropContext>
      </div>

      {/* Delete Project Confirmation Modal */}
      {showDeleteModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <h2 className="text-xl font-semibold text-red-600 mb-4">⚠️ Delete Project</h2>
            <p className="text-gray-600 mb-6">
              Are you sure you want to delete <strong>"{project.name}"</strong>?<br />
              This action <strong>cannot be undone</strong> and all tasks, comments, and members will be permanently removed.
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setShowDeleteModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
                disabled={isDeleting}
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteProject}
                disabled={isDeleting}
                className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors disabled:opacity-50 flex items-center gap-2"
              >
                {isDeleting ? (
                  <>
                    <span className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
                    Deleting...
                  </>
                ) : (
                  <>
                    <TrashIcon className="w-5 h-5" />
                    Delete Project
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProjectBoard;