import { useEffect, useState } from 'react';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import api from '../api/axios';

export default function ResultPage() {
  const { attemptId } = useParams();
  const { state } = useLocation();
  const navigate = useNavigate();
  const [data, setData] = useState(state || null);
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [openRoadmap, setOpenRoadmap] = useState(null);

  useEffect(() => {
    const loadResult = async () => {
      if (data) {
        if (data.recommended_courses?.length) setSelectedCourse(data.recommended_courses[0]);
        return;
      }
      const res = await api.get(`/result/${attemptId}`);
      setData(res.data);
      if (res.data.recommended_courses?.length) setSelectedCourse(res.data.recommended_courses[0]);
    };
    loadResult();
  }, [attemptId]);

  if (!data) return <div className="max-w-5xl mx-auto px-4 py-8">Loading result...</div>;

  const recommendedCourses = (data.recommended_courses || []).slice(0, 3);
  const canStartFinal = Boolean(selectedCourse);

  return (
    <div className="max-w-5xl mx-auto px-4 py-8 fade-in">
      <div className="rounded-2xl p-8 shadow-card border border-amber-100 bg-gradient-to-br from-white via-rose-50 to-amber-50">
        <p className="text-slate-500 text-sm">Assessment Result</p>
        <h1 className="text-5xl font-extrabold text-orange-600 mt-2">{data.overall_points}/100</h1>
        <p className="mt-3 text-lg text-slate-700">Current Level: <span className="font-semibold">{data.current_level}</span></p>

        <h2 className="text-2xl font-bold text-slate-900 mt-8">Recommended Courses</h2>
        <div className="mt-4 grid gap-4">
          {recommendedCourses.length === 0 && <p className="text-slate-700">No recommendation available right now.</p>}
          {recommendedCourses.map((course) => (
            <div
              key={course.id}
              className={`rounded-xl border bg-white/90 p-4 ${
                selectedCourse?.id === course.id ? 'border-orange-300' : 'border-amber-200'
              }`}
            >
              <button className="w-full text-left" onClick={() => setSelectedCourse(course)}>
                <p className="font-semibold text-slate-900">{course.title}</p>
                <p className="text-sm text-slate-600 mt-1">{course.topic} - {course.difficulty}</p>
                <p className="text-sm text-slate-700 mt-2"><span className="font-semibold">Why recommended:</span> {course.why_recommended}</p>
              </button>

              <button
                onClick={() => setOpenRoadmap(openRoadmap === course.id ? null : course.id)}
                className="mt-3 text-sm text-orange-700 font-semibold"
              >
                {openRoadmap === course.id ? 'Hide Roadmap' : 'View Roadmap'}
              </button>

              {openRoadmap === course.id && course.roadmap?.steps?.length > 0 && (
                <div className="mt-3 border-t border-amber-200 pt-3 grid gap-2">
                  {course.roadmap.steps.map((step) => (
                    <div key={`${course.id}-${step.step_no}`} className="rounded-lg border border-amber-100 p-3 bg-white">
                      <p className="font-semibold text-slate-900">Step {step.step_no}: {step.title}</p>
                      <p className="text-sm text-slate-700 mt-1">{step.description}</p>
                      <p className="text-xs text-slate-600 mt-1">Outcome: {step.outcome}</p>
                      <p className="text-xs text-slate-600 mt-1">Est. Time: {step.est_time_hours} hrs</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        <button
          disabled={!canStartFinal}
          onClick={() => navigate(`/final-assessment?course_id=${selectedCourse.id}`)}
          className="mt-6 py-3 px-6 rounded-xl bg-orange-600 text-white font-semibold disabled:bg-slate-400"
        >
          Start Final Assessment
        </button>
      </div>
    </div>
  );
}
