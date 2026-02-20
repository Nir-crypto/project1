import { useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import api from '../api/axios';

export default function AssessmentPage() {
  const navigate = useNavigate();
  const { state } = useLocation();

  const [attemptId, setAttemptId] = useState(state?.attempt_id || null);
  const [question, setQuestion] = useState(state?.question || null);
  const [selectedOption, setSelectedOption] = useState('');
  const [progress, setProgress] = useState(state?.progress || { index: 0, total: 10 });
  const [answering, setAnswering] = useState(false);
  const [questionStartTime, setQuestionStartTime] = useState(Date.now());

  useEffect(() => {
    if (!attemptId || !question) {
      navigate('/select-course');
    }
  }, [attemptId, question]);

  const progressPct = useMemo(() => {
    if (!progress.total) return 0;
    return Math.round((Math.max(progress.index - 1, 0) / progress.total) * 100);
  }, [progress]);

  const submitAnswer = async () => {
    if (!selectedOption || !attemptId || !question) return;
    setAnswering(true);

    const elapsed = Math.max(1, Math.round((Date.now() - questionStartTime) / 1000));
    try {
      const res = await api.post('/assessment/answer', {
        attempt_id: attemptId,
        question_id: question.id,
        selected_option: selectedOption,
        time_spent: elapsed,
      });

      if (res.data.done) {
        navigate(`/result/${attemptId}`, { state: res.data });
        return;
      }

      toast.success(res.data.is_correct ? 'Correct! Difficulty increased.' : 'Incorrect. Difficulty adjusted down.');
      setQuestion(res.data.next_question);
      setProgress(res.data.progress);
      setSelectedOption('');
      setQuestionStartTime(Date.now());
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Could not submit answer.');
    } finally {
      setAnswering(false);
    }
  };

  if (!attemptId || !question) return null;

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="rounded-2xl shadow-card p-6 slide-up border border-sky-100 bg-gradient-to-br from-white via-sky-50 to-emerald-50">
        <h1 className="text-2xl font-bold text-slate-900">Adaptive Assessment</h1>
        <p className="text-slate-600 mt-1">One question at a time. Difficulty adjusts after every answer.</p>

        <div className="mt-6 fade-in">
          <p className="text-sm text-slate-600">Question {progress.index} of {progress.total}</p>
          <div className="w-full h-2 bg-slate-200 rounded-full mt-2 overflow-hidden">
            <div className="h-full bg-emerald-600 transition-all duration-500" style={{ width: `${progressPct}%` }} />
          </div>

          <h2 className="mt-5 text-lg font-semibold text-slate-900">{question.text}</h2>
          <div className="mt-4 grid gap-3">
            {['a', 'b', 'c', 'd'].map((opt) => (
              <button key={opt} onClick={() => setSelectedOption(opt)} className={`text-left border rounded-xl px-4 py-3 transition ${selectedOption === opt ? 'border-emerald-600 bg-emerald-50' : 'border-slate-200 bg-white/90 hover:border-emerald-400'}`}>
                <span className="uppercase font-semibold mr-2">{opt}.</span>
                {question[`option_${opt}`]}
              </button>
            ))}
          </div>

          <button onClick={submitAnswer} disabled={!selectedOption || answering} className="mt-6 py-3 px-5 rounded-xl bg-emerald-600 text-white font-semibold disabled:bg-slate-400">
            {answering ? 'Submitting...' : 'Submit Answer'}
          </button>
        </div>
      </div>
    </div>
  );
}
