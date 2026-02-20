import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import api from '../api/axios';

export default function FeedbackPage() {
  const [params] = useSearchParams();
  const courseId = params.get('course_id');
  const navigate = useNavigate();

  const [questions, setQuestions] = useState([]);
  const [responses, setResponses] = useState({});
  const [comment, setComment] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    if (!courseId) {
      navigate('/dashboard');
      return;
    }

    const loadQuestions = async () => {
      try {
        const res = await api.get('/feedback/questions');
        setQuestions(res.data);
      } catch {
        toast.error('Unable to load feedback questions.');
      } finally {
        setLoading(false);
      }
    };
    loadQuestions();
  }, [courseId]);

  const submit = async () => {
    const unanswered = questions.some((q) => !responses[q.id]);
    if (unanswered) {
      toast.error('Please answer all feedback questions.');
      return;
    }

    setSubmitting(true);
    try {
      await api.post('/feedback/submit', { course_id: Number(courseId), responses, comment });
      setSubmitted(true);
      toast.success('Thanks for your feedback.');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Could not submit feedback.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <div className="max-w-4xl mx-auto px-4 py-8">Loading feedback page...</div>;

  if (submitted) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-10 fade-in">
        <div className="bg-white rounded-2xl p-8 shadow-card text-center">
          <h1 className="text-3xl font-bold text-slate-900">Feedback Submitted</h1>
          <p className="mt-2 text-slate-600">Your responses were saved successfully.</p>
          <button onClick={() => navigate('/dashboard')} className="mt-6 py-3 px-5 rounded-xl bg-brand-600 text-white font-semibold">
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 slide-up">
      <div className="bg-white rounded-2xl p-6 shadow-card">
        <h1 className="text-2xl font-bold text-slate-900">Course Feedback</h1>
        <p className="text-slate-600 mt-1">This form is shown only after a passed final assessment.</p>

        <div className="mt-6 grid gap-5">
          {questions.map((q) => (
            <div key={q.id} className="border border-slate-200 rounded-xl p-4">
              <p className="font-semibold text-slate-900">{q.question_text}</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {(q.options || []).map((opt) => (
                  <button key={opt} onClick={() => setResponses((prev) => ({ ...prev, [q.id]: opt }))} className={`px-3 py-2 rounded-lg border ${responses[q.id] === opt ? 'border-brand-600 bg-brand-50' : 'border-slate-200'}`}>
                    {opt}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-5">
          <label className="block text-sm text-slate-700 mb-1">Optional Comment</label>
          <textarea className="w-full border border-slate-300 rounded-lg px-3 py-2 min-h-28" value={comment} onChange={(e) => setComment(e.target.value)} placeholder="Share your suggestions..." />
        </div>

        <button onClick={submit} disabled={submitting} className="mt-6 py-3 px-5 rounded-xl bg-slate-900 text-white font-semibold disabled:bg-slate-400">
          {submitting ? 'Submitting...' : 'Submit Feedback'}
        </button>
      </div>
    </div>
  );
}
