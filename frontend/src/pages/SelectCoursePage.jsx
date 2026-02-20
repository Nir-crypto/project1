import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';

function matchScore(course, interests) {
  if (!interests?.length) return 0;
  const courseTopic = (course.topic || '').toLowerCase();
  return interests.reduce((acc, item) => {
    const v = (item.name || '').toLowerCase();
    if (!v) return acc;
    if (courseTopic.includes(v) || v.includes(courseTopic)) return acc + 2;
    if (v.includes('web') && courseTopic.includes('web')) return acc + 1;
    if (v.includes('python') && courseTopic.includes('python')) return acc + 1;
    if (v.includes('java') && courseTopic.includes('java')) return acc + 1;
    return acc;
  }, 0);
}

export default function SelectCoursePage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [courses, setCourses] = useState([]);
  const [selectedCourseId, setSelectedCourseId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [starting, setStarting] = useState(false);

  useEffect(() => {
    const loadCourses = async () => {
      try {
        const res = await api.get('/courses');
        setCourses(res.data || []);
      } catch {
        toast.error('Unable to load courses.');
      } finally {
        setLoading(false);
      }
    };
    loadCourses();
  }, []);

  const rankedCourses = useMemo(() => {
    return [...courses]
      .map((course) => ({ ...course, _score: matchScore(course, user?.interests || []) }))
      .sort((a, b) => b._score - a._score);
  }, [courses, user]);

  const startAssessment = async () => {
    if (!selectedCourseId) {
      toast.error('Please select one course.');
      return;
    }

    setStarting(true);
    try {
      const res = await api.post('/assessment/start', { selected_course_id: selectedCourseId });
      navigate('/assessment', { state: res.data });
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Could not start assessment.');
    } finally {
      setStarting(false);
    }
  };

  if (loading) return <div className="max-w-6xl mx-auto px-4 py-10">Loading courses...</div>;

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 fade-in">
      <div className="rounded-2xl p-6 shadow-card border border-amber-100 bg-gradient-to-br from-white via-amber-50 to-sky-50">
        <h1 className="text-2xl font-bold text-slate-900">Select Course</h1>
        <p className="text-slate-600 mt-1">Choose one course to begin your adaptive quiz.</p>

        <div className="mt-6 grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {rankedCourses.map((course) => (
            <button
              key={course.id}
              type="button"
              onClick={() => setSelectedCourseId(course.id)}
              className={`text-left rounded-xl border p-4 transition ${selectedCourseId === course.id ? 'border-emerald-600 bg-emerald-50' : 'border-slate-200 bg-white/90 hover:border-emerald-400'}`}
            >
              <p className="font-semibold text-slate-900">{course.title}</p>
              <p className="text-sm text-slate-600 mt-1">{course.topic} - {course.difficulty}</p>
              <p className="text-sm text-slate-700 mt-2">{course.description}</p>
            </button>
          ))}
        </div>

        <button
          onClick={startAssessment}
          disabled={starting || !selectedCourseId}
          className="mt-6 py-3 px-5 rounded-xl bg-emerald-600 text-white font-semibold disabled:bg-slate-400"
        >
          {starting ? 'Starting...' : 'Start Adaptive Quiz'}
        </button>
      </div>
    </div>
  );
}
