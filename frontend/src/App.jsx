import { Navigate, Route, Routes } from 'react-router-dom';
import Navbar from './components/Navbar';
import ProtectedRoute from './components/ProtectedRoute';
import { useAuth } from './context/AuthContext';
import LandingPage from './pages/LandingPage';
import RegisterPage from './pages/RegisterPage';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import SelectCoursePage from './pages/SelectCoursePage';
import AssessmentPage from './pages/AssessmentPage';
import ResultPage from './pages/ResultPage';
import FinalAssessmentPage from './pages/FinalAssessmentPage';
import FeedbackPage from './pages/FeedbackPage';

function HomeRoute() {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <Navigate to="/dashboard" replace /> : <LandingPage />;
}

export default function App() {
  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />
      <Routes>
        <Route path="/" element={<HomeRoute />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
        <Route path="/select-course" element={<ProtectedRoute><SelectCoursePage /></ProtectedRoute>} />
        <Route path="/assessment" element={<ProtectedRoute><AssessmentPage /></ProtectedRoute>} />
        <Route path="/result/:attemptId" element={<ProtectedRoute><ResultPage /></ProtectedRoute>} />
        <Route path="/final-assessment" element={<ProtectedRoute><FinalAssessmentPage /></ProtectedRoute>} />
        <Route path="/feedback" element={<ProtectedRoute><FeedbackPage /></ProtectedRoute>} />
      </Routes>
    </div>
  );
}
