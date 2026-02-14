import { useEffect, useState } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { getResult } from '../services/platformService';

export default function ResultPage() {
  const { attemptId } = useParams();
  const { state } = useLocation();
  const navigate = useNavigate();
  const [data, setData] = useState(state || null);
  const [selectedCourse, setSelectedCourse] = useState(null);

  useEffect(() => {
    const loadResult = async () => {
      if (data) {
        if (data.recommended_courses?.length) setSelectedCourse(data.recommended_courses[0]);
        return;
      }
      const payload = await getResult(attemptId);
      setData(payload);
      if (payload.recommended_courses?.length) setSelectedCourse(payload.recommended_courses[0]);
    };
    loadResult();
  }, [attemptId]);

  if (!data) return <div className="max-w-5xl mx-auto px-4 py-8">Loading result...</div>;

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 fade-in">
      <div className="bg-white rounded-2xl p-8 shadow-card">
        <p className="text-slate-500 text-sm">Assessment Result</p>
        <h1 className="text-5xl font-extrabold text-brand-700 mt-2">{data.overall_points}/100</h1>
        <p className="mt-3 text-lg text-slate-700">Current Level: <span className="font-semibold">{data.current_level}</span></p>

        <h2 className="text-2xl font-bold text-slate-900 mt-8">Recommended Courses</h2>
        <div className="mt-4 grid gap-4">
          {data.recommended_courses.map((course) => (
            <div key={course.id} className={`rounded-xl border p-4 cursor-pointer transition ${selectedCourse?.id === course.id ? 'border-brand-600 bg-brand-50' : 'border-slate-200 bg-white'}`} onClick={() => setSelectedCourse(course)}>
              <p className="font-semibold text-slate-900">{course.title}</p>
              <p className="text-sm text-slate-600 mt-1">{course.topic} - {course.difficulty}</p>
              <p className="text-sm text-slate-700 mt-2"><span className="font-semibold">Why recommended:</span> {course.why_recommended}</p>
            </div>
          ))}
        </div>

        <button disabled={!selectedCourse} onClick={() => navigate(`/final-assessment?course_id=${selectedCourse.id}`)} className="mt-6 py-3 px-6 rounded-xl bg-slate-900 text-white font-semibold disabled:bg-slate-400">
          Start Final Assessment
        </button>
      </div>
    </div>
  );
}
