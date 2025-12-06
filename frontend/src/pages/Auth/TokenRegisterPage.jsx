import React from 'react';
import TokenRegisterForm from '../../components/auth/TokenRegisterForm'; // Import the new component

const TokenRegisterPage = () => {
  return (
    <div className="flex justify-center items-center min-h-screen bg-gray-50">
      <div className="w-full max-w-md p-8 bg-white shadow-xl rounded-lg border border-gray-200">
        <h2 className="text-3xl font-extrabold mb-6 text-center text-gray-800">
          A2SV Tracker Setup
        </h2>
        <p className="text-center text-gray-600 mb-6">
          Set your name and password to finalize your account.
        </p>
        
        <TokenRegisterForm />
        
        <p className="text-center text-sm text-gray-400 mt-6">
          Your email is securely linked via the invitation token.
        </p>
      </div>
    </div>
  );
};

export default TokenRegisterPage;