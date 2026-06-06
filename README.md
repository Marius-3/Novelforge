# NovelForge

NovelForge 是一个本地运行的 AI 小说创作工作台。项目目标是帮助用户从一句小说灵感出发，逐步生成书级方案、章节目录、单章大纲和章节正文，并在本地保存小说项目数据。

当前版本已经具备本地用户模式雏形：

- 支持一键初始化环境
- 支持一键启动本地网页工作台
- 支持在网页中配置 DeepSeek API Key
- 支持生成书级方案
- 支持查看小说项目列表
- 支持查看项目详情
- 支持生成章节目录
- 支持生成单章大纲
- 支持生成单章正文
- 所有用户配置和小说数据默认保存在项目文件夹内部

---

## 1. 项目定位

NovelForge 不是单纯的“一次性 AI 写作工具”，而是面向长篇小说创作流程的本地工作台。

它希望逐步实现以下创作链路：

```text
一句灵感
  ↓
书级方案
  ↓
世界观 / 人物 / 金手指 / 主线冲突
  ↓
章节目录
  ↓
单章大纲
  ↓
章节正文
  ↓
后续审校、修订、设定库、长期记忆
```

当前版本重点完成了前半段能力：

```text
灵感输入 → 书级方案 → 小说项目 → 章节目录 → 章节大纲 → 章节正文
```

---

## 2. 当前功能

### 2.1 书级方案生成

用户输入小说创意后，系统会生成结构化书级方案，包括：

- 书名候选
- 核心卖点
- 小说类型
- 目标读者
- 世界观
- 主角设定
- 主要反派
- 金手指机制
- 主线冲突
- 卷纲
- 前三章梗概
- 长期爽点
- 风险点

### 2.2 小说项目管理

每次生成书级方案后，系统会自动创建一个小说项目。

目前支持：

- 查看项目列表
- 查看项目详情
- 在项目内继续生成章节内容

项目数据会保存在：

```text
apps/api/data/projects/
```

### 2.3 章节系统

目前支持：

- 生成章节目录
- 查看章节列表
- 生成指定章节的大纲
- 读取指定章节的大纲
- 生成指定章节的正文
- 读取指定章节的正文

章节数据会保存在：

```text
apps/api/data/projects/项目ID/chapters/
```

其中包括：

```text
catalog.json                       # 章节目录
outlines/chapter_0001.json         # 第 1 章大纲
drafts/chapter_0001.json           # 第 1 章正文
```

### 2.4 网页配置 API Key

当前版本支持在网页中配置模型服务。

支持配置：

- 模型服务商
- API Key
- 模型名称
- Base URL

DeepSeek 示例配置：

```text
Provider: deepseek
Model: deepseek-chat
Base URL: https://api.deepseek.com
```

API Key 会保存到项目内部：

```text
apps/api/local/llm_config.json
```

不会写入系统目录。

### 2.5 一键启动

当前版本提供两个脚本：

```text
setup-novelforge.bat
start-novelforge.bat
```

第一次使用时运行：

```text
setup-novelforge.bat
```

日常使用时运行：

```text
start-novelforge.bat
```

---

## 3. 技术架构

当前项目采用前后端分离架构，但在用户模式下由后端统一托管前端页面。

```text
NovelForge
├── FastAPI 后端
│   ├── 项目管理
│   ├── 章节生成
│   ├── 模型调用
│   ├── API Key 配置
│   └── 本地 JSON 保存
│
├── React 前端
│   ├── 项目列表
│   ├── 项目详情
│   ├── 章节目录
│   ├── 大纲生成
│   ├── 正文生成
│   └── 模型设置
│
└── 本地数据
    ├── 小说项目数据
    ├── 章节数据
    └── 模型配置
```

开发阶段：

```text
前端：React + Vite + TypeScript
后端：FastAPI + Python
模型调用：OpenAI-compatible SDK
数据保存：本地 JSON 文件
```

用户模式：

```text
访问 http://127.0.0.1:8000
  ↓
FastAPI 返回 React 页面
  ↓
React 页面调用同一个 FastAPI 后端接口
```

---

## 4. 项目目录说明

```text
novelforge-starter/
├── setup-novelforge.bat
├── setup-novelforge.ps1
├── start-novelforge.bat
├── README.md
├── .gitignore
├── apps/
│   ├── api/
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── schemas.py
│   │   │   ├── storage.py
│   │   │   ├── llm_service.py
│   │   │   ├── settings_service.py
│   │   │   └── ...
│   │   ├── data/
│   │   │   └── projects/
│   │   ├── local/
│   │   │   └── llm_config.json
│   │   ├── requirements.txt
│   │   └── .env.example
│   │
│   └── web/
│       ├── src/
│       │   ├── App.tsx
│       │   ├── api.ts
│       │   ├── types.ts
│       │   ├── styles.css
│       │   └── ...
│       ├── dist/
│       ├── package.json
│       ├── tsconfig.json
│       └── vite.config.ts
│
└── docs/
```

### 4.1 根目录脚本

