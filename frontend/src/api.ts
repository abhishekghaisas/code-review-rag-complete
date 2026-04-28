import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface ReviewRequest {
  code: string;
  language: string;
  model: string;
  use_rag: boolean;
  n_similar: number;
}

export interface ReviewResponse {
  id?: number;  // Added: database ID
  review: string;
  similar_code: string[];
  similar_code_metadata: Array<{
    file_path: string;
    function_name?: string;
    language: string;
  }>;
  model_used: string;
  rag_enabled: boolean;
  context_used: boolean;
  error?: string;
}

export interface SavedReview {
  id: number;
  code: string;
  language: string;
  model: string;
  use_rag: boolean;
  review: ReviewResponse;
  created_at: string;
}

export interface Model {
  id: string;
  name: string;
  cost: string;
  quality?: string;
  description?: string;
}

export interface ModelsResponse {
  models: Model[];
}

export interface StatsResponse {
  collection_name: string;
  total_chunks: number;
  embedding_model: string;
  embedding_dimension: number;
}

export interface HealthResponse {
  status: string;
  version: string;
  database_connected: boolean;
  llm_client_initialized: boolean;
}

export interface IngestionJob {
  id: number;
  job_type: string;
  source: string;
  status: string;
  chunks_ingested: number;
  error_message?: string;
  created_at: string;
  completed_at?: string;
}

// Review endpoints
export const reviewCode = async (request: ReviewRequest): Promise<ReviewResponse> => {
  const response = await api.post<ReviewResponse>('/api/review', request);
  return response.data;
};

export const getReviews = async (limit: number = 20, skip: number = 0): Promise<SavedReview[]> => {
  const response = await api.get<{ reviews: SavedReview[] }>('/api/reviews', {
    params: { limit, skip }
  });
  return response.data.reviews;
};

export const getReviewById = async (id: number): Promise<SavedReview> => {
  const response = await api.get<SavedReview>(`/api/reviews/${id}`);
  return response.data;
};

export const deleteReview = async (id: number): Promise<void> => {
  await api.delete(`/api/reviews/${id}`);
};

// Other endpoints
export const getModels = async (): Promise<ModelsResponse> => {
  const response = await api.get<ModelsResponse>('/api/models');
  return response.data;
};

export const getStats = async (): Promise<StatsResponse> => {
  const response = await api.get<StatsResponse>('/api/stats');
  return response.data;
};

export const getHealth = async (): Promise<HealthResponse> => {
  const response = await api.get<HealthResponse>('/health');
  return response.data;
};

export const getIngestionJobs = async (limit: number = 20): Promise<IngestionJob[]> => {
  const response = await api.get<{ jobs: IngestionJob[] }>('/api/ingestion/jobs', {
    params: { limit }
  });
  return response.data.jobs;
};

export default api;
