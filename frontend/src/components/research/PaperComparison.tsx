import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { comparisonService, type ComparisonRecordResponse } from '../../services/comparisonService';

export function PaperComparison() {
  const [searchParams] = useSearchParams();
  const idsParam = searchParams.get('ids');
  const paperIds = idsParam ? idsParam.split(',') : [];

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ComparisonRecordResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (paperIds.length >= 2) {
      handleCompare();
    }
  }, []);

  const handleCompare = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await comparisonService.createComparison({ paper_ids: paperIds });
      setResult(res);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to compare papers.');
    } finally {
      setLoading(false);
    }
  };

  if (paperIds.length < 2) {
    return (
      <div className="p-8 text-center text-gray-500">
        <h2 className="text-xl font-bold mb-4">Paper Comparison</h2>
        <p>Please select at least two papers from the Library to compare them.</p>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-6xl mx-auto h-full flex flex-col">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Compare Research Papers</h1>
      </div>

      {loading && (
        <div className="flex-1 flex flex-col items-center justify-center text-gray-600">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mb-4"></div>
          <p className="text-lg">Analyzing selected papers...</p>
        </div>
      )}

      {error && (
        <div className="bg-red-50 text-red-700 p-4 rounded mb-6">
          {error}
        </div>
      )}

      {result && !loading && (
        <div className="flex-1 overflow-auto bg-white rounded-lg shadow border">
          <div className="p-6 border-b bg-gray-50">
            <h2 className="text-xl font-semibold mb-4">Comparison Results</h2>
            <div className="flex gap-4 flex-wrap">
              {result.paper_ids.map(id => (
                <div key={id} className="bg-indigo-100 text-indigo-800 px-3 py-1 rounded font-medium text-sm">
                  {result.paper_titles[id] || id}
                </div>
              ))}
            </div>
          </div>
          
          <div className="p-6">
            {result.aspects.map(aspect => (
              <div key={aspect} className="mb-8">
                <h3 className="text-lg font-bold mb-4 capitalize border-b pb-2 text-gray-800">{aspect}</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {result.paper_ids.map(id => (
                    <div key={`${aspect}-${id}`} className="bg-gray-50 p-4 rounded border border-gray-200">
                      <h4 className="font-semibold text-sm text-gray-600 mb-2 truncate">
                        {result.paper_titles[id] || id}
                      </h4>
                      <p className="text-gray-800 whitespace-pre-wrap text-sm leading-relaxed">
                        {result.results[id]?.[aspect] || 'No data for this aspect.'}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
