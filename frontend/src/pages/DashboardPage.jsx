import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getDashboardData } from '../services/platformService';

export default function DashboardPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        const payload = await getDashboardData();
        setData(payload);
      } finally {
        setLoading(false);
      }
    };
    loadDashboard();
  }, []);

  if (loading) return <div className="max-w-6xl mx-auto px-4 py-10">Loading dashboard...</div>;

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 fade-in">
      <div className="bg-white rounded-2xl p-6 shadow-card">
        <p className="text-slate-500 text-sm">Welcome</p>
        <h1 className="text-3xl font-extrabold text-slate-900 mt-1">{user?.name || 'Learner'}</h1>

        <div className="mt-5 grid md:grid-cols-3 gap-4">
          <div className="rounded-xl border border-slate-200 p-4">
            <p className="text-slate-500 text-sm">Current Level</p>
            <span className="inline-block mt-2 px-3 py-1 rounded-full text-sm font-semibold bg-brand-100 text-brand-800">{data.current_level}</span>
          </div>
          <div className="rounded-xl border border-slate-200 p-4">
            <p className="text-slate-500 text-sm">Completed Courses</p>
            <p className="text-2xl font-bold mt-1">{data.progress_stats.completed_count}</p>
          </div>
          <div className="rounded-xl border border-slate-200 p-4">
            <p className="text-slate-500 text-sm">Completion Rate</p>
            <p className="text-2xl font-bold mt-1">{data.progress_stats.completion_rate}%</p>
          </div>
        </div>

        <button onClick={() => navigate('/assessment')} className="mt-6 py-3 px-5 rounded-xl bg-brand-600 text-white font-semibold hover:bg-brand-700 transition">
          Start Assessment
        </button>
      </div>

      <div className="mt-8">
        <h2 className="text-xl font-bold text-slate-900">Completed Courses</h2>
        {data.completed_courses.length === 0 ? (
          <p className="text-slate-600 mt-2">No completed courses yet.</p>
        ) : (
          <div className="mt-3 grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {data.completed_courses.map((course) => (
              <div key={course.id} className="bg-white rounded-xl p-4 border border-slate-200">
                <p className="font-semibold text-slate-900">{course.title}</p>
                <p className="text-sm text-slate-600 mt-1">{course.topic} - {course.difficulty}</p>
                <p className="text-sm text-brand-700 mt-2">Score: {course.score}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
