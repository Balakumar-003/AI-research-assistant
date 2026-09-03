import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { paperService, type Paper } from '../../services/paperService';
import { searchService } from '../../services/searchService';

export function ResearchDashboard() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const projectId = 'default_project';

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [papersData, statsData] = await Promise.all([
          paperService.getProjectPapers(projectId).catch(() => ({ papers: [] })),
          searchService.getVectorStats().catch(() => null)
        ]);
        setPapers(papersData.papers || papersData || []);
        setStats(statsData);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <div className="p-8">Loading dashboard...</div>;

  const totalPapers = papers.length;
  const readyPapers = papers.filter(p => p.status === 'ready').length;
  const recentPapers = [...papers].sort((a, b) => new Date(b.upload_date).getTime() - new Date(a.upload_date).getTime()).slice(0, 5);

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-800">Research Overview</h1>
        <Link to="/research/papers" className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
          Manage Papers
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow border border-gray-100">
          <h3 className="text-gray-500 font-medium mb-2">Total Papers</h3>
          <p className="text-4xl font-bold text-gray-900">{totalPapers}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow border border-gray-100">
          <h3 className="text-gray-500 font-medium mb-2">Ready for AI</h3>
          <p className="text-4xl font-bold text-green-600">{readyPapers}</p>
        </div>
        <div className="bg-white p-6 rounded-lg shadow border border-gray-100">
          <h3 className="text-gray-500 font-medium mb-2">Vector Chunks</h3>
          <p className="text-4xl font-bold text-blue-600">{stats?.total_chunks || 0}</p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow border border-gray-100">
        <div className="px-6 py-4 border-b border-gray-100">
          <h2 className="text-xl font-semibold text-gray-800">Recent Papers</h2>
        </div>
        <div className="p-6">
          {recentPapers.length === 0 ? (
            <p className="text-gray-500 text-center">No papers uploaded yet.</p>
          ) : (
            <ul className="divide-y divide-gray-100">
              {recentPapers.map(paper => (
                <li key={paper._id} className="py-4 flex justify-between items-center">
                  <div>
                    <h4 className="font-medium text-gray-900">{paper.title}</h4>
                    <p className="text-sm text-gray-500">Uploaded: {new Date(paper.upload_date).toLocaleDateString()}</p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    paper.status === 'ready' ? 'bg-green-100 text-green-800' :
                    paper.status === 'processing' ? 'bg-blue-100 text-blue-800' :
                    paper.status === 'failed' ? 'bg-red-100 text-red-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {paper.status}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
