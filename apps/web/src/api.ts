import type {
  BookPlanResponse,
  ChapterCatalogItem,
  ChapterCatalogResponse,
  ChapterDraftResponse,
  ChapterOutlineResponse,
  LLMConnectionTestResponse,
  LLMSettings,
  LLMSettingsUpdate,
  ProjectDetailResponse,
  ProjectSummary
} from './types';

// 开发模式可在 apps/web/.env 中设置 VITE_API_BASE_URL=http://127.0.0.1:8000。
// 用户模式下，前端由 FastAPI 托管，直接使用同源相对路径。
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options?.headers ?? {})
    },
    ...options
  });

  if (!response.ok) {
    let message = `请求失败：${response.status}`;
    try {
      const data = await response.json();
      message = data.detail ?? message;
    } catch {
      // Ignore JSON parse errors and use default message.
    }
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export function getLLMSettings(): Promise<LLMSettings> {
  return request<LLMSettings>('/api/settings/llm');
}

export function saveLLMSettings(payload: LLMSettingsUpdate): Promise<LLMSettings> {
  return request<LLMSettings>('/api/settings/llm', {
    method: 'POST',
    body: JSON.stringify(payload)
  });
}

export function testLLMSettings(): Promise<LLMConnectionTestResponse> {
  return request<LLMConnectionTestResponse>('/api/settings/llm/test', {
    method: 'POST',
    body: JSON.stringify({})
  });
}

export function createBookPlan(payload: {
  premise: string;
  genre: string;
  style: string;
}): Promise<BookPlanResponse> {
  return request<BookPlanResponse>('/api/director/book-plan', {
    method: 'POST',
    body: JSON.stringify(payload)
  });
}

export function listProjects(): Promise<ProjectSummary[]> {
  return request<ProjectSummary[]>('/api/projects');
}

export function getProject(projectId: string): Promise<ProjectDetailResponse> {
  return request<ProjectDetailResponse>(`/api/projects/${projectId}`);
}

export function createCatalog(projectId: string, payload: {
  volume_index: number;
  total_chapters: number;
  extra_requirements: string;
}): Promise<ChapterCatalogResponse> {
  return request<ChapterCatalogResponse>(`/api/projects/${projectId}/chapters/catalog`, {
    method: 'POST',
    body: JSON.stringify(payload)
  });
}

export function listChapters(projectId: string): Promise<ChapterCatalogItem[]> {
  return request<ChapterCatalogItem[]>(`/api/projects/${projectId}/chapters`);
}

export function createOutline(projectId: string, payload: {
  chapter_no: number;
  extra_requirements: string;
}): Promise<ChapterOutlineResponse> {
  return request<ChapterOutlineResponse>(`/api/projects/${projectId}/chapters/outline`, {
    method: 'POST',
    body: JSON.stringify(payload)
  });
}

export function getOutline(projectId: string, chapterNo: number): Promise<ChapterOutlineResponse> {
  return request<ChapterOutlineResponse>(`/api/projects/${projectId}/chapters/${chapterNo}/outline`);
}

export function createDraft(projectId: string, payload: {
  chapter_no: number;
  target_words: number;
  extra_requirements: string;
}): Promise<ChapterDraftResponse> {
  return request<ChapterDraftResponse>(`/api/projects/${projectId}/chapters/draft`, {
    method: 'POST',
    body: JSON.stringify(payload)
  });
}

export function getDraft(projectId: string, chapterNo: number): Promise<ChapterDraftResponse> {
  return request<ChapterDraftResponse>(`/api/projects/${projectId}/chapters/${chapterNo}/draft`);
}
