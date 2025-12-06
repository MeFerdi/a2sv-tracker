import { BrowserRouter as Router, Routes, Route, Navigate, useLocation, Outlet } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext'; 

// Import your page components
import LoginPage from './pages/LoginPage';
import TokenRegisterPage from './pages/TokenRegisterPage';
import ApplicantDashboard from './pages/ApplicantDashboard';
import AdminDashboard from './pages/Admin/AdminDashboard';
import QuestionManagementPage from './pages/Admin/QuestionManagementPage';
import NotFound from './pages/NotFound'; // You'll need to create this simple page

// --- 1. Router Setup ---
function App() {
  return (
    <Router>
      {/* 2. Wrap the entire app in the AuthProvider */}
      <AuthProvider>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<TokenRegisterPage />} /> {/* Handles ?token=... */}
          
          {/* Protected Routes (Uses AuthGuard) */}
          <Route path="/applicant" element={<AuthGuard allowedRoles={['APPLICANT']} />}>
            <Route index element={<ApplicantDashboard />} />
          </Route>

          <Route path="/admin" element={<AuthGuard allowedRoles={['ADMIN']} />}>
            <Route index element={<AdminDashboard />} />
            <Route path="questions" element={<QuestionManagementPage />} />
          </Route>
          
          {/* Default and Catch-all Routes */}
          <Route path="/" element={<Navigate to="/applicant" replace />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;

// --- 3. AuthGuard Component for Route Protection (Required for protected routes) ---

/**
 * A wrapper component to protect routes based on authentication status and user role.
 */
function AuthGuard({ allowedRoles }) {
  const { isAuthenticated, user, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    // Show a loading screen while checking authentication status
    return <div>Loading authentication state...</div>; 
  }

  if (!isAuthenticated) {
    // User is not logged in, redirect them to the login page
    // Store current location to redirect back after login
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check if the user's role is included in the allowedRoles list
  if (user && allowedRoles.includes(user.role)) {
    // Role is authorized, render the child component (Outlet)
    return <Outlet />; 
  } else {
    // User is logged in but unauthorized for this route (e.g., APPLICANT accessing /admin)
    // Redirect to a known safe route for their role
    return <Navigate to={`/${user.role.toLowerCase()}`} replace />;
  }
}