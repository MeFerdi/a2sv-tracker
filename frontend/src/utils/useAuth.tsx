import { jwtDecode } from 'jwt-decode';

// Function to decode user data from an access token
export const decodeUser = (token: string) => {
    try {
        const payload = jwtDecode(token) as { user_id: string; email: string; role: string };
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