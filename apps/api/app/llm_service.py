import json
from json import JSONDecodeError

from openai import OpenAI

from app.config import settings
from app.schemas import BookPlan, BookPlanRequest


class LLMServiceError(RuntimeError):
    pass


class LLMService:
    """AI 调用层。

    第一版支持两个 provider：
    - mock：不调用真实 AI，返回固定示例。
    - deepseek：调用 DeepSeek OpenAI-compatible API。
    """

    def generate_book_plan(self, request: BookPlanRequest) -> BookPlan:
        provider = settings.llm_provider.lower().strip()
        if provider == "mock":
            return self._mock_book_plan(request)
        if provider == "deepseek":
            return self._deepseek_book_plan(request)
        raise LLMServiceError(f"不支持的 LLM_PROVIDER：{settings.llm_provider}")

    def _deepseek_book_plan(self, request: BookPlanRequest) -> BookPlan:
        if not settings.deepseek_api_key or settings.deepseek_api_key == "your_deepseek_api_key_here":
            raise LLMServiceError(
                "未配置 DEEPSEEK_API_KEY。请打开 apps/api/.env，填入真实 DeepSeek API Key，"
                "或把 LLM_PROVIDER 改回 mock。"
            )

        client = OpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
        )

        system_prompt = """
你是一个专业网文总编和长篇小说策划系统。你的任务是根据用户创意生成结构化书级方案。
必须只输出 JSON，不要输出 Markdown，不要解释。
JSON 字段必须严格符合下面结构：
{
  "title_candidates": ["书名1", "书名2", "书名3"],
  "core_hook": "核心卖点",
  "genre": "类型",
  "target_reader": "目标读者",
  "world_setting": "世界观",
  "protagonist": {
    "name": "主角名",
    "role": "角色定位",
    "identity": "身份",
    "motivation": "动机",
    "conflict": "核心矛盾"
  },
  "main_antagonist": {
    "name": "反派名",
    "role": "角色定位",
    "identity": "身份",
    "motivation": "动机",
    "conflict": "与主角的冲突"
  },
  "golden_finger": "金手指机制",
  "main_conflict": "主线冲突",
  "volume_outline": ["第一卷", "第二卷", "第三卷"],
  "first_three_chapters": ["第一章梗概", "第二章梗概", "第三章梗概"],
  "long_term_payoffs": ["长期爽点1", "长期爽点2"],
  "risks": ["潜在问题1", "潜在问题2"]
}
""".strip()

        user_prompt = f"""
小说创意：{request.premise}
类型：{request.genre}
文风：{request.style}

请生成一个适合长篇连载的书级方案 JSON。
""".strip()

        try:
            response = client.chat.completions.create(
                model=settings.deepseek_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=3000,
            )
            content = response.choices[0].message.content or "{}"
            data = json.loads(content)
            return BookPlan.model_validate(data)
        except JSONDecodeError as exc:
            raise LLMServiceError(f"AI 返回内容不是合法 JSON：{exc}") from exc
        except Exception as exc:
            raise LLMServiceError(f"生成书级方案失败：{exc}") from exc

    def _mock_book_plan(self, request: BookPlanRequest) -> BookPlan:
        """不调用真实 AI 的示例结果。"""

        return BookPlan.model_validate(
            {
                "title_candidates": ["天衍医途", "药铺里的天衍者", "病骨问长生"],
                "core_hook": "体弱穿越者不能练武，却用现代医学和天衍系统破解修仙世界的疫病、毒术与长生骗局。",
                "genre": request.genre,
                "target_reader": "喜欢修仙、成长、医学破局和智斗爽点的网文读者。",
                "world_setting": "一个武道、仙门、药术和疫病秘法并存的架空修仙世界。底层凡人受病灾、药价和宗门垄断压迫。",
                "protagonist": {
                    "name": "秦照",
                    "role": "体弱药铺帮工 / 穿越者 / 医学体系开拓者",
                    "identity": "没有练武天赋的凡人少年，携带天衍系统。",
                    "motivation": "活下去，并在异世建立真正可验证、可传播的医学体系。",
                    "conflict": "身体孱弱、资源匮乏，又被掌握疫病秘术的敌人盯上。",
                },
                "main_antagonist": {
                    "name": "瞎眼乞丐",
                    "role": "早期隐性反派 / 疫病术修行者",
                    "identity": "重伤潜伏城中的疫病修士。",
                    "motivation": "借城中大疫恢复修为，同时试探秦照是否掌握克制疫病的方法。",
                    "conflict": "他想放疫取利，秦照必须用医学和天衍系统阻止灾难。",
                },
                "golden_finger": "天衍系统可辅助分析病因、药性、传播路径和治疗方案，但需要秦照自行验证、实践和承担代价。",
                "main_conflict": "秦照以现代医学思想挑战修仙世界的药术垄断、疫病邪法和长生骗局。",
                "volume_outline": [
                    "第一卷：药铺微光——秦照在小城疫病危机中显露锋芒。",
                    "第二卷：医道入局——秦照被宗门、药商和官府共同关注。",
                    "第三卷：疫术真相——揭开疫病修士背后的长生实验。",
                ],
                "first_three_chapters": [
                    "第一章：病骨药铺。秦照在药铺帮工，救治小病患者，暴露出异常医理。",
                    "第二章：瞎眼乞丐。秦照治过的乞丐发现他可能克制疫病，暗中试探。",
                    "第三章：风寒不寒。城中出现异常病症，秦照发现这不是普通风寒。",
                ],
                "long_term_payoffs": [
                    "用显微、隔离、消毒等现代医学思想破解修仙疫术。",
                    "从小药铺成长为影响王朝和仙门的医道开创者。",
                    "天衍系统从辅助诊断逐渐揭示世界底层法则。",
                ],
                "risks": [
                    "医学知识不能写成说明书，要通过剧情冲突展示。",
                    "主角体弱设定需要持续制造限制，避免金手指过强。",
                ],
            }
        )
