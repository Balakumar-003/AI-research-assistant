import { useState, useRef, useEffect } from 'react';
import { chatService, type ChatMessage, type Citation } from '../../services/chatService';
import { type Paper } from '../../services/paperService';
import { ConversationSidebar } from './ConversationSidebar';
import './ResearchChat.css';

export function ResearchChat({ paper, projectId }: { paper?: Paper, projectId: string }) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setLoading(true);

    try {
      const response = await chatService.askQuestion(userMsg, projectId, paper?._id);
      setMessages(prev => [
        ...prev, 
        { 
          role: 'assistant', 
          content: response.answer || response.response || 'No answer returned.', 
          sources: response.sources || response.citations || []
        }
      ]);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: 'Sorry, an error occurred while processing your question.' }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-full w-full">
      <ConversationSidebar 
        projectId={projectId} 
        onSelectConversation={(id) => {
          if (id === 'new') setMessages([]);
        }} 
      />
      <div className="research-chat flex flex-col flex-1 h-full">
        <div className="chat-header p-4 border-b">
          <h2 className="text-xl font-bold">
            {paper ? `Research: ${paper.title}` : 'General Research'}
          </h2>
          {paper && <p className="text-sm text-muted">Status: {paper.status}</p>}
        </div>

        <div className="chat-messages flex-1 p-4 overflow-y-auto">
          {messages.length === 0 ? (
            <div className="h-full flex items-center justify-center text-muted">
              Start your research by asking a question.
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div key={idx} className={`message-container mb-6 ${msg.role}`}>
                <div className="message-bubble p-4 rounded-lg bg-gray-100 max-w-4xl w-full">
                  <div className="flex justify-between items-center mb-2">
                    <div className="font-semibold">{msg.role === 'user' ? 'You' : 'Assistant'}</div>
                    {msg.role === 'assistant' && (
                      <button 
                        onClick={() => navigator.clipboard.writeText(msg.content)}
                        className="text-xs text-blue-600 hover:underline"
                      >
                        Copy Answer
                      </button>
                    )}
                  </div>
                  <div className="whitespace-pre-wrap text-gray-800">{msg.content}</div>
                  
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-4 border-t pt-2">
                      <h4 className="font-semibold text-sm mb-2 text-gray-600">Sources / Citations</h4>
                      <div className="sources-list space-y-2 text-sm">
                        {msg.sources.map((src: Citation, i: number) => (
                          <details key={i} className="source-item bg-white p-2 rounded border border-gray-200 cursor-pointer shadow-sm">
                            <summary className="font-medium text-blue-600 hover:text-blue-700 outline-none flex justify-between">
                              <span>[{i + 1}] {src.paper_title || 'Paper'}</span>
                              <span className="text-xs text-gray-500">Score: {src.score?.toFixed(2) || 'N/A'}</span>
                            </summary>
                            <p className="mt-2 text-gray-700 p-3 bg-gray-50 rounded italic border-l-4 border-blue-400">
                              "{src.text}"
                            </p>
                          </details>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
          {loading && (
            <div className="message-container assistant">
              <div className="message-bubble p-4 rounded-lg bg-gray-100">
                <span className="animate-pulse font-medium text-gray-600">Analyzing research and generating response...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="chat-input p-4 border-t bg-gray-50">
          <form onSubmit={handleSubmit} className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loading}
              placeholder={paper ? "Ask a question about this research paper..." : "Ask a general research question..."}
              className="flex-1 p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm"
            />
            <button 
              type="submit" 
              disabled={loading || !input.trim()}
              className="px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors shadow-sm"
            >
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
