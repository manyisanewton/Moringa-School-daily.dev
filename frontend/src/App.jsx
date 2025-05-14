import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { getUserProfile } from './api';

import RegistrationPage from './pages/RegistrationPage';
import LoginPage from './pages/LoginPage';
import LandingPage from './pages/LandingPage';
import ResetPasswordPage from './pages/ResetPasswordPage';
import Home2 from './pages/Home2';
import FeedSection from './components/FeedSection';
import Notificationss from './components/Notificationss';
import Profile from './pages/Profile';
import Categories from './pages/Categories';
import FeedPage from './pages/FeedPage';
import Notifications from './pages/Notifications';
import AuthCallback from './components/AuthCallback';
import ErrorBoundary from './ErrorBoundary';
import TechHome from './techWriter/TechHome';
import TechWriterPosts from './techWriter/TechWriterPosts';
import Content from './techWriter/Content';
import TechWriterFlaggedContent from './techWriter/TechWriterFlaggedContent';
import TechWriterProfile from './techWriter/TechWriterProfile';
import Code from "./admin/Code";
import NewPassword from "./admin/NewPassword";

import AdminHome from './admin/AdminHome';
import CategoriesManagement from './admin/CategoriesManagement';
import AdminProfile from './admin/AdminProfile';
import UserManagement from './admin/UserManagement';
import ContentManagement from './admin/ContentManagement';

function ProtectedRoute({ children, requiredRole }) {
  const location = useLocation();
  const navigate = useNavigate();
  const [userRole, setUserRole] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const hasCheckedAuth = useRef(false); // Track if auth check has run

  useEffect(() => {
    if (hasCheckedAuth.current) return; // Prevent multiple runs
    hasCheckedAuth.current = true;

    const checkAuth = async () => {
      const role = localStorage.getItem('user_role');
      if (role) {
        setUserRole(role);
        setIsLoading(false);
        return;
      }

      try {
        const response = await getUserProfile();
        const fetchedRole = response.data.primary_role;
        localStorage.setItem('user_role', fetchedRole);
        setUserRole(fetchedRole);
      } catch (error) {
        console.error('Auth check failed:', error.response?.data || error.message);
        if (location.pathname !== '/login') {
          navigate('/login', { state: { error: 'Please log in to access this page' }, replace: true });
        }
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, []); // Empty dependency array to run once on mount

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (userRole === null) {
    return <Navigate to="/login" replace />;
  }

  if (userRole !== requiredRole) {
    switch (userRole) {
      case 'Admin':
        return <Navigate to="/admindashboard" replace />;
      case 'TechWriter':
        return <Navigate to="/techwriterdashboard" replace />;
      case 'User':
        return <Navigate to="/userdashboard" replace />;
      default:
        return <Navigate to="/login" replace />;
    }
  }

  return children;
}

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/auth/callback" element={<AuthCallback />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/forgot-password" element={<ResetPasswordPage />} />
        <Route path="/register" element={<RegistrationPage />} />
        <Route path="/feed" element={<FeedSection />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/category" element={<Categories />} />
        <Route path="/feedpage" element={<FeedPage />} />
        <Route path="/notifications" element={<Notifications />} />
        <Route path="/home" element={<Home2 />} />
        <Route path="/code" element={<Code />} />
        <Route path="/notificationss" element={<Notificationss />} />
        <Route
          path="/new-password"
          element={
            <ErrorBoundary>
              <NewPassword />
            </ErrorBoundary>
          }
        />
        <Route
          path="/userdashboard"
          element={
            <ProtectedRoute requiredRole="User">
              <Home2 />
            </ProtectedRoute>
          }
        />
        <Route
          path="/techwriterdashboard"
          element={
            <ProtectedRoute requiredRole="TechWriter">
              <TechHome />
            </ProtectedRoute>
          }
        />
        <Route
          path="/admindashboard"
          element={
            <ProtectedRoute requiredRole="Admin">
              <AdminHome />
            </ProtectedRoute>
          }
        />
        <Route path="/techhome" element={<TechHome />} />
        <Route path="/my-posts" element={<TechWriterPosts />} />
        <Route path="/content" element={<Content />} />
        <Route path="/tech-writer-flagged" element={<TechWriterFlaggedContent />} />
        <Route path="/tech-writer-profile" element={<TechWriterProfile />} />
        <Route path="/admin-home" element={<AdminHome />} />
        <Route path="/user-management" element={<UserManagement />} />
        <Route path="/categories-management" element={<CategoriesManagement />} />
        <Route path="/admin-profile" element={<AdminProfile />} />
        <Route path="/content-management" element={<ContentManagement />} />
      </Routes>
    </Router>
  );
}

export default App;