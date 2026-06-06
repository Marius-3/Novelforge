from typing import List

from fastapi import FastAPI, HTTPException

from app.llm_service import LLMService, LLMServiceError
from app.schemas import (
    BookPlanRequest,
    BookPlanResponse,
    ChapterCatalogRequest,
    ChapterCatalogResponse,
    ChapterDraftRequest,
    ChapterDraftResponse,
    ChapterOutlineRequest,
    ChapterOutlineResponse,
    ChapterStatusSummary,
    ProjectDetailResponse,
    ProjectSummary,
)
from app.storage import (
    list_chapters,
    list_projects,
    load_book_plan,
    load_chapter_catalog,
    load_chapter_draft,
    load_chapter_outline,
    save_book_plan,
    save_chapter_catalog,
    save_chapter_draft,
    save_chapter_outline,
)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="NovelForge API",
    description="AI 小说创作工作台后端 MVP",
    version="0.3.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm_service = LLMService()


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "NovelForge API is running."}


@app.post("/api/director/book-plan", response_model=BookPlanResponse)
def create_book_plan(request: BookPlanRequest):
    try:
        plan = llm_service.generate_book_plan(request)
        project_id, saved_path = save_book_plan(plan)
        return BookPlanResponse(project_id=project_id, plan=plan, saved_path=saved_path)
    except LLMServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/projects", response_model=List[ProjectSummary])
def get_projects():
    return list_projects()


@app.get("/api/projects/{project_id}", response_model=ProjectDetailResponse)
def get_project(project_id: str):
    try:
        plan, saved_path = load_book_plan(project_id)
        return ProjectDetailResponse(
            project_id=project_id,
            plan=plan,
            saved_path=saved_path,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post(
    "/api/projects/{project_id}/chapters/catalog",
    response_model=ChapterCatalogResponse,
)
def create_chapter_catalog(project_id: str, request: ChapterCatalogRequest):
    """为某个小说项目生成章节目录。"""

    try:
        plan, _ = load_book_plan(project_id)
        catalog = llm_service.generate_chapter_catalog(plan, request)
        saved_path = save_chapter_catalog(project_id, catalog)
        return ChapterCatalogResponse(
            project_id=project_id,
            catalog=catalog,
            saved_path=saved_path,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except LLMServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get(
    "/api/projects/{project_id}/chapters",
    response_model=List[ChapterStatusSummary],
)
def get_chapters(project_id: str):
    """查看章节列表，以及每章是否已经生成大纲和正文。"""

    try:
        # 先确认项目存在
        load_book_plan(project_id)
        return list_chapters(project_id)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=f"找不到章节目录。请先调用 POST /api/projects/{project_id}/chapters/catalog。原始错误：{exc}",
        ) from exc


@app.post(
    "/api/projects/{project_id}/chapters/outline",
    response_model=ChapterOutlineResponse,
)
def create_chapter_outline(project_id: str, request: ChapterOutlineRequest):
    """为某一章生成详细大纲。"""

    try:
        plan, _ = load_book_plan(project_id)
        catalog, _ = load_chapter_catalog(project_id)
        outline = llm_service.generate_chapter_outline(plan, catalog, request)
        saved_path = save_chapter_outline(project_id, outline)
        return ChapterOutlineResponse(
            project_id=project_id,
            outline=outline,
            saved_path=saved_path,
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=f"缺少项目或章节目录。请先生成书级方案和章节目录。原始错误：{exc}",
        ) from exc
    except LLMServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get(
    "/api/projects/{project_id}/chapters/{chapter_no}/outline",
    response_model=ChapterOutlineResponse,
)
def get_chapter_outline(project_id: str, chapter_no: int):
    """读取某一章大纲。"""

    try:
        outline, saved_path = load_chapter_outline(project_id, chapter_no)
        return ChapterOutlineResponse(
            project_id=project_id,
            outline=outline,
            saved_path=saved_path,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post(
    "/api/projects/{project_id}/chapters/draft",
    response_model=ChapterDraftResponse,
)
def create_chapter_draft(project_id: str, request: ChapterDraftRequest):
    """为某一章生成正文。"""

    try:
        plan, _ = load_book_plan(project_id)
        catalog, _ = load_chapter_catalog(project_id)
        outline, _ = load_chapter_outline(project_id, request.chapter_no)
        draft = llm_service.generate_chapter_draft(plan, catalog, outline, request)
        saved_path = save_chapter_draft(project_id, draft)
        return ChapterDraftResponse(
            project_id=project_id,
            draft=draft,
            saved_path=saved_path,
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=f"缺少项目、章节目录或该章大纲。请先生成章节目录和该章大纲。原始错误：{exc}",
        ) from exc
    except LLMServiceError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get(
    "/api/projects/{project_id}/chapters/{chapter_no}/draft",
    response_model=ChapterDraftResponse,
)
def get_chapter_draft(project_id: str, chapter_no: int):
    """读取某一章正文。"""

    try:
        draft, saved_path = load_chapter_draft(project_id, chapter_no)
        return ChapterDraftResponse(
            project_id=project_id,
            draft=draft,
            saved_path=saved_path,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
