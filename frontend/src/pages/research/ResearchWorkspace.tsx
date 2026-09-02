import { useState } from 'react';
import { PaperLibrary } from '../../components/papers/PaperLibrary';
import { ResearchChat } from '../../components/chat/ResearchChat';
import { type Paper } from '../../services/paperService';
import './ResearchWorkspace.css';

export function ResearchWorkspace() {
  const [selectedPaper, setSelectedPaper] = useState<Paper | undefined>(undefined);
  // Optional: projectId from context or state
  const projectId = 'default_project';

  return (
    <div className="research-workspace flex h-screen bg-white">
      {/* Sidebar for papers */}
      <div className="w-1/4 min-w-[250px] max-w-[350px] bg-gray-50 border-r border-gray-200 flex flex-col">
        <PaperLibrary 
          onSelectPaper={setSelectedPaper} 
          selectedPaperId={selectedPaper?._id} 
        />
      </div>

      {/* Main content area for Chat/Q&A */}
      <div className="flex-1 flex flex-col">
        <ResearchChat 
          paper={selectedPaper} 
          projectId={projectId}
        />
      </div>
    </div>
  );
}
