import React from 'react';
import LoginForm from '../../components/auth/LoginForm'; // Import the new component
const LoginPage = () => {
  return (
    <div className="flex justify-center items-center min-h-screen bg-gray-50">
      <div className="w-full max-w-md p-8 bg-white shadow-xl rounded-lg border border-gray-200">
        <h2 className="text-3xl font-extrabold mb-6 text-center text-gray-800">
          Sign In to A2SV Tracker
        </h2>
        
        <LoginForm />
        
        <p className="text-center text-sm text-gray-500 mt-6">
          Trouble logging in? Contact the A2SV team.
        </p>
      </div>
    </div>
  );
};

export default LoginPage;