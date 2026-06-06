import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.config import settings
from app.schemas import LLMSettingsResponse, LLMSettingsUpdate


API_ROOT = Path(__file__).resolve().parents[1]
LOCAL_DIR = API_ROOT / "local"
LLM_CONFIG_PATH = LOCAL_DIR / "llm_config.json"


@dataclass(frozen=True)
class EffectiveLLMConfig:
    provider: str
    api_key: str
    model: str
    base_url: str
    source: str


def _read_local_config() -> dict[str, Any]:
    if not LLM_CONFIG_PATH.exists():
        return {}
    try:
        return json.loads(LLM_CONFIG_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _write_local_config(data: dict[str, Any]) -> None:
    LOCAL_DIR.mkdir(parents=True, exist_ok=True)
    LLM_CONFIG_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _mask_api_key(api_key: str) -> str:
    key = (api_key or "").strip()
    if not key:
        return ""
    if len(key) <= 8:
        return "****"
    return f"{key[:3]}-****{key[-4:]}" if key.startswith("sk-") else f"****{key[-4:]}"


def get_effective_llm_config() -> EffectiveLLMConfig:
    """返回当前真正用于模型调用的配置。

    优先级：
    1. apps/api/local/llm_config.json
    2. apps/api/.env
    3. mock 默认配置
    """

    local = _read_local_config()
    local_provider = str(local.get("provider", "")).strip().lower()

    if local_provider:
        return EffectiveLLMConfig(
            provider=local_provider,
            api_key=str(local.get("api_key", "")).strip(),
            model=str(local.get("model", "deepseek-chat")).strip() or "deepseek-chat",
            base_url=str(local.get("base_url", "https://api.deepseek.com")).strip()
            or "https://api.deepseek.com",
            source="local",
        )

    env_provider = settings.llm_provider.lower().strip() or "mock"
    if env_provider == "deepseek":
        return EffectiveLLMConfig(
            provider="deepseek",
            api_key=settings.deepseek_api_key.strip(),
            model=settings.deepseek_model.strip() or "deepseek-chat",
            base_url=settings.deepseek_base_url.strip() or "https://api.deepseek.com",
            source="env",
        )

    return EffectiveLLMConfig(
        provider="mock",
        api_key="",
        model="mock",
        base_url="",
        source="env" if settings.llm_provider else "default",
    )


def get_llm_settings_response() -> LLMSettingsResponse:
    config = get_effective_llm_config()
    return LLMSettingsResponse(
        provider=config.provider,
        model=config.model,
        base_url=config.base_url,
        has_api_key=bool(config.api_key),
        api_key_preview=_mask_api_key(config.api_key),
        source=config.source,
        config_path=str(LLM_CONFIG_PATH),
    )


def save_llm_settings(payload: LLMSettingsUpdate) -> LLMSettingsResponse:
    provider = payload.provider.lower().strip()
    if provider not in {"mock", "deepseek"}:
        raise ValueError("目前只支持 mock 和 deepseek。")

    existing = _read_local_config()
    api_key = payload.api_key.strip() if payload.api_key is not None else str(existing.get("api_key", "")).strip()
    model = payload.model.strip() if payload.model else "deepseek-chat"
    base_url = payload.base_url.strip() if payload.base_url else "https://api.deepseek.com"

    if provider == "deepseek" and not api_key:
        raise ValueError("使用 deepseek 时必须填写 API Key。")

    data = {
        "provider": provider,
        "model": model,
        "base_url": base_url,
        "api_key": api_key if provider == "deepseek" else "",
    }
    _write_local_config(data)
    return get_llm_settings_response()
