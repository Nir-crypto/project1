import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';

export default function LoginPage() {
  const { login, refreshUser } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(form.email, form.password);
      await refreshUser();
      toast.success('Login successful.');
      navigate('/dashboard');
    } catch (error) {
      const detail = error.response?.data?.detail || error.message || 'Invalid email or password.';
      toast.error(typeof detail === 'string' ? detail : 'Invalid email or password.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto px-4 py-12">
      <form onSubmit={submit} className="rounded-2xl border border-sky-100 bg-gradient-to-br from-white via-sky-50 to-amber-50 p-8 shadow-card slide-up">
        <h2 className="text-2xl font-bold text-slate-900">Login</h2>
        <p className="text-slate-600 mt-1">Continue your adaptive learning journey.</p>

        <div className="mt-5">
          <label className="block text-sm text-slate-700 mb-1">Email</label>
          <input type="email" className="w-full border border-slate-300 rounded-lg px-3 py-2" value={form.email} onChange={(e) => setForm((prev) => ({ ...prev, email: e.target.value }))} required />
        </div>

        <div className="mt-4">
          <label className="block text-sm text-slate-700 mb-1">Password</label>
          <input type="password" className="w-full border border-slate-300 rounded-lg px-3 py-2" value={form.password} onChange={(e) => setForm((prev) => ({ ...prev, password: e.target.value }))} required />
        </div>

        <button disabled={loading} type="submit" className="mt-6 w-full py-3 rounded-xl bg-orange-600 text-white font-semibold disabled:bg-slate-400">
          {loading ? 'Logging in...' : 'Login'}
        </button>

        <p className="text-sm text-slate-600 mt-4 text-center">
          New user? <Link to="/register" className="text-brand-700 font-semibold">Create Account</Link>
        </p>
      </form>
    </div>
  );
}
