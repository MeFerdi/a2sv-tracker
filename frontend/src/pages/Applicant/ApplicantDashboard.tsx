import { useAuth } from '../../utils/Auth.tsx'; // Import context for user info
// import QuestionList from '@/components/dashboard/QuestionList';
// import FinalizeButton from '@/components/dashboard/FinalizeButton';

const ApplicantDashboard = () => {
  const { user, logout } = useAuth();
  
  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Welcome, {user?.email || 'Applicant'}!</h1>
        <button onClick={logout} className="px-4 py-2 bg-red-500 text-white rounded">Logout</button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Progress Card */}
        <div className="md:col-span-1 p-6 bg-white shadow rounded-lg">
          <h3 className="text-xl font-semibold mb-3">Progress</h3>
          <p>Total Solved: 0/40</p>
          <p>Mandatory Solved: 0/15</p>
        </div>

        {/* Question List Area */}
        <div className="md:col-span-2">
          <h3 className="text-2xl font-semibold mb-4 border-b pb-2">Problem Set</h3>
          {/* Placeholder for Mandatory/Recommended Tabs */}
          <p>Questions will be displayed here, fetched from /api/questions/</p>
        </div>
      </div>

      <div className="mt-8">
        {/* Placeholder for Finalize Button */}
        <p>Finalize Submission button logic here.</p>
      </div>
    </div>
  );
};

export default ApplicantDashboard;