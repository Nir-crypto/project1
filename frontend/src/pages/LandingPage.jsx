import { Link } from 'react-router-dom';

export default function LandingPage() {
  return (
    <div className="min-h-[calc(100vh-64px)]" style={{ background: 'var(--bg-gradient)' }}>
      <div className="max-w-6xl mx-auto px-4 py-14 md:py-24">
        <div className="grid lg:grid-cols-2 gap-8 items-center">
          <div className="text-white fade-in">
            <p className="uppercase tracking-[0.2em] text-sm text-blue-100">Reward-Based Erudition Platform</p>
            <h1 className="text-4xl md:text-6xl font-extrabold leading-tight mt-3">
              Adaptive Assessment.
              <span className="block text-cyan-200">Smarter Skill Growth.</span>
            </h1>
            <p className="mt-5 text-lg text-blue-100 max-w-xl">
              Assess one question at a time, predict your skill level with ML, and get high-fit course recommendations.
            </p>
          </div>

          <div className="bg-white rounded-2xl p-8 shadow-card slide-up">
            <h2 className="text-2xl font-bold text-slate-900">Start your learning journey</h2>
            <p className="mt-2 text-slate-600">Create your account or log in to continue.</p>
            <div className="mt-6 grid gap-3">
              <Link to="/register" className="w-full py-3 rounded-xl bg-brand-600 text-white text-center font-semibold hover:bg-brand-700 transition">
                Create Account
              </Link>
              <Link to="/login" className="w-full py-3 rounded-xl border border-slate-300 text-slate-800 text-center font-semibold hover:bg-slate-100 transition">
                Login
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
