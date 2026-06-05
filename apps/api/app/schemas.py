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