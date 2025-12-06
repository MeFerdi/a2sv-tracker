import { createContext, useState, useCallback, useContext } from 'react';
import { jwtDecode } from 'jwt-decode';
import axiosInstance from '../api/axiosClient'; // Import the configured Axios instance
import { useNavigate } from 'react-router-dom';

// 1. Create the Context
const AuthContext = createContext();

// Function to decode user data from an access token
const decodeUser = (token) => {
    try {
        const payload = jwtDecode(token);
        // The role (ADMIN or APPLICANT) is typically stored in the token payload
        return {
            id: payload.user_id,
            email: payload.email,
            role: payload.role, 
        };
    } catch (error) {
        console.error("Failed to decode token:", error);
        return null;
    }
};

// 2. Create the Provider Component
export const AuthProvider = ({ children }) => {
    const navigate = useNavigate();
    
    // Initialize state with tokens from localStorage or null
    const [authTokens, setAuthTokens] = useState(() => {
        const access = localStorage.getItem('access');
        const refresh = localStorage.getItem('refresh');
        return access && refresh ? { access, refresh } : null;
    });

    // Initialize user state by decoding the stored token (if available)
    const [user, setUser] = useState(() => 
        authTokens ? decodeUser(authTokens.access) : null
    );

    const [isLoading, setIsLoading] = useState(false);

// ------------------------------------------------------------------
// Core Authentication Functions
// ------------------------------------------------------------------

    // 1. Register with Invite Token
    const registerWithToken = useCallback(async (token, name, password) => {
        setIsLoading(true);
        try {
            const response = await axiosInstance.post('/auth/invite/register/', {
                token,
                name,
                password,
            });
            
            // Django should return new JWT tokens upon successful registration
            const { access, refresh } = response.data;
            
            localStorage.setItem('access', access);
            localStorage.setItem('refresh', refresh);

            setAuthTokens({ access, refresh });
            setUser(decodeUser(access)); // Store the decoded user info
            
            setIsLoading(false);
            return { success: true, user: decodeUser(access) };

        } catch (error) {
            setIsLoading(false);
            console.error("Registration failed:", error.response?.data || error.message);
            throw error; // Re-throw for component-level error handling
        }
    }, []);

    // 2. Standard Login
    const login = useCallback(async (email, password) => {
        setIsLoading(true);
        try {
            const response = await axiosInstance.post('/auth/login/', {
                email,
                password,
            });

            // Django should return JWT tokens upon successful login
            const { access, refresh } = response.data;

            localStorage.setItem('access', access);
            localStorage.setItem('refresh', refresh);

            setAuthTokens({ access, refresh });
            setUser(decodeUser(access));
            
            setIsLoading(false);
            return { success: true, user: decodeUser(access) };

        } catch (error) {
            setIsLoading(false);
            console.error("Login failed:", error.response?.data || error.message);
            throw error;
        }
    }, []);

    // 3. Logout
    const logout = useCallback(() => {
        // Clear all state and local storage
        setAuthTokens(null);
        setUser(null);
        localStorage.removeItem('access');
        localStorage.removeItem('refresh');
        
        // Redirect to login page
        navigate('/login');
    }, [navigate]);

// ------------------------------------------------------------------
// Context Value and Provider
// ------------------------------------------------------------------

    const contextData = {
        user,
        authTokens,
        isLoading,
        isAuthenticated: !!user, // Simple check if user object exists
        registerWithToken,
        login,
        logout,
    };

    return (
        <AuthContext.Provider value={contextData}>
            {children}
        </AuthContext.Provider>
    );
};

// 3. Custom Hook to consume the Auth Context easily
export const useAuth = () => {
    return useContext(AuthContext);
};

// Ensure you export AuthProvider and AuthContext for routing setup
export default AuthContext;