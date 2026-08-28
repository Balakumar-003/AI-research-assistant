
import { Link } from 'react-router-dom';
import { Button } from '../components/common/Button';
import { Bot, Search, FileText, Layers, Share2, AlignLeft } from 'lucide-react';
import './Landing.css';

export const LandingPage = () => {
  return (
    <div className="landing-page animate-fade-in">
      <nav className="landing-nav">
        <div className="landing-brand">
          <Bot size={28} color="var(--primary)" />
          <span>AI Research Assistant</span>
        </div>
        <div className="landing-nav-links">
          <Link to="/login" className="login-link">Sign In</Link>
          <Link to="/register"><Button>Get Started</Button></Link>
        </div>
      </nav>

      <main className="landing-main">
        <section className="hero-section">
          <h1>Accelerate Your <span>Academic Research</span></h1>
          <p>Read papers, search academic content, summarize articles, and compare research findings with the power of advanced AI.</p>
          <div className="hero-actions">
            <Link to="/register"><Button size="large">Get Started for Free</Button></Link>
            <Link to="/login"><Button variant="secondary" size="large">Sign In</Button></Link>
          </div>
        </section>

        <section className="features-section">
          <h2>Powerful Research Tools</h2>
          <div className="features-grid">
            <div className="feature-card">
              <Search className="feature-icon" />
              <h3>AI-Powered Research</h3>
              <p>Ask complex questions and get answers grounded in your uploaded documents.</p>
            </div>
            <div className="feature-card">
              <FileText className="feature-icon" />
              <h3>Paper Summarization</h3>
              <p>Quickly understand the core concepts of lengthy papers in minutes.</p>
            </div>
            <div className="feature-card">
              <Layers className="feature-icon" />
              <h3>Multi-Paper Comparison</h3>
              <p>Synthesize information across multiple papers to find common themes.</p>
            </div>
            <div className="feature-card">
              <AlignLeft className="feature-icon" />
              <h3>Literature Review</h3>
              <p>Automatically generate comprehensive literature reviews from your library.</p>
            </div>
            <div className="feature-card">
              <Share2 className="feature-icon" />
              <h3>Citation-Grounded Answers</h3>
              <p>Every claim is backed by exact citations from your source material.</p>
            </div>
          </div>
        </section>
      </main>

      <footer className="landing-footer">
        <div className="footer-content">
          <div className="footer-brand">
            <Bot size={20} />
            <span>AI Research Assistant</span>
          </div>
          <p>&copy; {new Date().getFullYear()} AI Research Assistant. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};
