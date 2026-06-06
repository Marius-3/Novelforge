import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from app.config import settings
from app.schemas import (
    BookPlan,
    ChapterCatalog,
    ChapterDraft,
    ChapterOutline,
    ChapterStatusSummary,
    ProjectSummary,
)


def get_projects_root() -> Path:
    """返回所有小说项目所在的根目录。"""

    root = Path(settings.data_dir) / "projects"
    root.mkdir(parents=True, exist_ok=True)
    return root


def get_project_dir(project_id: str) -> Path:
    """返回某个小说项目目录。"""

    return get_projects_root() / project_id


def save_json(path: Path, data: dict) -> str:
    """把字典保存成 JSON 文件。"""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return str(path)


def load_json(path: Path) -> dict:
    """读取 JSON 文件。"""

    if not path.exists():
        raise FileNotFoundError(f"找不到文件：{path}")

    raw_text = path.read_text(encoding="utf-8")
    return json.loads(raw_text)


def save_book_plan(plan: BookPlan) -> tuple[str, str]:
    """把书级方案保存到本地 JSON 文件。"""

    project_id = str(uuid4())
    project_dir = get_project_dir(project_id)
    save_path = project_dir / "book_plan.json"
    saved_path = save_json(save_path, plan.model_dump())

    return project_id, saved_path


def load_book_plan(project_id: str) -> tuple[BookPlan, str]:
    """读取某个小说项目的书级方案。"""

    save_path = get_project_dir(project_id) / "book_plan.json"

    if not save_path.exists():
        raise FileNotFoundError(f"找不到项目：{project_id}")

    data = load_json(save_path)
    plan = BookPlan.model_validate(data)

    return plan, str(save_path)


def list_projects() -> list[ProjectSummary]:
    """列出已经生成过的小说项目。"""

    root = get_projects_root()
    projects: list[ProjectSummary] = []

    for project_dir in root.iterdir():
        if not project_dir.is_dir():
            continue

        save_path = project_dir / "book_plan.json"
        if not save_path.exists():
            continue

        try:
            data = load_json(save_path)
            plan = BookPlan.model_validate(data)

            title = plan.title_candidates[0] if plan.title_candidates else "未命名小说"
            updated_at = datetime.fromtimestamp(save_path.stat().st_mtime).isoformat(
                timespec="seconds"
            )

            projects.append(
                ProjectSummary(
                    project_id=project_dir.name,
                    title=title,
                    genre=plan.genre,
                    core_hook=plan.core_hook,
                    updated_at=updated_at,
                    saved_path=str(save_path),
                )
            )
        except Exception:
            # 某个项目文件坏了，不让整个列表接口崩掉
            continue

    projects.sort(key=lambda item: item.updated_at, reverse=True)
    return projects


def get_chapters_dir(project_id: str) -> Path:
    """返回某个项目的章节目录。"""

    return get_project_dir(project_id) / "chapters"


def save_chapter_catalog(project_id: str, catalog: ChapterCatalog) -> str:
    """保存章节目录。"""

    save_path = get_chapters_dir(project_id) / "catalog.json"
    return save_json(save_path, catalog.model_dump())


def load_chapter_catalog(project_id: str) -> tuple[ChapterCatalog, str]:
    """读取章节目录。"""

    save_path = get_chapters_dir(project_id) / "catalog.json"
    data = load_json(save_path)
    return ChapterCatalog.model_validate(data), str(save_path)


def get_chapter_outline_path(project_id: str, chapter_no: int) -> Path:
    """返回某章大纲文件路径。"""

    filename = f"chapter_{chapter_no:04d}.json"
    return get_chapters_dir(project_id) / "outlines" / filename


def get_chapter_draft_path(project_id: str, chapter_no: int) -> Path:
    """返回某章正文文件路径。"""

    filename = f"chapter_{chapter_no:04d}.json"
    return get_chapters_dir(project_id) / "drafts" / filename


def save_chapter_outline(project_id: str, outline: ChapterOutline) -> str:
    """保存单章大纲。"""

    save_path = get_chapter_outline_path(project_id, outline.chapter_no)
    return save_json(save_path, outline.model_dump())


def load_chapter_outline(project_id: str, chapter_no: int) -> tuple[ChapterOutline, str]:
    """读取单章大纲。"""

    save_path = get_chapter_outline_path(project_id, chapter_no)
    data = load_json(save_path)
    return ChapterOutline.model_validate(data), str(save_path)


def save_chapter_draft(project_id: str, draft: ChapterDraft) -> str:
    """保存单章正文。"""

    save_path = get_chapter_draft_path(project_id, draft.chapter_no)
    return save_json(save_path, draft.model_dump())


def load_chapter_draft(project_id: str, chapter_no: int) -> tuple[ChapterDraft, str]:
    """读取单章正文。"""

    save_path = get_chapter_draft_path(project_id, chapter_no)
    data = load_json(save_path)
    return ChapterDraft.model_validate(data), str(save_path)


def list_chapters(project_id: str) -> list[ChapterStatusSummary]:
    """列出章节目录，以及每章是否已经有大纲和正文。"""

    catalog, _ = load_chapter_catalog(project_id)
    result: list[ChapterStatusSummary] = []

    for chapter in catalog.chapters:
        outline_path = get_chapter_outline_path(project_id, chapter.chapter_no)
        draft_path = get_chapter_draft_path(project_id, chapter.chapter_no)

        result.append(
            ChapterStatusSummary(
                chapter_no=chapter.chapter_no,
                title=chapter.title,
                summary=chapter.summary,
                has_outline=outline_path.exists(),
                has_draft=draft_path.exists(),
            )
        )

    return result
