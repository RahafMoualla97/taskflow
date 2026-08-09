import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import apiClient from '../api/client';
import toast from 'react-hot-toast';
import { 
  FolderIcon, 
  ClipboardDocumentListIcon, 
  CheckCircleIcon, 
  ExclamationTriangleIcon,
  UserIcon,
  ArrowPathIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Area,
  AreaChart
} from 'recharts';

interface Project {
  id: number;
  name: string;
  key: string;
  description?: string;
  owner_id: number;
  created_at: string;
}

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

interface Activity {
  id: number;
  user_id: number;
  user_name?: string;
  project_id: number;
  project_name?: string;
  task_id?: number;
  task_title?: string;
  action: string;
  created_at: string;
}

interface Stats {
  total_projects: number;
  total_tasks: number;
  completed_tasks: number;
  overdue_tasks: number;
  my_tasks: number;
}

interface AdvancedStats {
  tasks_by_status: { ToDo: number; InProgress: number; Done: number };
  tasks_by_priority: { Low: number; Medium: number; High: number };
  tasks_by_project: Array<{ name: string; count: number }>;
  weekly_activity: Array<{ date: string; count: number }>;
  total_tasks: number;
  completion_rate: number;
  overdue_count: number;
}

const COLORS = {
  ToDo: '#94a3b8',
  InProgress: '#3b82f6',
  Done: '#22c55e',
  Low: '#22c55e',
  Medium: '#eab308',
  High: '#ef4444'
};

