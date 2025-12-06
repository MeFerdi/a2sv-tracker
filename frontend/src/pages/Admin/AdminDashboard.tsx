import { Link } from 'react-router-dom';
import { useAuth } from '../../utils/Auth.tsx';

const AdminDashboard = () => {
  const {logout } = useAuth();
  
  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Admin Panel Dashboard</h1>
        <button onClick={logout} className="px-4 py-2 bg-red-500 text-white rounded">Logout</button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Card 1: Question Management */}
        <Link to="/admin/questions" className="block p-6 bg-blue-100 shadow rounded-lg hover:bg-blue-200 transition">
          <h2 className="text-2xl font-semibold">📝 Manage Questions</h2>
          <p className="mt-2 text-gray-700">Create, edit, or deactivate questions (CRUD).</p>
        </Link>
        
        {/* Card 2: Applicant Tracker */}
        <Link to="/admin/applicants" className="block p-6 bg-green-100 shadow rounded-lg hover:bg-green-200 transition">
          <h2 className="text-2xl font-semibold">🥇 Applicant Ranking</h2>
          <p className="mt-2 text-gray-700">View rankings, status, and export data.</p>
        </Link>

        {/* Card 3: Token Generation (Optional Placeholder) */}
        <div className="p-6 bg-yellow-100 shadow rounded-lg">
          <h2 className="text-2xl font-semibold">📧 Invitation Utility</h2>
          <p className="mt-2 text-gray-700">Generate and manage invite tokens.</p>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;