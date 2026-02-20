import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import api from '../api/axios';

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
  const [failOptions, setFailOptions] = useState([]);
  const [selectedFailOption, setSelectedFailOption] = useState('');
  const [failSubmitted, setFailSubmitted] = useState(false);
  const [retrying, setRetrying] = useState(false);
  const [finalAttemptId, setFinalAttemptId] = useState(null);

  useEffect(() => {
    if (!courseId) {
      navigate('/dashboard');
      return;
    }

    const loadFinal = async () => {
      try {
        const res = await api.post('/final/start', { course_id: Number(courseId) });
        setCourse(res.data.course);
        setQuestions(res.data.questions);
      } catch {
        toast.error('Unable to load final assessment.');
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
      if (finalAttemptId) payload.final_attempt_id = finalAttemptId;

      const res = await api.post('/final/submit', payload);
      setResult(res.data);

      if (!res.data.passed) {
        const optionsRes = await api.get('/feedback/fail-options');
        setFailOptions(optionsRes.data.options || []);
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Unable to submit final assessment.');
    } finally {
      setSubmitting(false);
    }
  };

  const submitFailFeedback = async () => {
    if (!selectedFailOption || !result?.final_attempt_id) {
      toast.error('Please choose one difficulty option.');
      return;
    }

    try {
      await api.post('/feedback/fail-submit', {
        course_id: Number(courseId),
        final_attempt_id: result.final_attempt_id,
        selected_option: selectedFailOption,
      });
      toast.success('Fail feedback saved. You can retry now.');
      setFailSubmitted(true);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Could not save fail feedback.');
    }
  };

  const retryFinal = async () => {
    setRetrying(true);
    try {
      const res = await api.post('/final/retry', { course_id: Number(courseId) });
      setCourse(res.data.course);
      setQuestions(res.data.questions);
      setFinalAttemptId(res.data.final_attempt_id || null);
      setAnswers({});
      setResult(null);
      setSelectedFailOption('');
      setFailSubmitted(false);
      toast.success('Retry loaded.');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Unable to retry final assessment.');
    } finally {
      setRetrying(false);
    }
  };

  if (loading) return <div className="max-w-5xl mx-auto px-4 py-8">Loading final assessment...</div>;

  if (result) {
    return (
      <div className="max-w-3xl mx-auto px-4 py-10 fade-in">
        <div className="rounded-2xl p-8 shadow-card text-center border border-amber-100 bg-gradient-to-br from-white via-amber-50 to-sky-50">
          <p className="text-slate-500">Final Assessment Result</p>
          <h1 className="text-4xl font-extrabold mt-2 text-slate-900">Score: {result.score}%</h1>
          <p className={`mt-3 text-lg font-semibold ${result.passed ? 'text-green-700' : 'text-red-700'}`}>{result.message}</p>

          {result.passed ? (
            <button onClick={() => navigate(`/feedback?course_id=${courseId}`)} className="mt-6 py-3 px-6 rounded-xl bg-emerald-600 text-white font-semibold">
              Give Feedback
            </button>
          ) : (
            <div className="mt-6 text-left">
              <h2 className="text-lg font-bold text-slate-900">Difficulty Faced</h2>
              <p className="text-sm text-slate-600 mt-1">Select what blocked you most before retrying.</p>
              <div className="mt-3 grid gap-2">
                {failOptions.map((opt) => (
                  <label key={opt} className="rounded-lg border border-slate-200 px-3 py-2 flex items-center gap-2">
                    <input type="radio" name="fail-option" checked={selectedFailOption === opt} onChange={() => setSelectedFailOption(opt)} />
                    <span>{opt}</span>
                  </label>
                ))}
              </div>

              {!failSubmitted ? (
                <button onClick={submitFailFeedback} className="mt-4 py-2 px-4 rounded-lg bg-amber-600 text-white font-semibold">
                  Submit Difficulty Feedback
                </button>
              ) : (
                <button onClick={retryFinal} disabled={retrying} className="mt-4 py-2 px-4 rounded-lg bg-orange-600 text-white font-semibold disabled:bg-slate-400">
                  {retrying ? 'Loading Retry...' : 'Retry Final Assessment'}
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="rounded-2xl p-6 shadow-card slide-up border border-sky-100 bg-gradient-to-br from-white via-sky-50 to-emerald-50">
        <h1 className="text-2xl font-bold text-slate-900">Final Assessment</h1>
        <p className="text-slate-600 mt-1">{course?.title}</p>

        <div className="w-full h-2 bg-slate-200 rounded-full mt-4 overflow-hidden">
          <div className="h-full bg-emerald-600 transition-all" style={{ width: `${completionPct}%` }} />
        </div>

        <div className="mt-6 grid gap-5">
          {questions.map((q, idx) => (
            <div key={q.id} className="rounded-xl border border-slate-200 p-4">
              <p className="font-semibold text-slate-900">Q{idx + 1}. {q.text}</p>
              <div className="mt-3 grid gap-2">
                {['a', 'b', 'c', 'd'].map((opt) => (
                  <button key={opt} onClick={() => setAnswers((prev) => ({ ...prev, [q.id]: opt }))} className={`text-left px-3 py-2 border rounded-lg ${answers[q.id] === opt ? 'border-emerald-600 bg-emerald-50' : 'border-slate-200 bg-white/90'}`}>
                    <span className="uppercase font-semibold mr-2">{opt}.</span>
                    {q[`option_${opt}`]}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>

        <button onClick={submit} disabled={submitting} className="mt-6 py-3 px-5 rounded-xl bg-emerald-600 text-white font-semibold disabled:bg-slate-400">
          {submitting ? 'Submitting...' : 'Submit Final Assessment'}
        </button>
      </div>
    </div>
  );
}