const Dashboard = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [recentTasks, setRecentTasks] = useState<Task[]>([]);
  const [overdueTasks, setOverdueTasks] = useState<Task[]>([]);
  const [activities, setActivities] = useState<Activity[]>([]);
  const [stats, setStats] = useState<Stats>({
    total_projects: 0,
    total_tasks: 0,
    completed_tasks: 0,
    overdue_tasks: 0,
    my_tasks: 0,
  });
  const [advancedStats, setAdvancedStats] = useState<AdvancedStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [
        projectsRes,
        statsRes,
        recentTasksRes,
        overdueTasksRes,
        activitiesRes,
        advancedStatsRes,
      ] = await Promise.all([
        apiClient.get('/projects'),
        apiClient.get('/dashboard/stats'),
        apiClient.get('/dashboard/tasks/recent?limit=5'),
        apiClient.get('/dashboard/tasks/overdue'),
        apiClient.get('/activities/recent?limit=10'),
        apiClient.get('/dashboard/advanced-stats'),
      ]);

      setProjects(projectsRes.data.slice(0, 3));
      setStats(statsRes.data);
      setRecentTasks(recentTasksRes.data);
      setOverdueTasks(overdueTasksRes.data);
      setActivities(activitiesRes.data);
      setAdvancedStats(advancedStatsRes.data);
    } catch (error: any) {
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = () => {
    setRefreshing(true);
    fetchDashboardData();
    toast.success('Dashboard refreshed!');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-500">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  const statCards = [
    { 
      title: 'Projects', 
      value: stats.total_projects, 
      icon: FolderIcon, 
      color: 'bg-blue-500' 
    },
    { 
      title: 'Total Tasks', 
      value: stats.total_tasks, 
      icon: ClipboardDocumentListIcon, 
      color: 'bg-purple-500' 
    },
    { 
      title: 'Completed', 
      value: stats.completed_tasks, 
      icon: CheckCircleIcon, 
      color: 'bg-green-500' 
    },
    { 
      title: 'Overdue', 
      value: stats.overdue_tasks, 
      icon: ExclamationTriangleIcon, 
      color: 'bg-red-500' 
    },
    { 
      title: 'My Tasks', 
      value: stats.my_tasks, 
      icon: UserIcon, 
      color: 'bg-orange-500' 
    },
  ];

  const statusData = advancedStats ? [
    { name: 'To Do', value: advancedStats.tasks_by_status.ToDo },
    { name: 'In Progress', value: advancedStats.tasks_by_status.InProgress },
    { name: 'Done', value: advancedStats.tasks_by_status.Done },
  ] : [];

  const priorityData = advancedStats ? [
    { name: 'Low', value: advancedStats.tasks_by_priority.Low },
    { name: 'Medium', value: advancedStats.tasks_by_priority.Medium },
    { name: 'High', value: advancedStats.tasks_by_priority.High },
  ] : [];

  const projectData = advancedStats?.tasks_by_project || [];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">📊 Dashboard</h1>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
        >
          <ArrowPathIcon className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {statCards.map((stat) => (
          <div key={stat.title} className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow">
            <div className="flex items-center">
              <div className={`p-3 rounded-lg ${stat.color}`}>
                <stat.icon className="w-6 h-6 text-white" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-500">{stat.title}</p>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 Tasks by Status</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={statusData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                  {statusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[entry.name as keyof typeof COLORS] || '#94a3b8'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">🎯 Tasks by Priority</h3>
          <div className="h-64 flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={priorityData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {priorityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[entry.name as keyof typeof COLORS] || '#94a3b8'} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Weekly Activity Chart */}
      {advancedStats && advancedStats.weekly_activity.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">📈 Weekly Activity</h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={advancedStats.weekly_activity}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Area type="monotone" dataKey="count" stroke="#3b82f6" fill="#93c5fd" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Recent & Overdue Tasks */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-gray-900">📋 Recent Tasks</h3>
            <Link to="/my-tasks" className="text-sm text-blue-600 hover:underline">
              View all
            </Link>
          </div>
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {recentTasks.length === 0 ? (
              <p className="text-gray-500 text-sm">No recent tasks</p>
            ) : (
              recentTasks.map((task) => (
                <Link
                  key={task.id}
                  to={`/tasks/${task.id}`}
                  className="block p-3 border rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="font-medium text-gray-900">{task.title}</p>
                      <p className="text-sm text-gray-500">{task.project_name}</p>
                    </div>
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      task.status === 'Done' ? 'bg-green-100 text-green-800' :
                      task.status === 'InProgress' ? 'bg-blue-100 text-blue-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {task.status}
                    </span>
                  </div>
                </Link>
              ))
            )}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-red-600">⚠️ Overdue Tasks</h3>
            <Link to="/my-tasks?status=overdue" className="text-sm text-blue-600 hover:underline">
              View all
            </Link>
          </div>
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {overdueTasks.length === 0 ? (
              <p className="text-gray-500 text-sm">No overdue tasks 🎉</p>
            ) : (
              overdueTasks.map((task) => (
                <Link
                  key={task.id}
                  to={`/tasks/${task.id}`}
                  className="block p-3 border border-red-200 rounded-lg hover:bg-red-50 transition-colors"
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="font-medium text-gray-900">{task.title}</p>
                      <p className="text-sm text-red-600">
                        Due: {task.due_date ? new Date(task.due_date).toLocaleDateString() : 'N/A'}
                      </p>
                    </div>
                    <ClockIcon className="w-5 h-5 text-red-500" />
                  </div>
                </Link>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Tasks by Project */}
      {projectData.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">📁 Tasks by Project</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {projectData.map((project) => (
              <div key={project.name} className="bg-gray-50 rounded-lg p-4">
                <p className="font-medium text-gray-900">{project.name}</p>
                <p className="text-2xl font-bold text-blue-600">{project.count}</p>
                <p className="text-xs text-gray-500">tasks</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Activity Feed */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">📊 Recent Activity</h3>
        <div className="space-y-3 max-h-80 overflow-y-auto">
          {activities.length === 0 ? (
            <p className="text-gray-500 text-sm">No recent activity</p>
          ) : (
            activities.map((activity) => (
              <div key={activity.id} className="flex items-start gap-3 p-2 border-b">
                <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 text-sm font-bold">
                  {activity.user_name?.charAt(0) || 'U'}
                </div>
                <div className="flex-1">
                  <p className="text-sm text-gray-800">
                    <span className="font-medium">{activity.user_name}</span>
                    {' '}
                    <span className="text-gray-600">{activity.action}</span>
                  </p>
                  <p className="text-xs text-gray-400">
                    {new Date(activity.created_at).toLocaleString()}
                  </p>
                  {activity.task_title && (
                    <Link
                      to={`/tasks/${activity.task_id}`}
                      className="text-xs text-blue-600 hover:underline"
                    >
                      View task
                    </Link>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Quick Projects */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">🚀 Quick Projects</h3>
          <Link to="/projects" className="text-sm text-blue-600 hover:underline">
            View all
          </Link>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {projects.map((project) => (
            <Link
              key={project.id}
              to={`/projects/${project.id}`}
              className="p-4 border rounded-lg hover:shadow-md transition-shadow"
            >
              <h4 className="font-medium text-gray-900">{project.name}</h4>
              <p className="text-sm text-gray-500">{project.key}</p>
              {project.description && (
                <p className="text-sm text-gray-600 mt-1 line-clamp-1">{project.description}</p>
              )}
            </Link>
          ))}
          <Link
            to="/projects"
            className="p-4 border-2 border-dashed rounded-lg hover:border-blue-500 transition-colors flex items-center justify-center text-gray-500 hover:text-blue-500"
          >
            <span className="text-2xl mr-2">+</span> New Project
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;