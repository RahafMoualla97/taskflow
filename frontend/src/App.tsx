// frontend/src/App.tsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import ProjectBoard from './pages/ProjectBoard';
import TaskDetails from './pages/TaskDetails';
import AuthCallback from './pages/AuthCallback';
import InvitationAccept from './pages/InvitationAccept';
import Profile from './pages/Profile';
import Settings from './pages/Settings';
import Layout from './components/Layout';
import MyTasks from './pages/MyTasks';
import Projects from './pages/Projects';
import NotificationsPage from './pages/NotificationsPage';
import TimesheetReport from './pages/TimesheetReport';
import MembersManagement from './pages/MembersManagement'; // ✅ أضيفي هذا
import { Toaster } from 'react-hot-toast';

const PrivateRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth();
  if (loading) return <div className="flex items-center justify-center h-screen">Loading...</div>;
  return user ? <>{children}</> : <Navigate to="/login" />;
};

const AppLayout = ({ children }: { children: React.ReactNode }) => (
  <Layout>{children}</Layout>
);

function App() {
  return (
    <>
      <Toaster position="top-right" />
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/auth/callback" element={<AuthCallback />} />
            <Route path="/invitations/accept" element={<InvitationAccept />} />
            
            <Route path="/" element={
              <PrivateRoute>
                <AppLayout>
                  <Dashboard />
                </AppLayout>
              </PrivateRoute>
            } />
            
            <Route path="/projects/:id" element={
              <PrivateRoute>
                <AppLayout>
                  <ProjectBoard />
                </AppLayout>
              </PrivateRoute>
            } />
            
            {/* ✅ مسار إدارة الأعضاء */}
            <Route path="/projects/:id/members" element={
              <PrivateRoute>
                <AppLayout>
                  <MembersManagement />
                </AppLayout>
              </PrivateRoute>
            } />
            
            <Route path="/tasks/:taskId" element={
              <PrivateRoute>
                <AppLayout>
                  <TaskDetails />
                </AppLayout>
              </PrivateRoute>
            } />
            
            <Route path="/profile" element={
              <PrivateRoute>
                <AppLayout>
                  <Profile />
                </AppLayout>
              </PrivateRoute>
            } />
            
            <Route path="/settings" element={
              <PrivateRoute>
                <AppLayout>
                  <Settings />
                </AppLayout>
              </PrivateRoute>
            } />
            
            <Route path="/my-tasks" element={
              <PrivateRoute>
                <AppLayout>
                  <MyTasks />
                </AppLayout>
              </PrivateRoute>
            } />
            
            <Route path="/projects" element={
              <PrivateRoute>
                <AppLayout>
                  <Projects />
                </AppLayout>
              </PrivateRoute>
            } />
            
            <Route path="/notifications" element={
              <PrivateRoute>
                <AppLayout>
                  <NotificationsPage />
                </AppLayout>
              </PrivateRoute>
            } />
            
            <Route path="/timesheet-report" element={
              <PrivateRoute>
                <AppLayout>
                  <TimesheetReport />
                </AppLayout>
              </PrivateRoute>
            } />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </>
  );
}

export default App;