import json
from json import JSONDecodeError

from openai import OpenAI

from app.settings_service import EffectiveLLMConfig, get_effective_llm_config
from app.schemas import (
    BookPlan,
    BookPlanRequest,
    ChapterCatalog,
    ChapterCatalogRequest,
    ChapterDraft,
    ChapterDraftRequest,
    ChapterOutline,
    ChapterOutlineRequest,
)


class LLMServiceError(RuntimeError):
    pass


class LLMService:
    """AI 调用层。

    支持两个 provider：
    - mock：不调用真实 AI，返回固定示例。
    - deepseek：调用 DeepSeek OpenAI-compatible API。
    """

    def generate_book_plan(self, request: BookPlanRequest) -> BookPlan:
        config = self._current_config()
        provider = config.provider
        if provider == "mock":
            return self._mock_book_plan(request)
        if provider == "deepseek":
            return self._deepseek_book_plan(request)
        raise LLMServiceError(f"不支持的模型服务商：{provider}")

    def generate_chapter_catalog(
        self,
        plan: BookPlan,
        request: ChapterCatalogRequest,
    ) -> ChapterCatalog:
        config = self._current_config()
        provider = config.provider
        if provider == "mock":
            return self._mock_chapter_catalog(plan, request)
        if provider == "deepseek":
            return self._deepseek_chapter_catalog(plan, request)
        raise LLMServiceError(f"不支持的模型服务商：{provider}")

    def generate_chapter_outline(
        self,
        plan: BookPlan,
        catalog: ChapterCatalog,
        request: ChapterOutlineRequest,
    ) -> ChapterOutline:
        config = self._current_config()
        provider = config.provider
        if provider == "mock":
            return self._mock_chapter_outline(plan, catalog, request)
        if provider == "deepseek":
            return self._deepseek_chapter_outline(plan, catalog, request)
        raise LLMServiceError(f"不支持的模型服务商：{provider}")

    def generate_chapter_draft(
        self,
        plan: BookPlan,
        catalog: ChapterCatalog,
        outline: ChapterOutline,
        request: ChapterDraftRequest,
    ) -> ChapterDraft:
        config = self._current_config()
        provider = config.provider
        if provider == "mock":
            return self._mock_chapter_draft(plan, catalog, outline, request)
        if provider == "deepseek":
            return self._deepseek_chapter_draft(plan, catalog, outline, request)
        raise LLMServiceError(f"不支持的模型服务商：{provider}")

    def _current_config(self) -> EffectiveLLMConfig:
        return get_effective_llm_config()

    def test_connection(self) -> str:
        """测试当前模型配置是否可用。"""

        config = self._current_config()
        if config.provider == "mock":
            return "当前为 mock 模式，不会调用真实模型。"
        if config.provider != "deepseek":
            raise LLMServiceError(f"不支持的模型服务商：{config.provider}")

        try:
            client = self._deepseek_client(config)
            response = client.chat.completions.create(
                model=config.model,
                messages=[
                    {"role": "system", "content": "你只返回 JSON。"},
                    {"role": "user", "content": "请只返回 {\"ok\": true}。"},
                ],
                response_format={"type": "json_object"},
                temperature=0,
                max_tokens=50,
            )
            content = response.choices[0].message.content or ""
            if not content.strip():
                raise LLMServiceError("模型返回为空。")
            return "DeepSeek 连接成功。"
        except Exception as exc:
            if isinstance(exc, LLMServiceError):
                raise
            raise LLMServiceError(f"DeepSeek 连接失败：{exc}") from exc

    def _deepseek_client(self, config: EffectiveLLMConfig | None = None) -> OpenAI:
        config = config or self._current_config()
        if not config.api_key or config.api_key == "your_deepseek_api_key_here":
            raise LLMServiceError(
                "未配置 DeepSeek API Key。请在网页右上角“模型设置”中填写 API Key，"
                "或把模型服务商改为 mock。"
            )

        return OpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
        )

    def _deepseek_json(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
        temperature: float = 0.7,
    ) -> dict:
        """调用 DeepSeek，并要求模型只返回 JSON。"""

        try:
            config = self._current_config()
            client = self._deepseek_client(config)
            response = client.chat.completions.create(
                model=config.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message.content or "{}"
            return json.loads(content)
        except JSONDecodeError as exc:
            raise LLMServiceError(f"AI 返回内容不是合法 JSON：{exc}") from exc
        except Exception as exc:
            raise LLMServiceError(f"AI 调用失败：{exc}") from exc

    def _deepseek_book_plan(self, request: BookPlanRequest) -> BookPlan:
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
            data = self._deepseek_json(system_prompt, user_prompt, max_tokens=3000)
            return BookPlan.model_validate(data)
        except Exception as exc:
            if isinstance(exc, LLMServiceError):
                raise
            raise LLMServiceError(f"生成书级方案失败：{exc}") from exc

    def _deepseek_chapter_catalog(
        self,
        plan: BookPlan,
        request: ChapterCatalogRequest,
    ) -> ChapterCatalog:
        system_prompt = """
你是一个专业网文责编，擅长把书级方案拆成可连载的章节目录。
必须只输出 JSON，不要输出 Markdown，不要解释。
JSON 字段必须严格符合下面结构：
{
  "volume_index": 1,
  "volume_title": "卷名",
  "chapters": [
    {
      "chapter_no": 1,
      "title": "章节标题",
      "summary": "本章剧情梗概",
      "hook": "本章结尾钩子"
    }
  ]
}
""".strip()

        user_prompt = f"""
请基于下面书级方案，生成第 {request.volume_index} 卷的章节目录。

书名候选：{plan.title_candidates}
核心卖点：{plan.core_hook}
类型：{plan.genre}
世界观：{plan.world_setting}
主角：{plan.protagonist.model_dump()}
主要反派：{plan.main_antagonist.model_dump()}
金手指：{plan.golden_finger}
主线冲突：{plan.main_conflict}
卷纲：{plan.volume_outline}
前三章：{plan.first_three_chapters}
长期爽点：{plan.long_term_payoffs}
风险点：{plan.risks}

本次需要生成章节数：{request.total_chapters}
额外要求：{request.extra_requirements or "无"}

要求：
1. chapter_no 从 1 开始连续编号。
2. 每章都要有明确推进，不要写成空泛设定。
3. 每章 summary 要说明冲突、行动和结果。
4. hook 要制造下一章阅读动力。
5. 必须返回 JSON。
""".strip()

        try:
            data = self._deepseek_json(system_prompt, user_prompt, max_tokens=4000)
            return ChapterCatalog.model_validate(data)
        except Exception as exc:
            if isinstance(exc, LLMServiceError):
                raise
            raise LLMServiceError(f"生成章节目录失败：{exc}") from exc

    def _deepseek_chapter_outline(
        self,
        plan: BookPlan,
        catalog: ChapterCatalog,
        request: ChapterOutlineRequest,
    ) -> ChapterOutline:
        target_chapter = next(
            (chapter for chapter in catalog.chapters if chapter.chapter_no == request.chapter_no),
            None,
        )

        if target_chapter is None:
            raise LLMServiceError(f"章节目录中没有第 {request.chapter_no} 章。")

        system_prompt = """
你是一个专业网文细纲编辑。你的任务是把某一章的章节梗概扩展成可执行的单章大纲。
必须只输出 JSON，不要输出 Markdown，不要解释。
JSON 字段必须严格符合下面结构：
{
  "chapter_no": 1,
  "title": "章节标题",
  "goal": "本章写作目标",
  "conflict": "本章核心冲突",
  "key_events": ["事件1", "事件2", "事件3"],
  "characters": ["出场人物1", "出场人物2"],
  "ending_hook": "章末钩子",
  "continuity_notes": ["需要延续的设定或伏笔"]
}
""".strip()

        user_prompt = f"""
请为第 {request.chapter_no} 章生成详细大纲。

书级方案：
核心卖点：{plan.core_hook}
世界观：{plan.world_setting}
主角：{plan.protagonist.model_dump()}
主要反派：{plan.main_antagonist.model_dump()}
金手指：{plan.golden_finger}
主线冲突：{plan.main_conflict}

当前章节目录：
卷号：{catalog.volume_index}
卷名：{catalog.volume_title}
全部章节：{[chapter.model_dump() for chapter in catalog.chapters]}

目标章节：{target_chapter.model_dump()}
额外要求：{request.extra_requirements or "无"}

要求：
1. 大纲要具体到可直接写正文。
2. key_events 至少 5 条。
3. 必须体现人物动机、障碍、行动、结果。
4. 不要提前解决全书主线。
5. 必须返回 JSON。
""".strip()

        try:
            data = self._deepseek_json(system_prompt, user_prompt, max_tokens=3500)
            return ChapterOutline.model_validate(data)
        except Exception as exc:
            if isinstance(exc, LLMServiceError):
                raise
            raise LLMServiceError(f"生成章节大纲失败：{exc}") from exc

    def _deepseek_chapter_draft(
        self,
        plan: BookPlan,
        catalog: ChapterCatalog,
        outline: ChapterOutline,
        request: ChapterDraftRequest,
    ) -> ChapterDraft:
        system_prompt = """
你是一个专业网文作者，擅长根据章节大纲写出节奏清晰、冲突明确、适合连载的正文。
必须只输出 JSON，不要输出 Markdown，不要解释。
JSON 字段必须严格符合下面结构：
{
  "chapter_no": 1,
  "title": "章节标题",
  "content": "章节正文",
  "summary": "本章摘要",
  "continuity_updates": ["本章新增设定、人物状态变化或伏笔"]
}
""".strip()

        user_prompt = f"""
请根据下面信息写第 {request.chapter_no} 章正文。

书级方案：
核心卖点：{plan.core_hook}
类型：{plan.genre}
目标读者：{plan.target_reader}
世界观：{plan.world_setting}
主角：{plan.protagonist.model_dump()}
主要反派：{plan.main_antagonist.model_dump()}
金手指：{plan.golden_finger}
主线冲突：{plan.main_conflict}
长期爽点：{plan.long_term_payoffs}
风险点：{plan.risks}

章节目录：{[chapter.model_dump() for chapter in catalog.chapters]}

本章大纲：{outline.model_dump()}
目标字数：{request.target_words}
额外要求：{request.extra_requirements or "无"}

正文要求：
1. 使用中文网文叙事，不要写成大纲或说明书。
2. 开头尽快进入场景和冲突。
3. 保留主角限制，不能让金手指无代价解决一切。
4. 对话、动作、心理、环境要服务剧情推进。
5. 结尾必须形成下一章钩子。
6. content 字段放完整正文。
7. 必须返回 JSON。
""".strip()

        try:
            data = self._deepseek_json(system_prompt, user_prompt, max_tokens=6000, temperature=0.8)
            return ChapterDraft.model_validate(data)
        except Exception as exc:
            if isinstance(exc, LLMServiceError):
                raise
            raise LLMServiceError(f"生成章节正文失败：{exc}") from exc

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

    def _mock_chapter_catalog(
        self,
        plan: BookPlan,
        request: ChapterCatalogRequest,
    ) -> ChapterCatalog:
        chapters = []
        for index in range(1, request.total_chapters + 1):
            chapters.append(
                {
                    "chapter_no": index,
                    "title": f"第{index}章 药铺风波",
                    "summary": f"秦照在药铺中遇到第 {index} 个麻烦，并用天衍系统和基础医理找到突破口。",
                    "hook": "一个看似普通的病人，暴露出城中疫病的异常源头。",
                }
            )

        return ChapterCatalog.model_validate(
            {
                "volume_index": request.volume_index,
                "volume_title": "第一卷：药铺微光",
                "chapters": chapters,
            }
        )

    def _mock_chapter_outline(
        self,
        plan: BookPlan,
        catalog: ChapterCatalog,
        request: ChapterOutlineRequest,
    ) -> ChapterOutline:
        target_chapter = next(
            (chapter for chapter in catalog.chapters if chapter.chapter_no == request.chapter_no),
            None,
        )
        title = target_chapter.title if target_chapter else f"第{request.chapter_no}章 未命名"

        return ChapterOutline.model_validate(
            {
                "chapter_no": request.chapter_no,
                "title": title,
                "goal": "让秦照第一次用现代医学思路解决修仙世界的小危机。",
                "conflict": "药铺掌柜只相信旧药方，病人家属急于求救，秦照却没有正式医师身份。",
                "key_events": [
                    "秦照在药铺整理药材时发现病人症状不合常理。",
                    "掌柜按照旧方用药，病人却出现恶化迹象。",
                    "秦照借天衍系统分析症状，判断不是普通风寒。",
                    "他用有限药材提出替代处理办法，引发旁人质疑。",
                    "病人症状暂时稳定，但瞎眼乞丐在门外听见了关键判断。",
                ],
                "characters": ["秦照", "药铺掌柜", "病人家属", "瞎眼乞丐"],
                "ending_hook": "瞎眼乞丐低声说：这小子，竟真能看出疫根。",
                "continuity_notes": [
                    "秦照体弱，不能用武力破局。",
                    "天衍系统只能辅助分析，不能直接治病。",
                    "瞎眼乞丐开始注意秦照。",
                ],
            }
        )

    def _mock_chapter_draft(
        self,
        plan: BookPlan,
        catalog: ChapterCatalog,
        outline: ChapterOutline,
        request: ChapterDraftRequest,
    ) -> ChapterDraft:
        content = f"""
{outline.title}

暮色压在青石巷上，药铺门前的灯笼被风吹得轻轻摇晃。

秦照抱着一捆晒干的药草，从后院慢慢走出来。只是这几步路，他胸口便有些发闷，指尖也泛着冷意。

他这具身体太弱了。

弱到连搬药都要分三次，弱到药铺里的伙计都敢把最累的活推给他。可秦照知道，自己能在这个世界活到今天，已经不容易。

就在这时，门外忽然传来一阵急促的拍门声。

“掌柜的！救命！我爹快不行了！”

药铺掌柜皱着眉走出柜台。秦照抬眼看去，只见两个汉子抬着一个脸色青灰的老人冲进来。老人嘴唇发紫，呼吸短促，额头却不见高热。

秦照的眉头微不可察地皱了一下。

这不像普通风寒。

掌柜已经开始抓药，嘴里念着旧方。秦照站在一旁，脑海中忽然浮现出一行淡淡的字迹。

【症状记录中。】

【寒热表现不匹配。】

【疑似外邪入肺，兼有毒性反应。】

秦照心头一沉。

他没有立刻开口。一个药铺帮工，没有资格质疑掌柜，更没有资格碰病人。可如果这副药真灌下去，老人可能撑不过今晚。

“掌柜。”秦照低声道，“这方子恐怕不合适。”

药铺里瞬间安静下来。

掌柜抬起头，眼神沉了下去：“你懂药？”

秦照垂着手，声音不高，却很稳：“他不是单纯风寒。若再用发散之药，气会更虚。”

病人家属急得眼睛发红：“那你说怎么办？”

秦照看了一眼药柜，又看了一眼老人胸口起伏的节奏。

他知道，自己没有退路了。

门外，一个披着破布的瞎眼乞丐靠在墙边，原本浑浊的脸上，忽然露出一丝极淡的笑。

“有意思。”他低声说，“这小子，竟真能看出疫根。”
""".strip()

        return ChapterDraft.model_validate(
            {
                "chapter_no": request.chapter_no,
                "title": outline.title,
                "content": content,
                "summary": "秦照在药铺发现病人症状异常，首次质疑旧方，并引起瞎眼乞丐注意。",
                "continuity_updates": [
                    "秦照体弱设定得到展示。",
                    "天衍系统具备症状分析能力。",
                    "瞎眼乞丐确认秦照可能看出疫病根源。",
                ],
            }
        )
