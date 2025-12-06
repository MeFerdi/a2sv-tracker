import axios from 'axios';

// 1. Define the Base URL
const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const axiosInstance = axios.create({
    baseURL: BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// 2. Request Interceptor: Attach Access Token

axiosInstance.interceptors.request.use(
    async (config) => {
        const accessToken = localStorage.getItem('access');
        
        // If an access token exists, attach it to the request headers
        if (accessToken) {
            config.headers.Authorization = `Bearer ${accessToken}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// 3. Response Interceptor: Handle Token Refresh (401 Error)
axiosInstance.interceptors.response.use(
    (response) => {
        // If the request was successful, just return the response
        return response;
    },
    async (error) => {
        const originalRequest = error.config;
        
        // Check for 401 Unauthorized error AND ensure it hasn't been retried already
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            
            const refreshToken = localStorage.getItem('refresh');
            
            // Check if a refresh token exists and hasn't expired
            if (!refreshToken) {
                // No refresh token, or it expired. Redirect to login.
                localStorage.clear();
                window.location.href = '/login'; // Use your actual login route
                return Promise.reject(error);
            }

            try {
                // Attempt to get a new access token using the refresh token
                const response = await axios.post(`${BASE_URL}/auth/token/refresh/`, {
                    refresh: refreshToken,
                });

                const { access, refresh } = response.data;
                
                // Store the new tokens
                localStorage.setItem('access', access);
                // The refresh token may also be rotated; store the new one if provided
                if (refresh) {
                     localStorage.setItem('refresh', refresh);
                }

                // Update the header of the original failed request with the new access token
                originalRequest.headers.Authorization = `Bearer ${access}`;

                // Re-run the original request
                return axios(originalRequest);
                
            } catch (refreshError) {
                // Refresh failed (e.g., refresh token is invalid or expired)
                localStorage.clear();
                window.location.href = '/login'; // Force re-login
                return Promise.reject(refreshError);
            }
        }

        // For other errors (or if the request was already retried), reject the promise
        return Promise.reject(error);
    }
);

export default axiosInstance;