#### `setup-novelforge.bat`

首次初始化脚本。

它会调用：

```text
setup-novelforge.ps1
```

完成：

- 检查 Python
- 创建 Python 虚拟环境
- 安装后端依赖
- 检查 Node.js 和 npm
- 安装前端依赖
- 构建前端页面
- 创建本地数据目录

#### `start-novelforge.bat`

日常启动脚本。

它会：

- 启动 FastAPI 后端
- 自动打开浏览器
- 访问 `http://127.0.0.1:8000`

### 4.2 后端目录

```text
apps/api/
```

主要负责：

- 接收前端请求
- 调用 AI 模型
- 保存小说项目数据
- 保存模型配置
- 托管前端静态页面

### 4.3 前端目录

```text
apps/web/
```

主要负责：

- 显示 NovelForge 网页工作台
- 调用后端接口
- 展示项目、章节、大纲和正文
- 提供模型设置页面

### 4.4 本地数据目录

```text
apps/api/data/projects/
```

保存用户生成的小说项目数据。

### 4.5 本地配置目录

```text
apps/api/local/
```

保存用户的模型配置，例如 API Key。

---

## 5. 安装要求

使用前需要安装：

### 5.1 Python

建议版本：

```text
Python 3.12+
```

当前项目已在 Python 3.13 环境下测试运行。

安装 Python 时请勾选：

```text
Add python.exe to PATH
```

### 5.2 Node.js

建议安装 Node.js LTS 版本。

需要包含：

```text
node
npm
```

可以在命令行中检查：

```powershell
node --version
npm --version
```

### 5.3 Git

用于从 GitHub 下载项目和保存代码版本。

检查命令：

```powershell
git --version
```

---

## 6. 快速开始

### 6.1 下载项目

从 GitHub 下载本项目：

```text
https://github.com/Marius-3/Novelforge
```

也可以使用 Git 克隆：

```powershell
git clone https://github.com/Marius-3/Novelforge.git
```

进入项目目录：

```powershell
cd Novelforge
```

如果你的文件夹名称是 `novelforge-starter`，则进入对应文件夹即可。

---

### 6.2 第一次初始化

在项目根目录双击：

```text
setup-novelforge.bat
```

或者在 PowerShell 中运行：

```powershell
.\setup-novelforge.bat
```

成功后会显示：

```text
Setup completed successfully.
You can now run start-novelforge.bat.
```

如果初始化失败，会在项目根目录生成：

```text
setup.log
```

可根据日志排查错误。

---

### 6.3 启动 NovelForge

初始化完成后，双击：

```text
start-novelforge.bat
```

程序会自动打开浏览器：

```text
http://127.0.0.1:8000
```

看到 NovelForge 小说创作平台页面后，即表示启动成功。

---

## 7. 配置 DeepSeek API Key

启动网页后，进入：

```text
模型设置
```

填写：

```text
Provider: deepseek
API Key: 你的 DeepSeek API Key
Model: deepseek-chat
Base URL: https://api.deepseek.com
```

然后点击：

```text
保存设置
测试连接
```

连接成功后，就可以使用真实模型生成小说内容。

---

## 8. 使用流程

推荐使用流程：

```text
1. 启动 NovelForge
2. 进入模型设置
3. 填写并测试 API Key
4. 创建小说项目
5. 输入小说创意
6. 生成书级方案
7. 进入项目详情
8. 生成章节目录
9. 生成单章大纲
10. 生成章节正文
```

---

## 9. 隐私与本地数据说明

当前版本是本地运行模式。

### 9.1 本地保存内容

以下内容保存在项目文件夹内部：

```text
apps/api/data/projects/
```

包括：

- 书级方案
- 小说项目数据
- 章节目录
- 章节大纲
- 章节正文

模型配置保存在：

```text
apps/api/local/llm_config.json
```

包括：

- Provider
- Model
- Base URL
- API Key

### 9.2 不会写入系统目录

当前版本不会把配置写入：

```text
C:\Users\用户名\AppData
Windows Credential Manager
注册表
```

所有用户配置和生成内容都在项目文件夹内部。

### 9.3 注意事项

`apps/api/local/llm_config.json` 中包含 API Key。请不要把它上传到 GitHub，也不要发送给他人。

`apps/api/data/projects/` 中包含你的小说创作内容。请根据需要自行备份，不建议上传公开仓库。

---

## 10. Git 忽略说明

项目应确保 `.gitignore` 中包含：

```gitignore
# Python
__pycache__/
*.py[cod]

# Virtual environment
.venv/
apps/api/.venv/

# Environment variables
.env
apps/api/.env

# Local user config
apps/api/local/

# Local generated novel data
apps/api/data/projects/
apps/api/data/chroma/

# Frontend
apps/web/node_modules/
apps/web/dist/

# Logs
*.log
setup.log

# Editor
.vscode/
.idea/
```

这些内容不应该上传到 GitHub：

```text
apps/api/local/
apps/api/data/projects/
apps/api/.env
apps/api/.venv/
apps/web/node_modules/
apps/web/dist/
setup.log
```

