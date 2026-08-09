export interface User {
  id: number;
  email: string;
  name: string;
  avatar_url?: string;
  created_at: string;
}

export interface Project {
  id: number;
  name: string;
  key: string;
  description?: string;
  owner_id: number;
  created_at: string;
}

export interface Task {
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

export interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<any>;
  logout: () => void;
  googleLogin: () => void;
  updateUser: (data: { name?: string; avatar_url?: string }) => Promise<User>;
}

export interface Collaborator {
  id: number;
  name: string;
  email: string;
  avatar_url?: string;
}

export interface Watcher {
  id: number;
  name: string;
  email: string;
  avatar_url?: string;
}

export interface Notification {
  id: number;
  user_id: number;
  type: string;
  title: string;
  content: string;
  task_id?: number;
  project_id?: number;
  action_url?: string;
  read: boolean;
  created_at: string;
}

export interface Invitation {
  id: number;
  email: string;
  project_id: number;
  task_id?: number;
  token: string;
  status: 'Pending' | 'Accepted' | 'Expired';
  expires_at: string;
  created_at: string;
}