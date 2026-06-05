from typing import List

from fastapi import FastAPI, HTTPException

from app.llm_service import LLMService, LLMServiceError
from app.schemas import (
    BookPlanRequest,
    BookPlanResponse,
    ProjectDetailResponse,
    ProjectSummary,
)
from app.storage import list_projects, load_book_plan, save_book_plan

app = FastAPI(
    title="NovelForge API",
    description="AI 小说创作工作台后端 MVP",
    version="0.2.0",
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