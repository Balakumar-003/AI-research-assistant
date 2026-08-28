import { useState, useEffect } from 'react';
import { FileUpload } from '../../components/ui/FileUpload';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Search, FileText, CheckCircle, Clock } from 'lucide-react';
import type { Paper } from '../../types';
import { LoadingState } from '../../components/feedback/LoadingState';
import api from '../../services/api';
import './Papers.css';

export const PapersPage = () => {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [showUpload, setShowUpload] = useState(false);

  // In a real app, you would fetch projects first. For this milestone, we use a placeholder project ID or fetch a default one.
  const DEFAULT_PROJECT_ID = 'default';

  const fetchPapers = async () => {
    setIsLoading(true);
    try {
      // Use the actual endpoint from api.py, assuming we get a list of papers
      const res = await api.get(`/projects/${DEFAULT_PROJECT_ID}/papers`);
      setPapers(res.data || []);
    } catch (err: any) {
      if (err.response?.status === 404) {
        setPapers([]); // Project might not exist yet, treat as empty
      } else {
        setError('Failed to load papers. Please try again later.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPapers();
  }, []);

  const handleUpload = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    
    await api.post(`/projects/${DEFAULT_PROJECT_ID}/papers`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    setShowUpload(false);
    fetchPapers();
  };

  if (isLoading) return <LoadingState message="Loading your papers..." />;

  return (
    <div className="papers-page animate-fade-in">
      <div className="papers-header">
        <div>
          <h1>My Papers</h1>
          <p>Manage your uploaded research documents.</p>
        </div>
        <Button onClick={() => setShowUpload(!showUpload)}>
          {showUpload ? 'Cancel Upload' : 'Upload Paper'}
        </Button>
      </div>

      {showUpload && (
        <Card className="upload-section mb-6 animate-fade-in">
          <h2>Upload New Document</h2>
          <FileUpload onUpload={handleUpload} />
        </Card>
      )}

      {error && <div className="error-banner mb-6">{error}</div>}

      <div className="papers-toolbar">
        <div className="search-bar">
          <Search size={20} className="search-icon" />
          <input type="text" placeholder="Search papers by title..." />
        </div>
      </div>

      {papers.length === 0 ? (
        <div className="empty-state">
          <FileText size={64} className="text-muted mb-4" />
          <h3>No papers found</h3>
          <p>You haven't uploaded any research papers yet.</p>
          <Button onClick={() => setShowUpload(true)} className="mt-4">
            Upload Your First Paper
          </Button>
        </div>
      ) : (
        <div className="papers-grid">
          {papers.map((paper) => (
            <Card key={paper.id} className="paper-card">
              <div className="paper-icon">
                <FileText size={24} />
              </div>
              <div className="paper-details">
                <h3 className="paper-title" title={paper.filename}>
                  {paper.filename}
                </h3>
                <div className="paper-meta">
                  <span className="flex items-center gap-1">
                    {paper.status === 'completed' ? (
                      <CheckCircle size={14} className="text-success" />
                    ) : (
                      <Clock size={14} className="text-muted" />
                    )}
                    {paper.status}
                  </span>
                  <span>•</span>
                  <span>{new Date(paper.uploaded_at).toLocaleDateString()}</span>
                  {paper.page_count && (
                    <>
                      <span>•</span>
                      <span>{paper.page_count} pages</span>
                    </>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
