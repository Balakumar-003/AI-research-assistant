import { useParams, Link } from 'react-router-dom';
import { PaperDetails } from '../../components/papers/PaperDetails';

export function PaperDetailsPage() {
  const { paperId } = useParams();

  if (!paperId) {
    return <div className="p-8 text-red-500">No paper ID provided.</div>;
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="mb-6">
        <Link to="/papers" className="text-blue-600 hover:underline">
          &larr; Back to Papers
        </Link>
      </div>
      <PaperDetails paperId={paperId} />
    </div>
  );
}
