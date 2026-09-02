import { useState, useEffect } from 'react';
import { paperService, type Paper } from '../../services/paperService';
import './PaperDetails.css';

export function PaperDetails({ paperId }: { paperId: string }) {
  const [paper, setPaper] = useState<Paper | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPaperDetails();
  }, [paperId]);

  const fetchPaperDetails = async () => {
    setLoading(true);
    try {
      const data = await paperService.getPaper(paperId);
      setPaper(data.paper || data);
      setError(null);
    } catch (err) {
      setError('Failed to load paper details.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="p-4 text-muted">Loading paper details...</div>;
  if (error) return <div className="p-4 text-red-500">{error}</div>;
  if (!paper) return <div className="p-4 text-muted">Paper not found.</div>;

  return (
    <div className="paper-details p-6 bg-white rounded shadow-sm border">
      <h2 className="text-2xl font-bold mb-4">{paper.title}</h2>
      
      <div className="metadata-grid grid grid-cols-2 gap-4 text-sm">
        <div className="metadata-item">
          <span className="font-semibold text-gray-600">Filename:</span>
          <p className="break-all">{paper.filename}</p>
        </div>
        <div className="metadata-item">
          <span className="font-semibold text-gray-600">Status:</span>
          <p className="capitalize">
            <span className={`status-badge ${paper.status}`}>
              {paper.status}
            </span>
          </p>
        </div>
        <div className="metadata-item">
          <span className="font-semibold text-gray-600">Upload Date:</span>
          <p>{new Date(paper.upload_date).toLocaleString()}</p>
        </div>
        {paper.page_count !== undefined && (
          <div className="metadata-item">
            <span className="font-semibold text-gray-600">Pages:</span>
            <p>{paper.page_count}</p>
          </div>
        )}
      </div>

      {paper.status === 'uploaded' && (
        <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded">
          <p className="text-yellow-800">This paper has not been processed yet. Process it to enable AI research.</p>
          <button 
            onClick={async () => {
              try {
                await paperService.processPaper(paper._id);
                fetchPaperDetails();
              } catch (e) {
                console.error("Processing failed");
              }
            }}
            className="mt-2 px-4 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-700"
          >
            Process Paper
          </button>
        </div>
      )}
    </div>
  );
}
