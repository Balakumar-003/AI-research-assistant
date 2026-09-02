import api from './api';

export interface Paper {
  _id: string;
  title: string;
  filename: string;
  status: 'uploaded' | 'processing' | 'ready' | 'failed';
  upload_date: string;
  page_count?: number;
}

export const paperService = {
  getProjectPapers: async (projectId: string) => {
    const response = await api.get(`/projects/${projectId}/papers`);
    return response.data;
  },

  uploadPaper: async (projectId: string, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post(`/projects/${projectId}/papers`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  getPaper: async (paperId: string) => {
    const response = await api.get(`/papers/${paperId}`);
    return response.data;
  },

  getProcessingStatus: async (paperId: string) => {
    const response = await api.get(`/papers/${paperId}/processing-status`);
    return response.data;
  },
  
  processPaper: async (paperId: string) => {
    const response = await api.post(`/papers/${paperId}/process`);
    return response.data;
  }
};
