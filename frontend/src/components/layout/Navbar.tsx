
import { useAuth } from '../../context/AuthContext';
import { Link } from 'react-router-dom';
import { Bot } from 'lucide-react';

export const Navbar = () => {
  const { user } = useAuth();

  return (
    <header className="navbar">
      <div className="navbar-brand">
        <Link to="/dashboard" className="flex items-center gap-2">
          <Bot size={24} color="var(--primary)" />
          <span className="navbar-title">AI Research Assistant</span>
        </Link>
      </div>
      <div className="navbar-user">
        <span className="user-name">{user?.name}</span>
        <div className="user-avatar">
          {user?.name?.charAt(0).toUpperCase() || 'U'}
        </div>
      </div>
    </header>
  );
};
