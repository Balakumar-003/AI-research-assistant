import api from './api';

export interface ComparisonRequest {
  paper_ids: string[];
  aspects?: string[];
}

export interface ComparisonRecordResponse {
  _id: string;
  project_id: string;
  paper_ids: string[];
  paper_titles: Record<string, string>;
  aspects: string[];
  results: Record<string, Record<string, string>>;
  created_at: string;
}

export interface ComparisonHistoryItem {
  _id: string;
  paper_ids: string[];
  paper_titles: Record<string, string>;
  created_at: string;
}

export const comparisonService = {
  createComparison: async (request: ComparisonRequest) => {
    const response = await api.post('/comparisons/', request);
    return response.data;
  },

  getComparison: async (comparisonId: string) => {
    const response = await api.get(`/comparisons/${comparisonId}`);
    return response.data;
  },

  getProjectComparisons: async (projectId: string) => {
    const response = await api.get(`/comparisons/project/${projectId}`);
    return response.data;
  }
};
