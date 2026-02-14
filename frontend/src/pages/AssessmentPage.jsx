import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { answerAssessment, getInterests, startAssessment as startAssessmentRequest } from '../services/platformService';

export default function AssessmentPage() {
  const navigate = useNavigate();
  const [interests, setInterests] = useState([]);
  const [interestId, setInterestId] = useState('');
  const [attemptId, setAttemptId] = useState(null);
  const [question, setQuestion] = useState(null);
  const [selectedOption, setSelectedOption] = useState('');
  const [progress, setProgress] = useState({ index: 0, total: 10 });
  const [loading, setLoading] = useState(false);
  const [answering, setAnswering] = useState(false);
  const [questionStartTime, setQuestionStartTime] = useState(null);

  useEffect(() => {
    const loadInterests = async () => {
      try {
        const data = await getInterests();
        setInterests(data);
      } catch (error) {
        toast.error(error?.message || 'Unable to load interests.');
      }
    };
    loadInterests();
  }, []);

  const progressPct = useMemo(() => {
    if (!progress.total) return 0;
    return Math.round((Math.max(progress.index - 1, 0) / progress.total) * 100);
  }, [progress]);

  const startAssessment = async () => {
    if (!interestId) {
      toast.error('Please select an interest first.');
      return;
    }

    setLoading(true);
    try {
      const data = await startAssessmentRequest(Number(interestId));
      setAttemptId(data.attempt_id);
      setQuestion(data.question);
      setProgress(data.progress);
      setQuestionStartTime(Date.now());
      setSelectedOption('');
    } catch (error) {
      toast.error(error?.message || 'Unable to start assessment.');
    } finally {
      setLoading(false);
    }
  };

  const submitAnswer = async () => {
    if (!selectedOption || !attemptId || !question) return;
    setAnswering(true);

    const elapsed = Math.max(1, Math.round((Date.now() - questionStartTime) / 1000));
    try {
      const data = await answerAssessment({
        attempt_id: attemptId,
        question_id: question.id,
        selected_option: selectedOption,
        time_spent: elapsed,
      });

      if (data.done) {
        navigate(`/result/${attemptId}`, { state: data });
        return;
      }

      toast.success(data.is_correct ? 'Correct! Difficulty increased.' : 'Incorrect. Difficulty adjusted down.');
      setQuestion(data.next_question);
      setProgress(data.progress);
      setSelectedOption('');
      setQuestionStartTime(Date.now());
    } catch (error) {
      toast.error(error?.message || 'Could not submit answer.');
    } finally {
      setAnswering(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="bg-white rounded-2xl shadow-card p-6 slide-up">
        <h1 className="text-2xl font-bold text-slate-900">Adaptive Assessment</h1>
        <p className="text-slate-600 mt-1">One question at a time. Difficulty adjusts after every answer.</p>

        {!attemptId && (
          <div className="mt-6">
            <label className="block text-sm text-slate-700 mb-2">Choose Interest</label>
            <select value={interestId} onChange={(e) => setInterestId(e.target.value)} className="w-full border border-slate-300 rounded-lg px-3 py-2">
              <option value="">Select an interest</option>
              {interests.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
            </select>
            <button onClick={startAssessment} disabled={loading} className="mt-4 py-3 px-5 rounded-xl bg-brand-600 text-white font-semibold disabled:bg-slate-400">
              {loading ? 'Starting...' : 'Start Assessment'}
            </button>
          </div>
        )}

        {attemptId && question && (
          <div className="mt-6 fade-in">
            <p className="text-sm text-slate-600">Question {progress.index} of {progress.total}</p>
            <div className="w-full h-2 bg-slate-200 rounded-full mt-2 overflow-hidden">
              <div className="h-full bg-brand-600 transition-all duration-500" style={{ width: `${progressPct}%` }} />
            </div>

            <h2 className="mt-5 text-lg font-semibold text-slate-900">{question.text}</h2>
            <div className="mt-4 grid gap-3">
              {['a', 'b', 'c', 'd'].map((opt) => (
                <button key={opt} onClick={() => setSelectedOption(opt)} className={`text-left border rounded-xl px-4 py-3 transition ${selectedOption === opt ? 'border-brand-600 bg-brand-50' : 'border-slate-200 hover:border-slate-400'}`}>
                  <span className="uppercase font-semibold mr-2">{opt}.</span>
                  {question[`option_${opt}`]}
                </button>
              ))}
            </div>

            <button onClick={submitAnswer} disabled={!selectedOption || answering} className="mt-6 py-3 px-5 rounded-xl bg-slate-900 text-white font-semibold disabled:bg-slate-400">
              {answering ? 'Submitting...' : 'Submit Answer'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