---

## 11. 常见问题

### 11.1 双击 setup 闪退怎么办？

当前版本的 `setup-novelforge.bat` 会调用 PowerShell 脚本：

```text
setup-novelforge.ps1
```

如果仍然失败，可以在 PowerShell 中执行：

```powershell
.\setup-novelforge.bat
```

然后查看：

```text
setup.log
```

### 11.2 启动时报找不到前端构建文件怎么办？

如果出现：

```text
Frontend build was not found.
Please run setup-novelforge.bat first.
```

说明还没有生成：

```text
apps/web/dist/index.html
```

请重新运行：

```text
setup-novelforge.bat
```

或者手动执行：

```powershell
cd apps/web
npm.cmd install
npm.cmd run build
```

### 11.3 PowerShell 不允许运行脚本怎么办？

如果遇到脚本权限问题，可以在 PowerShell 中运行：

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

然后输入：

```text
Y
```

当前版本的 `setup-novelforge.bat` 默认使用：

```text
-ExecutionPolicy Bypass
```

一般不需要手动修改权限。

### 11.4 npm 无法运行怎么办？

如果 PowerShell 中运行：

```powershell
npm --version
```

提示 `.ps1` 被禁止，可以使用：

```powershell
npm.cmd --version
```

项目脚本中默认使用：

```text
npm.cmd
```

### 11.5 API Key 保存在哪里？

保存在：

```text
apps/api/local/llm_config.json
```

这是项目文件夹内部的本地配置文件。

### 11.6 为什么 GitHub 上看不到我生成的小说？

因为小说数据目录被 `.gitignore` 忽略了：

```text
apps/api/data/projects/
```

这是为了避免把私人创作内容上传到公开仓库。

---

## 12. 开发模式

普通用户建议使用：

```text
setup-novelforge.bat
start-novelforge.bat
```

开发者也可以手动启动后端和前端。

### 12.1 启动后端

```powershell
cd apps/api
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

后端地址：

```text
http://127.0.0.1:8000
```

API 文档：

```text
http://127.0.0.1:8000/docs
```

### 12.2 启动前端开发服务器

```powershell
cd apps/web
npm.cmd install
npm.cmd run dev
```

前端开发地址：

```text
http://127.0.0.1:5173
```

---

## 13. 当前已实现接口

### 13.1 基础接口

```text
GET /health
```

检查后端是否运行。

### 13.2 模型设置接口

```text
GET  /api/settings/llm
POST /api/settings/llm
POST /api/settings/llm/test
```

用于读取、保存和测试模型配置。

### 13.3 小说项目接口

```text
POST /api/director/book-plan
GET  /api/projects
GET  /api/projects/{project_id}
```

用于生成书级方案、查看项目列表和查看项目详情。

### 13.4 章节接口

```text
POST /api/projects/{project_id}/chapters/catalog
GET  /api/projects/{project_id}/chapters

POST /api/projects/{project_id}/chapters/outline
GET  /api/projects/{project_id}/chapters/{chapter_no}/outline

POST /api/projects/{project_id}/chapters/draft
GET  /api/projects/{project_id}/chapters/{chapter_no}/draft
```

用于生成章节目录、大纲和正文。

---

## 14. 当前版本限制

当前版本仍然是早期 MVP，存在以下限制：

- 暂未提供正式安装包
- 暂未提供用户账号系统
- 暂未提供数据库
- 暂未提供云端同步
- 暂未提供复杂的设定库管理
- 暂未提供 RAG 长期记忆
- 暂未提供章节审校和自动修订
- API Key 当前以本地 JSON 文件形式保存，未加密
- 小说内容当前以 JSON 文件形式保存在本地

---

## 15. 后续规划

建议后续按以下阶段继续开发：

### 第 6 阶段：正文编辑器增强

- 支持在网页中编辑章节正文
- 支持保存修改后的正文
- 支持章节状态管理
- 支持复制正文

### 第 7 阶段：AI 审校与修订

- 检查人物是否前后矛盾
- 检查时间线是否冲突
- 检查设定是否崩坏
- 检查节奏是否拖沓
- 根据审校意见自动修订

### 第 8 阶段：设定库

- 人物卡
- 地点卡
- 势力卡
- 物品卡
- 能力体系
- 伏笔库

### 第 9 阶段：长期记忆与 RAG

- 章节摘要入库
- 人物状态追踪
- 伏笔追踪
- 历史上下文检索
- 长篇一致性维护

### 第 10 阶段：桌面应用打包

- 打包成 NovelForge.exe
- 用户无需手动安装开发环境
- 打开软件即进入工作台

---

## 16. 当前项目状态

截至目前，NovelForge 已经完成：

```text
第 1 阶段：FastAPI 后端 MVP
第 2 阶段：小说项目管理
第 3 阶段：章节系统
第 4 阶段：React 前端工作台
第 5 阶段：本地用户模式、一键启动、网页配置 API Key
```

当前已经可以作为一个本地 AI 小说创作工作台雏形使用。
