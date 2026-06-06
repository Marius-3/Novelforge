from typing import List
from pydantic import BaseModel, Field


class BookPlanRequest(BaseModel):
    """用户输入的小说创意。"""

    premise: str = Field(..., min_length=5, description="一句或一段小说创意")
    genre: str = Field(default="玄幻/修仙", description="小说类型，例如玄幻、都市、科幻、悬疑")
    style: str = Field(default="网文爽文，节奏紧凑", description="期望文风")


class CharacterCard(BaseModel):
    name: str
    role: str
    identity: str
    motivation: str
    conflict: str


class BookPlan(BaseModel):
    title_candidates: List[str]
    core_hook: str
    genre: str
    target_reader: str
    world_setting: str
    protagonist: CharacterCard
    main_antagonist: CharacterCard
    golden_finger: str
    main_conflict: str
    volume_outline: List[str]
    first_three_chapters: List[str]
    long_term_payoffs: List[str]
    risks: List[str]


class BookPlanResponse(BaseModel):
    project_id: str
    plan: BookPlan
    saved_path: str


class ProjectSummary(BaseModel):
    """项目列表里展示的简略信息。"""

    project_id: str
    title: str
    genre: str
    core_hook: str
    updated_at: str
    saved_path: str


class ProjectDetailResponse(BaseModel):
    """读取某个项目时返回的详细信息。"""

    project_id: str
    plan: BookPlan
    saved_path: str


class ChapterCatalogRequest(BaseModel):
    """生成章节目录的请求。"""

    volume_index: int = Field(default=1, ge=1, description="第几卷，从 1 开始")
    total_chapters: int = Field(default=10, ge=1, le=50, description="本次生成多少章")
    extra_requirements: str = Field(default="", description="额外要求，例如前三章更强钩子")


class ChapterBrief(BaseModel):
    chapter_no: int
    title: str
    summary: str
    hook: str


class ChapterCatalog(BaseModel):
    volume_index: int
    volume_title: str
    chapters: List[ChapterBrief]


class ChapterCatalogResponse(BaseModel):
    project_id: str
    catalog: ChapterCatalog
    saved_path: str


class ChapterOutlineRequest(BaseModel):
    """生成单章大纲的请求。"""

    chapter_no: int = Field(..., ge=1, description="要生成第几章大纲")
    extra_requirements: str = Field(default="", description="额外要求")


class ChapterOutline(BaseModel):
    chapter_no: int
    title: str
    goal: str
    conflict: str
    key_events: List[str]
    characters: List[str]
    ending_hook: str
    continuity_notes: List[str]


class ChapterOutlineResponse(BaseModel):
    project_id: str
    outline: ChapterOutline
    saved_path: str


class ChapterDraftRequest(BaseModel):
    """生成单章正文的请求。"""

    chapter_no: int = Field(..., ge=1, description="要生成第几章正文")
    target_words: int = Field(default=1500, ge=500, le=6000, description="目标字数")
    extra_requirements: str = Field(default="", description="额外要求")


class ChapterDraft(BaseModel):
    chapter_no: int
    title: str
    content: str
    summary: str
    continuity_updates: List[str]


class ChapterDraftResponse(BaseModel):
    project_id: str
    draft: ChapterDraft
    saved_path: str


class ChapterStatusSummary(BaseModel):
    """章节列表里展示的状态。"""

    chapter_no: int
    title: str
    summary: str
    has_outline: bool
    has_draft: bool


class LLMSettingsUpdate(BaseModel):
    """网页模型设置表单。"""

    provider: str = Field(default="deepseek", description="模型服务商：mock 或 deepseek")
    api_key: str | None = Field(default=None, description="API Key。为空时保留旧 Key。")
    model: str = Field(default="deepseek-chat", description="模型名称")
    base_url: str = Field(default="https://api.deepseek.com", description="OpenAI-compatible Base URL")


class LLMSettingsResponse(BaseModel):
    """返回给前端的模型配置状态。不会返回完整 API Key。"""

    provider: str
    model: str
    base_url: str
    has_api_key: bool
    api_key_preview: str
    source: str
    config_path: str


class LLMConnectionTestResponse(BaseModel):
    ok: bool
    message: str
