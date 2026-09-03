import api from './api';

export interface SearchRequest {
  query: string;
  project_id: string;
  paper_id?: string;
  top_k?: number;
}

export interface SearchResultItem {
  chunk_id: string;
  paper_id: string;
  paper_title: string;
  text: string;
  score: number;
  metadata?: any;
}

export interface SearchResponse {
  results: SearchResultItem[];
  total_found: number;
}

export const searchService = {
  searchVectors: async (request: SearchRequest) => {
    const response = await api.post('/search', request);
    return response.data;
  },

  getVectorStats: async () => {
    const response = await api.get('/search/stats');
    return response.data;
  }
};
