// API client for SnapBrand.ai backend

const API_BASE_URL = (typeof window !== 'undefined' ? window.location.origin : 'http://localhost:3000').replace('3000', '8000');

export interface GenerateRequest {
  prompt: string;
  negative_prompt?: string;
  num_images?: number;
  size?: string;
  guidance_scale?: number;
  seed?: number;
  template_id?: string;
  brand_style?: Record<string, any>;
}

export interface GeneratedImage {
  id: string;
  s3_url: string;
  presigned_url: string;
  prompt: string;
  size: string;
  created_at: string;
  metadata?: Record<string, any>;
}

export interface GenerateResponse {
  images: GeneratedImage[];
  total_cost?: number;
  processing_time?: number;
}

export interface Template {
  id: string;
  name: string;
  category: string;
  description: string;
  prompt_template: string;
  negative_prompt?: string;
  default_size: string;
  parameters: Record<string, any>;
  is_active: boolean;
}

export interface BatchGenerateRequest {
  requests: GenerateRequest[];
  batch_id?: string;
  priority?: 'low' | 'normal' | 'high';
}

export interface BatchStatusResponse {
  batch_id: string;
  status: string;
  progress: number;
  completed_requests: number;
  total_requests: number;
  results?: GenerateResponse[];
  error_count: number;
  created_at: string;
  updated_at: string;
}

export interface UploadUrlResponse {
  upload_url: string;
  object_key: string;
  expires_at: string;
}

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public details?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

class ApiClient {
  private baseUrl: string;
  private apiKey?: string;

  constructor(baseUrl: string = API_BASE_URL, apiKey?: string) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.apiKey) {
      (headers as Record<string, string>)['X-API-Key'] = this.apiKey;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        errorData.error || `HTTP ${response.status}`,
        response.status,
        errorData
      );
    }

    return response.json();
  }

  // Health check
  async healthCheck(): Promise<{ status: string; version: string }> {
    return this.request('/health');
  }

  // Image Generation
  async generateImages(request: GenerateRequest): Promise<GenerateResponse> {
    return this.request('/v1/generate', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getGenerationStatus(): Promise<Record<string, any>> {
    return this.request('/v1/generate/status');
  }

  // Templates
  async getTemplates(category?: string): Promise<Template[]> {
    const params = category ? `?category=${encodeURIComponent(category)}` : '';
    return this.request(`/v1/templates${params}`);
  }

  async getTemplate(templateId: string): Promise<Template> {
    return this.request(`/v1/templates/${templateId}`);
  }

  async getTemplateCategories(): Promise<string[]> {
    return this.request('/v1/templates/categories');
  }

  async getTemplatePrompt(
    templateId: string,
    params: Record<string, string>
  ): Promise<{
    template_id: string;
    prompt: string;
    negative_prompt?: string;
    size: string;
    parameters: Record<string, string>;
  }> {
    const queryParams = new URLSearchParams(params);
    return this.request(`/v1/templates/${templateId}/prompt?${queryParams}`);
  }

  // Batch Operations
  async createBatchJob(request: BatchGenerateRequest): Promise<{
    batch_id: string;
    total_requests: number;
    status: string;
    estimated_completion?: string;
  }> {
    return this.request('/v1/batch/generate', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getBatchStatus(batchId: string): Promise<BatchStatusResponse> {
    return this.request(`/v1/batch/${batchId}/status`);
  }

  async listBatchJobs(limit?: number, status?: string): Promise<BatchStatusResponse[]> {
    const params = new URLSearchParams();
    if (limit) params.append('limit', limit.toString());
    if (status) params.append('status', status);
    return this.request(`/v1/batch?${params}`);
  }

  async cancelBatchJob(batchId: string): Promise<{ message: string }> {
    return this.request(`/v1/batch/${batchId}`, {
      method: 'DELETE',
    });
  }

  // Asset Management
  async getUploadUrl(filename: string): Promise<UploadUrlResponse> {
    return this.request(`/v1/assets/upload-url?filename=${encodeURIComponent(filename)}`);
  }

  // Utility methods
  async uploadFile(uploadUrl: string, file: File): Promise<void> {
    await fetch(uploadUrl, {
      method: 'PUT',
      body: file,
      headers: {
        'Content-Type': file.type,
      },
    });
  }

  // Polling utilities
  async pollBatchStatus(
    batchId: string,
    onProgress?: (status: BatchStatusResponse) => void,
    interval: number = 2000
  ): Promise<BatchStatusResponse> {
    return new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          const status = await this.getBatchStatus(batchId);
          onProgress?.(status);

          if (['completed', 'completed_with_errors', 'cancelled', 'failed'].includes(status.status)) {
            resolve(status);
          } else {
            setTimeout(poll, interval);
          }
        } catch (error) {
          reject(error);
        }
      };
      poll();
    });
  }
}

// Create default instance
export const apiClient = new ApiClient();

// Export types for convenience
export type { ApiError }; 