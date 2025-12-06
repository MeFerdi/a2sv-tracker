import { createContext, useState, useCallback } from 'react';
import axiosInstance from '../api/axiosClient.ts'; // Import the configured Axios instance
import { useNavigate } from 'react-router-dom';
import { decodeUser } from '../utils/useAuth.tsx';

// 1. Create the Context
// eslint-disable-next-line react-refresh/only-export-components
export const AuthContext = createContext<{
    user: { id: string; email: string; role: string } | null;
    authTokens: { access: string; refresh: string } | null;
    isLoading: boolean;
    isAuthenticated: boolean;
    registerWithToken: (token: string, name: string, password: string) => Promise<{ success: boolean; user: { id: string; email: string; role: string } | null }>;
    login: (email: string, password: string) => Promise<{ success: boolean; user: { id: string; email: string; role: string } | null }>;
    logout: () => void;
} | undefined>(undefined);

// 2. Create the Provider Component
import type { PropsWithChildren } from 'react';

export const AuthProvider = ({ children }: PropsWithChildren<object>) => {
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

// Core Authentication Functions

    // 1. Register with Invite Token
    const registerWithToken = useCallback(async (token: string, name: string, password: string) => {
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
            if (error && typeof error === 'object' && 'response' in error && error.response && typeof error.response === 'object' && 'data' in error.response) {
                console.error("Registration failed:", error.response.data);
            } else if (error instanceof Error) {
                console.error("Registration failed:", error.message);
            } else {
                console.error("Registration failed:", error);
            }
            throw error; // Re-throw for component-level error handling
        }
    }, []);

    // 2. Standard Login
    const login = useCallback(async (email: string, password: string) => {
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
            if (error && typeof error === 'object' && 'response' in error && error.response && typeof error.response === 'object' && 'data' in error.response) {
            
                console.error("Login failed:", error.response.data);
            } else if (error instanceof Error) {
                console.error("Login failed:", error.message);
            } else {
                console.error("Login failed:", error);
            }
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