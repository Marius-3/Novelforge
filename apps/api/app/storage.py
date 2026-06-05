import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from app.config import settings
from app.schemas import BookPlan, ProjectSummary


def get_projects_root() -> Path:
    """返回所有小说项目所在的根目录。"""

    root = Path(settings.data_dir) / "projects"
    root.mkdir(parents=True, exist_ok=True)
    return root


def save_book_plan(plan: BookPlan) -> tuple[str, str]:
    """把书级方案保存到本地 JSON 文件。"""

    project_id = str(uuid4())
    project_dir = get_projects_root() / project_id
    project_dir.mkdir(parents=True, exist_ok=True)

    save_path = project_dir / "book_plan.json"
    save_path.write_text(
        json.dumps(plan.model_dump(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return project_id, str(save_path)


def load_book_plan(project_id: str) -> tuple[BookPlan, str]:
    """读取某个小说项目的书级方案。"""

    save_path = get_projects_root() / project_id / "book_plan.json"

    if not save_path.exists():
        raise FileNotFoundError(f"找不到项目：{project_id}")

    raw_text = save_path.read_text(encoding="utf-8")
    data = json.loads(raw_text)
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
            raw_text = save_path.read_text(encoding="utf-8")
            data = json.loads(raw_text)
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