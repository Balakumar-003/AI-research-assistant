import { useState, useEffect } from 'react';
import { paperService, type Paper } from '../../services/paperService';
import { UploadPaper } from './UploadPaper';
import './PaperLibrary.css';

export function PaperLibrary({ onSelectPaper, selectedPaperId }: { onSelectPaper: (paper: Paper) => void, selectedPaperId?: string }) {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Using a mock project ID for the demo if there's no project context, or fetch from auth/context.
  const projectId = 'default_project';

  useEffect(() => {
    fetchPapers();
  }, []);

  const fetchPapers = async () => {
    setLoading(true);
    try {
      const data = await paperService.getProjectPapers(projectId);
      setPapers(data.papers || data || []);
      setError(null);
    } catch (err: any) {
      setError('Failed to load papers');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="p-4 text-muted">Loading papers...</div>;
  
  return (
    <div className="paper-library">
      <div className="library-header">
        <h2 className="text-xl font-bold">Research Papers</h2>
        <UploadPaper projectId={projectId} onUploadSuccess={fetchPapers} />
      </div>
      
      {error && <div className="text-red-500 mb-4">{error}</div>}
      
      {papers.length === 0 ? (
        <div className="text-center p-8 text-muted">
          <p>No research papers yet.</p>
        </div>
      ) : (
        <ul className="paper-list">
          {papers.map((paper) => (
            <li 
              key={paper._id} 
              className={`paper-item ${selectedPaperId === paper._id ? 'selected' : ''}`}
              onClick={() => onSelectPaper(paper)}
            >
              <h3 className="font-semibold">{paper.title}</h3>
              <p className="text-sm text-muted">Status: {paper.status}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
