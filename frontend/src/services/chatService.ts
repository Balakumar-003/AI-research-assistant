import api from './api';

export interface ChatMessage {
  _id?: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: Citation[];
  timestamp?: string;
}

export interface Citation {
  chunk_id: string;
  paper_id: string;
  paper_title?: string;
  text: string;
  score: number;
  metadata?: any;
}

export const chatService = {
  askQuestion: async (question: string, projectId?: string, paperId?: string) => {
    const response = await api.post('/chat', {
      question,
      project_id: projectId,
      paper_id: paperId,
    });
    return response.data;
  },

  getHistory: async (projectId?: string) => {
    const response = await api.get('/chat/history', {
      params: { project_id: projectId },
    });
    return response.data;
  },
};
