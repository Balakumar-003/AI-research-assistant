import { useState, useEffect } from 'react';
import { chatService } from '../../services/chatService';

export function ConversationSidebar({ projectId, onSelectConversation }: { projectId: string, onSelectConversation: (id: string) => void }) {
  const [history, setHistory] = useState<any[]>([]);
  
  useEffect(() => {
    fetchHistory();
  }, [projectId]);

  const fetchHistory = async () => {
    try {
      const data = await chatService.getHistory(projectId);
      setHistory(data.history || []);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="w-64 bg-gray-50 border-r flex flex-col p-4 h-full">
      <h3 className="font-bold text-gray-700 mb-4">Chat History</h3>
      <button 
        onClick={() => onSelectConversation('new')}
        className="mb-4 px-4 py-2 bg-white border border-gray-300 rounded hover:bg-gray-100 text-sm font-medium text-gray-700"
      >
        + New Conversation
      </button>
      <div className="flex-1 overflow-auto space-y-2">
        {history.length === 0 ? (
          <p className="text-sm text-gray-500">No previous sessions.</p>
        ) : (
          history.map((session, i) => (
            <div 
              key={session._id || i}
              onClick={() => onSelectConversation(session._id)}
              className="p-2 bg-white rounded shadow-sm border cursor-pointer hover:border-blue-300 text-sm"
            >
              <div className="truncate font-medium text-gray-800">{session.title || 'Research Session'}</div>
              <div className="text-xs text-gray-500">{new Date(session.updated_at || Date.now()).toLocaleDateString()}</div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
