export type CharacterCard = {
  name: string;
  role: string;
  identity: string;
  motivation: string;
  conflict: string;
};

export type BookPlan = {
  title_candidates: string[];
  core_hook: string;
  genre: string;
  target_reader: string;
  world_setting: string;
  protagonist: CharacterCard;
  main_antagonist: CharacterCard;
  golden_finger: string;
  main_conflict: string;
  volume_outline: string[];
  first_three_chapters: string[];
  long_term_payoffs: string[];
  risks: string[];
};

export type BookPlanResponse = {
  project_id: string;
  plan: BookPlan;
  saved_path: string;
};

export type ProjectSummary = {
  project_id: string;
  title: string;
  genre: string;
  core_hook: string;
  updated_at: string;
  saved_path: string;
};

export type ProjectDetailResponse = {
  project_id: string;
  plan: BookPlan;
  saved_path: string;
};

export type ChapterCatalogItem = {
  chapter_no: number;
  title: string;
  summary: string;
  hook?: string;
  has_outline?: boolean;
  has_draft?: boolean;
};

export type ChapterCatalog = {
  volume_index: number;
  volume_title: string;
  chapters: ChapterCatalogItem[];
};

export type ChapterCatalogResponse = {
  project_id: string;
  catalog: ChapterCatalog;
  saved_path: string;
};

export type ChapterOutline = {
  chapter_no: number;
  title: string;
  goal: string;
  conflict: string;
  key_events: string[];
  characters: string[];
  ending_hook: string;
  continuity_notes: string[];
};

export type ChapterOutlineResponse = {
  project_id: string;
  outline: ChapterOutline;
  saved_path: string;
};

export type ChapterDraft = {
  chapter_no: number;
  title: string;
  content: string;
  summary: string;
  continuity_updates: string[];
};

export type ChapterDraftResponse = {
  project_id: string;
  draft: ChapterDraft;
  saved_path: string;
};

export type LLMSettings = {
  provider: string;
  model: string;
  base_url: string;
  has_api_key: boolean;
  api_key_preview: string;
  source: string;
  config_path: string;
};

export type LLMSettingsUpdate = {
  provider: string;
  api_key?: string;
  model: string;
  base_url: string;
};

export type LLMConnectionTestResponse = {
  ok: boolean;
  message: string;
};
