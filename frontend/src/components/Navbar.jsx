import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  return (
    <header className="sticky top-0 z-40 bg-gradient-to-r from-white/95 via-sky-50/95 to-amber-50/95 backdrop-blur border-b border-slate-200">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
        <Link to="/dashboard" className="text-lg font-bold text-sky-700">Erudition Platform</Link>
        {isAuthenticated && (
          <button
            onClick={handleLogout}
            className="px-4 py-2 text-sm rounded-lg bg-orange-600 text-white hover:bg-orange-700 transition"
          >
            Logout
          </button>
        )}
      </div>
    </header>
  );
}
