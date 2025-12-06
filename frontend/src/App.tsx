import { BrowserRouter as Router, Routes, Route, Navigate, useLocation, Outlet } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext.tsx'; 
import { useAuth } from './utils/Auth.tsx'

// Import page components
import LoginPage from './pages/Auth/LoginPage.tsx';
import TokenRegisterPage from './pages/Auth/TokenRegisterPage.tsx';
import ApplicantDashboard from './pages/Applicant/ApplicantDashboard.tsx';
import AdminDashboard from './pages/Admin/AdminDashboard.tsx';
import QuestionManagementPage from './pages/Admin/QuestionManagementPage.tsx';
import ApplicantTrackerPage from './pages/Admin/ApplicantTrackerPage.tsx';
import NotFound from './pages/Shared/NotFound.tsx';

// --- 1. Router Setup ---
function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<TokenRegisterPage />} />
          
          {/* Protected Routes (Uses AuthGuard) */}
          <Route element={<AuthGuard allowedRoles={['APPLICANT']} />}>
            <Route path="/applicant" element={<ApplicantDashboard />} />
          </Route>

          <Route element={<AuthGuard allowedRoles={['ADMIN']} />}>
            <Route path="/admin" element={<AdminDashboard />} />
            <Route path="/admin/questions" element={<QuestionManagementPage />} />
            <Route path="/admin/applicants" element={<ApplicantTrackerPage />} />
          </Route>
          
          {/* Dynamic Default Route and Catch-all Routes */}
          <Route path="/" element={<HomeRedirect />} /> {/* NEW: Dynamic redirect component */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;

// --- 2. NEW: HomeRedirect Component ---

/**
 * Redirects the user to the correct dashboard based on their role after login.
 * This replaces the problematic static <Navigate to="/applicant" />.
 */
function HomeRedirect() {
    const { isAuthenticated, user, isLoading } = useAuth();
    
    if (isLoading) {
        return <div>Loading authentication state...</div>;
    }
    
    if (!isAuthenticated) {
        // If not logged in, they should go to the login page
        return <Navigate to="/login" replace />;
    }
    
    // Logged in: redirect based on role
    if (user && user.role.toLowerCase() === 'admin') {
        return <Navigate to="/admin" replace />;
    }
    
    // Default to applicant route
    return <Navigate to="/applicant" replace />;
}


// --- 3. AuthGuard Component (Simplified and Corrected) ---

function AuthGuard({ allowedRoles }: { allowedRoles: string[] }) {
  const { isAuthenticated, user, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return <div>Loading authentication state...</div>; 
  }

  if (!isAuthenticated) {
    // Redirect to login, preserving the path they were trying to access
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check if the user's role is included in the allowedRoles list
  if (user && allowedRoles.includes(user.role)) {
    // Role is authorized, render the protected route content
    return <Outlet />; 
  } else {
    // If user is null/undefined, redirect to login. Otherwise, redirect to their default dashboard.
    if (!user || !user.role) {
      return <Navigate to="/login" replace />;
    }
    const userDefaultPath = `/${user.role.toLowerCase()}`;
    return <Navigate to={userDefaultPath} replace />;
  }
}