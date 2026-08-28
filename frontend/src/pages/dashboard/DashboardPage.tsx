
import { useAuth } from '../../context/AuthContext';
import { Card } from '../../components/common/Card';
import { FileText, MessageSquare, Save, Activity } from 'lucide-react';
import { Link } from 'react-router-dom';
import './Dashboard.css';

export const DashboardPage = () => {
  const { user } = useAuth();

  return (
    <div className="dashboard-page animate-fade-in">
      <div className="dashboard-header">
        <h1>Welcome back, {user?.name || 'Researcher'}</h1>
        <p>Here's an overview of your research activities.</p>
      </div>

      <div className="stats-grid">
        <Card className="stat-card">
          <div className="stat-icon"><FileText size={24} color="var(--primary)" /></div>
          <div className="stat-info">
            <h3>Total Papers</h3>
            <p className="stat-value">0</p>
          </div>
        </Card>
        <Card className="stat-card">
          <div className="stat-icon"><Activity size={24} color="var(--success)" /></div>
          <div className="stat-info">
            <h3>Research Sessions</h3>
            <p className="stat-value">0</p>
          </div>
        </Card>
        <Card className="stat-card">
          <div className="stat-icon"><MessageSquare size={24} color="#f59e0b" /></div>
          <div className="stat-info">
            <h3>Questions Asked</h3>
            <p className="stat-value">0</p>
          </div>
        </Card>
        <Card className="stat-card">
          <div className="stat-icon"><Save size={24} color="#8b5cf6" /></div>
          <div className="stat-info">
            <h3>Saved Research</h3>
            <p className="stat-value">0</p>
          </div>
        </Card>
      </div>

      <div className="quick-actions-section">
        <h2>Quick Actions</h2>
        <div className="actions-grid">
          <Link to="/papers" className="action-card">
            <div className="action-icon bg-primary-light">
              <FileText size={28} />
            </div>
            <h3>Upload Paper</h3>
            <p>Add a new PDF to your library</p>
          </Link>
          <Link to="/research" className="action-card">
            <div className="action-icon bg-success-light">
              <MessageSquare size={28} />
            </div>
            <h3>Ask Question</h3>
            <p>Query your existing papers</p>
          </Link>
        </div>
      </div>
    </div>
  );
};
