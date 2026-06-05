# NovelForge Starter

这是一个从 0 开始的 AI 小说创作工作台后端 MVP。

第一版目标：

1. 启动 FastAPI 后端。
2. 打开浏览器看到接口文档。
3. 输入一句小说创意。
4. 生成结构化“书级方案”。
5. 保存到本地 `data/projects/` 文件夹。

## 目录结构

```text
novelforge-starter/
├── apps/
│   └── api/
│       ├── app/
│       │   ├── main.py
│       │   ├── config.py
│       │   ├── schemas.py
│       │   ├── llm_service.py
│       │   └── storage.py
│       ├── data/
│       │   └── projects/
│       ├── requirements.txt
│       └── .env.example
└── docs/
    └── beginner-notes.md
```

## 第一次运行

进入后端目录：

```bash
cd apps/api
```

创建虚拟环境：

```bash
python -m venv .venv
```

Windows PowerShell 激活虚拟环境：

```powershell
.\.venv\Scripts\Activate.ps1
```

安装依赖：

```bash
pip install -r requirements.txt
```

复制环境变量文件：

```powershell
copy .env.example .env
```

启动后端：

```bash
uvicorn app.main:app --reload
```

浏览器打开：

```text
http://127.0.0.1:8000/docs
```

先测试：

```text
GET /health
```

然后测试：

```text
POST /api/director/book-plan
```

## 使用真实 DeepSeek

默认 `.env` 中是：

```text
LLM_PROVIDER=mock
```

这表示不调用真实 AI，只返回一个示例结果，适合先检查项目能不能跑通。

要使用 DeepSeek，把 `.env` 改成：

```text
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=你的真实APIKey
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

然后重启后端。
