import React from 'react';
import { Link } from 'react-router-dom';

const NotFound = () => {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen text-center">
      <h1 className="text-9xl font-extrabold text-blue-600">404</h1>
      <p className="text-2xl font-semibold mt-4">Page Not Found</p>
      <p className="text-gray-600 mt-2">The page you are looking for does not exist.</p>
      <Link to="/" className="mt-6 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition">
        Go Home
      </Link>
    </div>
  );
};

export default NotFound;