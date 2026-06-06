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

export type ChapterCatalogResponse = {
  project_id: string;
  volume_index: number;
  volume_title: string;
  chapters: ChapterCatalogItem[];
  saved_path: string;
};

export type ChapterOutlineResponse = {
  project_id: string;
  chapter_no: number;
  title: string;
  outline: unknown;
  saved_path: string;
};

export type ChapterDraftResponse = {
  project_id: string;
  chapter_no: number;
  title: string;
  draft: string;
  saved_path: string;
};
