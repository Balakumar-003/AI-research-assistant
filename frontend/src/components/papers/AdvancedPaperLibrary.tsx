import { useState, useEffect } from 'react';
import { paperService, type Paper } from '../../services/paperService';
import { UploadPaper } from './UploadPaper';
import { Link } from 'react-router-dom';

export function AdvancedPaperLibrary() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  
  const projectId = 'default_project';

  useEffect(() => {
    fetchPapers();
  }, []);

  const fetchPapers = async () => {
    setLoading(true);
    try {
      const data = await paperService.getProjectPapers(projectId);
      setPapers(data.papers || data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const filteredPapers = papers.filter(p => {
    const matchesSearch = p.title.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || p.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const toggleSelection = (id: string) => {
    const newSel = new Set(selectedIds);
    if (newSel.has(id)) newSel.delete(id);
    else newSel.add(id);
    setSelectedIds(newSel);
  };

  return (
    <div className="p-8 max-w-6xl mx-auto h-full flex flex-col">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Paper Library</h1>
        <UploadPaper projectId={projectId} onUploadSuccess={fetchPapers} />
      </div>

      <div className="bg-white p-4 rounded-lg shadow border border-gray-100 mb-6 flex gap-4 flex-wrap">
        <input 
          type="text" 
          placeholder="Search papers..." 
          className="border rounded p-2 flex-1 min-w-[200px]"
          value={searchTerm}
          onChange={e => setSearchTerm(e.target.value)}
        />
        <select 
          className="border rounded p-2"
          value={statusFilter}
          onChange={e => setStatusFilter(e.target.value)}
        >
          <option value="all">All Statuses</option>
          <option value="ready">Ready</option>
          <option value="processing">Processing</option>
          <option value="uploaded">Uploaded</option>
          <option value="failed">Failed</option>
        </select>
        
        {selectedIds.size > 0 && (
          <div className="flex items-center gap-4 border-l pl-4">
            <span className="font-medium text-blue-600">{selectedIds.size} selected</span>
            <Link 
              to={`/research/compare?ids=${Array.from(selectedIds).join(',')}`}
              className={`px-4 py-2 rounded text-white ${selectedIds.size > 1 ? 'bg-indigo-600 hover:bg-indigo-700' : 'bg-gray-400 cursor-not-allowed'}`}
              onClick={(e) => {
                if (selectedIds.size < 2) {
                  e.preventDefault();
                  alert('Select at least 2 papers to compare.');
                }
              }}
            >
              Compare
            </Link>
          </div>
        )}
      </div>

      <div className="flex-1 overflow-auto">
        {loading ? (
          <div className="text-center p-8 text-gray-500">Loading library...</div>
        ) : filteredPapers.length === 0 ? (
          <div className="text-center p-12 bg-white rounded-lg border text-gray-500">
            No papers match your criteria.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredPapers.map(paper => (
              <div key={paper._id} className="bg-white p-5 rounded-lg shadow-sm border border-gray-200 flex flex-col">
                <div className="flex items-start justify-between mb-3">
                  <input 
                    type="checkbox" 
                    className="mt-1 mr-3 w-5 h-5 cursor-pointer"
                    checked={selectedIds.has(paper._id)}
                    onChange={() => toggleSelection(paper._id)}
                  />
                  <h3 className="font-semibold text-lg text-gray-900 flex-1 line-clamp-2" title={paper.title}>{paper.title}</h3>
                </div>
                
                <div className="text-sm text-gray-500 mb-4 mt-auto">
                  <p>Status: <span className="capitalize">{paper.status}</span></p>
                  <p>Uploaded: {new Date(paper.upload_date).toLocaleDateString()}</p>
                </div>
                
                <Link to={`/papers/${paper._id}`} className="text-blue-600 text-sm hover:underline font-medium">
                  View Details &rarr;
                </Link>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
