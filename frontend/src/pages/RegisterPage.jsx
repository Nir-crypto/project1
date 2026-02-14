import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';
import { getInterests } from '../services/platformService';

export default function RegisterPage() {
  const navigate = useNavigate();
  const { register } = useAuth();

  const [interests, setInterests] = useState([]);
  const [selected, setSelected] = useState([]);
  const [form, setForm] = useState({ name: '', email: '', password: '' });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

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

  const toggleInterest = (id) => {
    setSelected((prev) => (prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]));
  };

  const validate = () => {
    const next = {};
    if (!form.name.trim()) next.name = 'Name is required.';
    if (!form.email.trim()) next.email = 'Email is required.';
    if (!form.password || form.password.length < 6) next.password = 'Password must be at least 6 characters.';
    if (selected.length < 2) next.interests = 'Select at least 2 interests.';
    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const submit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    setLoading(true);
    try {
      await register({ name: form.name, email: form.email, password: form.password, interests: selected });
      toast.success('Account created. Please login.');
      navigate('/login');
    } catch (error) {
      toast.error(error?.message || 'Registration failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-10">
      <form onSubmit={submit} className="bg-white rounded-2xl p-8 shadow-card slide-up">
        <h2 className="text-2xl font-bold text-slate-900">Create Account</h2>
        <p className="text-slate-600 mt-1">Set up your profile and pick your interests.</p>

        <div className="grid md:grid-cols-2 gap-4 mt-6">
          <div>
            <label className="block text-sm text-slate-700 mb-1">Name</label>
            <input type="text" className="w-full border border-slate-300 rounded-lg px-3 py-2" value={form.name} onChange={(e) => setForm((prev) => ({ ...prev, name: e.target.value }))} />
            {errors.name && <p className="text-red-600 text-sm mt-1">{errors.name}</p>}
          </div>

          <div>
            <label className="block text-sm text-slate-700 mb-1">Email</label>
            <input type="email" className="w-full border border-slate-300 rounded-lg px-3 py-2" value={form.email} onChange={(e) => setForm((prev) => ({ ...prev, email: e.target.value }))} />
            {errors.email && <p className="text-red-600 text-sm mt-1">{errors.email}</p>}
          </div>
        </div>

        <div className="mt-4">
          <label className="block text-sm text-slate-700 mb-1">Password</label>
          <input type="password" className="w-full border border-slate-300 rounded-lg px-3 py-2" value={form.password} onChange={(e) => setForm((prev) => ({ ...prev, password: e.target.value }))} />
          {errors.password && <p className="text-red-600 text-sm mt-1">{errors.password}</p>}
        </div>

        <div className="mt-6">
          <p className="text-sm font-semibold text-slate-700">Select at least 2 interests</p>
          <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-3 mt-3">
            {interests.map((item) => (
              <label key={item.id} className="border border-slate-300 rounded-lg px-3 py-2 flex gap-2 items-center text-sm">
                <input type="checkbox" checked={selected.includes(item.id)} onChange={() => toggleInterest(item.id)} />
                {item.name}
              </label>
            ))}
          </div>
          {errors.interests && <p className="text-red-600 text-sm mt-1">{errors.interests}</p>}
        </div>

        <button disabled={loading} type="submit" className="mt-6 w-full py-3 rounded-xl bg-brand-600 text-white font-semibold disabled:bg-slate-400">
          {loading ? 'Creating Account...' : 'Create Account'}
        </button>

        <p className="text-sm text-slate-600 mt-4 text-center">
          Already have an account? <Link to="/login" className="text-brand-700 font-semibold">Login</Link>
        </p>
      </form>
    </div>
  );
}
