// frontend/src/components/Layout.tsx
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import NotificationBell from './NotificationBell';
import { 
  HomeIcon, 
  UserCircleIcon, 
  Cog6ToothIcon, 
  ArrowRightOnRectangleIcon, 
  FolderIcon, 
  ClipboardDocumentListIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout = ({ children }: LayoutProps) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [profileOpen, setProfileOpen] = useState(false);

  const handleLogout = () => {
    logout();
    toast.success('Logged out successfully!');
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-white shadow-lg fixed h-full">
        <div className="p-4 border-b">
          <h1 className="text-2xl font-bold text-blue-600">TaskFlow</h1>
        </div>
        <nav className="p-4 space-y-2">
          <Link to="/" className="flex items-center gap-3 px-4 py-2 text-gray-700 hover:bg-blue-50 rounded-lg transition-colors">
            <HomeIcon className="w-5 h-5" />
            Dashboard
          </Link>
          <Link to="/my-tasks" className="flex items-center gap-3 px-4 py-2 text-gray-700 hover:bg-blue-50 rounded-lg transition-colors">
            <ClipboardDocumentListIcon className="w-5 h-5" />
            My Tasks
          </Link>
          <Link to="/projects" className="flex items-center gap-3 px-4 py-2 text-gray-700 hover:bg-blue-50 rounded-lg transition-colors">
            <FolderIcon className="w-5 h-5" />
            Projects
          </Link>
          <Link to="/timesheet-report" className="flex items-center gap-3 px-4 py-2 text-gray-700 hover:bg-blue-50 rounded-lg transition-colors">
            <DocumentTextIcon className="w-5 h-5" />
            Timesheet Report
          </Link>
          <Link to="/profile" className="flex items-center gap-3 px-4 py-2 text-gray-700 hover:bg-blue-50 rounded-lg transition-colors">
            <UserCircleIcon className="w-5 h-5" />
            Profile
          </Link>
          <Link to="/settings" className="flex items-center gap-3 px-4 py-2 text-gray-700 hover:bg-blue-50 rounded-lg transition-colors">
            <Cog6ToothIcon className="w-5 h-5" />
            Settings
          </Link>
        </nav>
        <div className="absolute bottom-0 w-full p-4 border-t">
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 w-full px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
          >
            <ArrowRightOnRectangleIcon className="w-5 h-5" />
            Logout
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="ml-64 flex-1">
        {/* Top Bar */}
        <header className="bg-white shadow-sm px-6 py-3 flex items-center justify-between sticky top-0 z-10">
          <div className="flex items-center gap-4">
            <h2 className="text-xl font-semibold text-gray-800">Welcome back, {user?.name || 'User'}!</h2>
          </div>
          <div className="flex items-center gap-4">
            {/* ✅ NotificationBell (بدون Socket) */}
            <NotificationBell />

            {/* Profile Dropdown */}
            <div className="relative">
              <button
                onClick={() => setProfileOpen(!profileOpen)}
                className="flex items-center gap-2 p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <img
                  src={user?.avatar_url || 'https://ui-avatars.com/api/?name=' + user?.name}
                  alt={user?.name}
                  className="w-8 h-8 rounded-full"
                />
                <span className="text-sm font-medium text-gray-700">{user?.name}</span>
              </button>
              {profileOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border p-2 z-20">
                  <Link to="/profile" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg">
                    Profile
                  </Link>
                  <Link to="/settings" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg">
                    Settings
                  </Link>
                  <hr className="my-1" />
                  <button
                    onClick={handleLogout}
                    className="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg"
                  >
                    Logout
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="p-6">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;