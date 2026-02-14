import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import { startFinalAssessment, submitFinalAssessment } from '../services/platformService';

export default function FinalAssessmentPage() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const courseId = params.get('course_id');

  const [course, setCourse] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);

  useEffect(() => {
    if (!courseId) {
      navigate('/dashboard');
      return;
    }

    const loadFinal = async () => {
      try {
        const data = await startFinalAssessment(Number(courseId));
        setCourse(data.course);
        setQuestions(data.questions);
      } catch (error) {
        toast.error(error?.message || 'Unable to load final assessment.');
      } finally {
        setLoading(false);
      }
    };

    loadFinal();
  }, [courseId]);

  const completionPct = useMemo(() => {
    if (!questions.length) return 0;
    return Math.round((Object.keys(answers).length / questions.length) * 100);
  }, [answers, questions]);

  const submit = async () => {
    if (Object.keys(answers).length < questions.length) {
      toast.error('Please answer all questions before submitting.');
      return;
    }

    setSubmitting(true);
    try {
      const payload = {
        course_id: Number(courseId),
        answers: questions.map((q) => ({ question_id: q.id, selected_option: answers[q.id] })),
      };
      const data = await submitFinalAssessment(payload);
      setResult(data);
    } catch (error) {
      toast.error(error?.message || 'Unable to submit final assessment.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <div className="max-w-5xl mx-auto px-4 py-8">Loading final assessment...</div>;

  if (result) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-10 fade-in">
        <div className="bg-white rounded-2xl p-8 shadow-card text-center">
          <p className="text-slate-500">Final Assessment Result</p>
          <h1 className="text-4xl font-extrabold mt-2 text-slate-900">Score: {result.score}%</h1>
          <p className={`mt-3 text-lg font-semibold ${result.passed ? 'text-green-700' : 'text-red-700'}`}>{result.message}</p>

          {!result.passed ? (
            <button onClick={() => window.location.reload()} className="mt-6 py-3 px-6 rounded-xl bg-brand-600 text-white font-semibold">
              Try again
            </button>
          ) : (
            <button onClick={() => navigate(`/feedback?course_id=${courseId}`)} className="mt-6 py-3 px-6 rounded-xl bg-slate-900 text-white font-semibold">
              Give Feedback
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="bg-white rounded-2xl p-6 shadow-card slide-up">
        <h1 className="text-2xl font-bold text-slate-900">Final Assessment</h1>
        <p className="text-slate-600 mt-1">{course?.title}</p>

        <div className="w-full h-2 bg-slate-200 rounded-full mt-4 overflow-hidden">
          <div className="h-full bg-brand-600 transition-all" style={{ width: `${completionPct}%` }} />
        </div>

        <div className="mt-6 grid gap-5">
          {questions.map((q, idx) => (
            <div key={q.id} className="rounded-xl border border-slate-200 p-4">
              <p className="font-semibold text-slate-900">Q{idx + 1}. {q.text}</p>
              <div className="mt-3 grid gap-2">
                {['a', 'b', 'c', 'd'].map((opt) => (
                  <button key={opt} onClick={() => setAnswers((prev) => ({ ...prev, [q.id]: opt }))} className={`text-left px-3 py-2 border rounded-lg ${answers[q.id] === opt ? 'border-brand-600 bg-brand-50' : 'border-slate-200'}`}>
                    <span className="uppercase font-semibold mr-2">{opt}.</span>
                    {q[`option_${opt}`]}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>

        <button onClick={submit} disabled={submitting} className="mt-6 py-3 px-5 rounded-xl bg-slate-900 text-white font-semibold disabled:bg-slate-400">
          {submitting ? 'Submitting...' : 'Submit Final Assessment'}
        </button>
      </div>
    </div>
  );
}
