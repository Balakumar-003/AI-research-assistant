export interface User {
  _id: string;
  name: string;
  email: string;
  role: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface Paper {
  id: string;
  filename: string;
  project_id: string;
  status: string;
  page_count?: number;
  chunking_status: string;
  chunk_count: number;
  uploaded_at: string;
}

export interface PageItem {
  page_number: number;
  text: string;
  has_text: boolean;
}

export interface PaginatedContentResponse {
  paper_id: string;
  pages: PageItem[];
  total_pages: number;
  current_page: number;
  limit: number;
}
