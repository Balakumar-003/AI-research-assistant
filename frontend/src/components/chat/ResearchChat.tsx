import { useState, useRef, useEffect } from 'react';
import { chatService, type ChatMessage, type Citation } from '../../services/chatService';
import { type Paper } from '../../services/paperService';
import './ResearchChat.css';

export function ResearchChat({ paper, projectId }: { paper?: Paper, projectId: string }) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // If we wanted to load history here, we could.
    // For now, reset messages when paper changes if needed, or keep them.
  }, [paper]);

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
    <div className="research-chat flex flex-col h-full">
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
              <div className="message-bubble p-4 rounded-lg bg-gray-100 max-w-3xl">
                <div className="font-semibold mb-1">{msg.role === 'user' ? 'You' : 'Assistant'}</div>
                <div className="whitespace-pre-wrap">{msg.content}</div>
                
                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-4 border-t pt-2">
                    <h4 className="font-semibold text-sm mb-2">Sources</h4>
                    <div className="sources-list space-y-2 text-sm">
                      {msg.sources.map((src: Citation, i: number) => (
                        <details key={i} className="source-item bg-white p-2 rounded border cursor-pointer">
                          <summary className="font-medium text-blue-600 outline-none">
                            [{i + 1}] {src.paper_title || 'Paper'} {src.metadata?.page ? `- Page ${src.metadata.page}` : ''}
                          </summary>
                          <p className="mt-2 text-gray-700 p-2 bg-gray-50 rounded">
                            {src.text}
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
              <span className="animate-pulse">Thinking...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input p-4 border-t">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            placeholder={paper ? "Ask a question about this research paper..." : "Ask a general research question..."}
            className="flex-1 p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button 
            type="submit" 
            disabled={loading || !input.trim()}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
