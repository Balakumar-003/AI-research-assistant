
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './routes/ProtectedRoute';

import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/auth/LoginPage';
import { RegisterPage } from './pages/auth/RegisterPage';
import { DashboardLayout } from './layouts/DashboardLayout';
import { DashboardPage } from './pages/dashboard/DashboardPage';
import { PapersPage } from './pages/papers/PapersPage';

import { ResearchWorkspace } from './pages/research/ResearchWorkspace';

import { PaperDetailsPage } from './pages/papers/PaperDetailsPage';

const PlaceholderPage = ({ title }: { title: string }) => (
  <div className="p-8 animate-fade-in">
    <h1 className="text-2xl font-bold mb-4">{title}</h1>
    <p className="text-muted">This feature is not implemented in this milestone.</p>
  </div>
);

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Protected Routes */}
          <Route element={<ProtectedRoute><DashboardLayout /></ProtectedRoute>}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/papers" element={<PapersPage />} />
            <Route path="/papers/:paperId" element={<PaperDetailsPage />} />
            <Route path="/research" element={<ResearchWorkspace />} />
            <Route path="/settings" element={<PlaceholderPage title="Settings" />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
