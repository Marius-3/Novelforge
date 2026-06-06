import { useEffect, useMemo, useState } from 'react';
import {
  createBookPlan,
  createCatalog,
  createDraft,
  createOutline,
  getDraft,
  getOutline,
  getProject,
  listChapters,
  listProjects
} from './api';
import type {
  BookPlan,
  ChapterCatalogItem,
  ChapterDraftResponse,
  ChapterOutlineResponse,
  ProjectDetailResponse,
  ProjectSummary
} from './types';

function toPrettyJson(value: unknown): string {
  return JSON.stringify(value, null, 2);
}

function SectionTitle(props: { title: string; description?: string }) {
  return (
    <div className="section-title">
      <h2>{props.title}</h2>
      {props.description ? <p>{props.description}</p> : null}
    </div>
  );
}

function BookPlanView({ plan }: { plan: BookPlan }) {
  return (
    <div className="book-plan">
      <div className="card">
        <h3>书名候选</h3>
        <ul>{plan.title_candidates.map((title) => <li key={title}>{title}</li>)}</ul>
      </div>
      <div className="card">
        <h3>核心卖点</h3>
        <p>{plan.core_hook}</p>
      </div>
      <div className="card two-column">
        <div>
          <h3>世界观</h3>
          <p>{plan.world_setting}</p>
        </div>
        <div>
          <h3>金手指</h3>
          <p>{plan.golden_finger}</p>
        </div>
      </div>
      <div className="card two-column">
        <div>
          <h3>主角</h3>
          <p><b>{plan.protagonist.name}</b>：{plan.protagonist.identity}</p>
          <p>动机：{plan.protagonist.motivation}</p>
          <p>冲突：{plan.protagonist.conflict}</p>
        </div>
        <div>
          <h3>主要反派</h3>
          <p><b>{plan.main_antagonist.name}</b>：{plan.main_antagonist.identity}</p>
          <p>动机：{plan.main_antagonist.motivation}</p>
          <p>冲突：{plan.main_antagonist.conflict}</p>
        </div>
      </div>
      <div className="card">
        <h3>前三章</h3>
        <ol>{plan.first_three_chapters.map((item) => <li key={item}>{item}</li>)}</ol>
      </div>
    </div>
  );
}

function ProjectCreator({ onCreated }: { onCreated: (projectId: string) => void }) {
  const [premise, setPremise] = useState('体弱药铺帮工秦照穿越到修仙世界，没有练武天赋，但拥有天衍系统，想用现代医学在异世立足。');
  const [genre, setGenre] = useState('修仙 / 医道 / 智斗');
  const [style, setStyle] = useState('网文爽文，节奏紧凑，主角靠知识破局');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleCreate() {
    setError('');
    setLoading(true);
    try {
      const result = await createBookPlan({ premise, genre, style });
      onCreated(result.project_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : '创建失败');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="panel">
      <SectionTitle title="新建小说项目" description="输入一句灵感，生成书级方案并保存为一个项目。" />
      <label>小说创意</label>
      <textarea value={premise} onChange={(e) => setPremise(e.target.value)} rows={5} />
      <label>类型</label>
      <input value={genre} onChange={(e) => setGenre(e.target.value)} />
      <label>风格</label>
      <input value={style} onChange={(e) => setStyle(e.target.value)} />
      <button onClick={handleCreate} disabled={loading || premise.trim().length < 5}>
        {loading ? '生成中...' : '生成书级方案'}
      </button>
      {error ? <div className="error">{error}</div> : null}
    </div>
  );
}

function ProjectList({
  projects,
  selectedProjectId,
  onRefresh,
  onSelect
}: {
  projects: ProjectSummary[];
  selectedProjectId: string;
  onRefresh: () => void;
  onSelect: (projectId: string) => void;
}) {
  return (
    <div className="sidebar-section">
      <div className="sidebar-header">
        <h2>项目</h2>
        <button className="small-button" onClick={onRefresh}>刷新</button>
      </div>
      <div className="project-list">
        {projects.length === 0 ? <p className="muted">暂无项目。先创建一个书级方案。</p> : null}
        {projects.map((project) => (
          <button
            key={project.project_id}
            className={project.project_id === selectedProjectId ? 'project-item active' : 'project-item'}
            onClick={() => onSelect(project.project_id)}
          >
            <strong>{project.title}</strong>
            <span>{project.genre}</span>
            <small>{project.updated_at}</small>
          </button>
        ))}
      </div>
    </div>
  );
}

function CatalogPanel({ projectId, onCatalogChanged }: { projectId: string; onCatalogChanged: () => void }) {
  const [totalChapters, setTotalChapters] = useState(10);
  const [extraRequirements, setExtraRequirements] = useState('前三章要强钩子，突出秦照体弱、药铺帮工、天衍系统和瞎眼乞丐的疫病威胁。');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  async function handleCreateCatalog() {
    setMessage('');
    setLoading(true);
    try {
      await createCatalog(projectId, {
        volume_index: 1,
        total_chapters: totalChapters,
        extra_requirements: extraRequirements
      });
      setMessage('章节目录已生成。');
      onCatalogChanged();
    } catch (err) {
      setMessage(err instanceof Error ? err.message : '生成失败');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card">
      <h3>章节目录生成</h3>
      <label>本卷章节数</label>
      <input type="number" min={1} max={100} value={totalChapters} onChange={(e) => setTotalChapters(Number(e.target.value))} />
      <label>额外要求</label>
      <textarea rows={4} value={extraRequirements} onChange={(e) => setExtraRequirements(e.target.value)} />
      <button onClick={handleCreateCatalog} disabled={loading}>{loading ? '生成中...' : '生成章节目录'}</button>
      {message ? <p className="muted">{message}</p> : null}
    </div>
  );
}

function ChapterPanel({ projectId, chapters, onRefresh }: {
  projectId: string;
  chapters: ChapterCatalogItem[];
  onRefresh: () => void;
}) {
  const [selectedChapterNo, setSelectedChapterNo] = useState<number>(1);
  const [outlineReq, setOutlineReq] = useState('第一章重点写秦照在药铺中的弱势处境，不要过早暴露全部金手指。结尾让瞎眼乞丐注意到秦照。');
  const [draftReq, setDraftReq] = useState('正文要有场景感、人物对话和紧迫感。不要写成设定说明。');
  const [targetWords, setTargetWords] = useState(1500);
  const [outline, setOutline] = useState<ChapterOutlineResponse | null>(null);
  const [draft, setDraft] = useState<ChapterDraftResponse | null>(null);
  const [message, setMessage] = useState('');
  const [loadingAction, setLoadingAction] = useState('');

  const selectedChapter = useMemo(
    () => chapters.find((item) => item.chapter_no === selectedChapterNo),
    [chapters, selectedChapterNo]
  );

  useEffect(() => {
    if (chapters.length > 0 && !chapters.some((item) => item.chapter_no === selectedChapterNo)) {
      setSelectedChapterNo(chapters[0].chapter_no);
    }
  }, [chapters, selectedChapterNo]);

  async function handleCreateOutline() {
    setMessage('');
    setLoadingAction('outline');
    try {
      const result = await createOutline(projectId, {
        chapter_no: selectedChapterNo,
        extra_requirements: outlineReq
      });
      setOutline(result);
      await onRefresh();
      setMessage('章节大纲已生成。');
    } catch (err) {
      setMessage(err instanceof Error ? err.message : '生成失败');
    } finally {
      setLoadingAction('');
    }
  }

  async function handleLoadOutline() {
    setMessage('');
    setLoadingAction('loadOutline');
    try {
      setOutline(await getOutline(projectId, selectedChapterNo));
    } catch (err) {
      setMessage(err instanceof Error ? err.message : '读取失败');
    } finally {
      setLoadingAction('');
    }
  }

  async function handleCreateDraft() {
    setMessage('');
    setLoadingAction('draft');
    try {
      const result = await createDraft(projectId, {
        chapter_no: selectedChapterNo,
        target_words: targetWords,
        extra_requirements: draftReq
      });
      setDraft(result);
      await onRefresh();
      setMessage('章节正文已生成。');
    } catch (err) {
      setMessage(err instanceof Error ? err.message : '生成失败');
    } finally {
      setLoadingAction('');
    }
  }

  async function handleLoadDraft() {
    setMessage('');
    setLoadingAction('loadDraft');
    try {
      setDraft(await getDraft(projectId, selectedChapterNo));
    } catch (err) {
      setMessage(err instanceof Error ? err.message : '读取失败');
    } finally {
      setLoadingAction('');
    }
  }

  if (chapters.length === 0) {
    return <p className="muted">还没有章节目录。请先生成章节目录。</p>;
  }

  return (
    <div className="chapter-workspace">
      <div className="chapter-list card">
        <h3>章节列表</h3>
        {chapters.map((chapter) => (
          <button
            key={chapter.chapter_no}
            className={chapter.chapter_no === selectedChapterNo ? 'chapter-item active' : 'chapter-item'}
            onClick={() => {
              setSelectedChapterNo(chapter.chapter_no);
              setOutline(null);
              setDraft(null);
              setMessage('');
            }}
          >
            <strong>第 {chapter.chapter_no} 章：{chapter.title}</strong>
            <span>{chapter.summary}</span>
            <small>{chapter.has_outline ? '有大纲' : '无大纲'} / {chapter.has_draft ? '有正文' : '无正文'}</small>
          </button>
        ))}
      </div>

      <div className="chapter-editor">
        <div className="card">
          <h3>当前章节</h3>
          <p><b>第 {selectedChapterNo} 章：</b>{selectedChapter?.title}</p>
          <p>{selectedChapter?.summary}</p>
          {message ? <p className="muted">{message}</p> : null}
        </div>

        <div className="card">
          <h3>生成 / 读取大纲</h3>
          <label>大纲要求</label>
          <textarea rows={4} value={outlineReq} onChange={(e) => setOutlineReq(e.target.value)} />
          <div className="button-row">
            <button onClick={handleCreateOutline} disabled={Boolean(loadingAction)}>{loadingAction === 'outline' ? '生成中...' : '生成大纲'}</button>
            <button className="secondary" onClick={handleLoadOutline} disabled={Boolean(loadingAction)}>{loadingAction === 'loadOutline' ? '读取中...' : '读取大纲'}</button>
          </div>
          {outline ? <pre>{toPrettyJson(outline.outline)}</pre> : null}
        </div>

        <div className="card">
          <h3>生成 / 读取正文</h3>
          <label>目标字数</label>
          <input type="number" min={500} max={10000} value={targetWords} onChange={(e) => setTargetWords(Number(e.target.value))} />
          <label>正文要求</label>
          <textarea rows={4} value={draftReq} onChange={(e) => setDraftReq(e.target.value)} />
          <div className="button-row">
            <button onClick={handleCreateDraft} disabled={Boolean(loadingAction)}>{loadingAction === 'draft' ? '生成中...' : '生成正文'}</button>
            <button className="secondary" onClick={handleLoadDraft} disabled={Boolean(loadingAction)}>{loadingAction === 'loadDraft' ? '读取中...' : '读取正文'}</button>
          </div>
          {draft ? <article className="draft-text">{draft.draft}</article> : null}
        </div>
      </div>
    </div>
  );
}

function Workspace({ projectId }: { projectId: string }) {
  const [project, setProject] = useState<ProjectDetailResponse | null>(null);
  const [chapters, setChapters] = useState<ChapterCatalogItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function refreshProject() {
    if (!projectId) return;
    setError('');
    setLoading(true);
    try {
      const [projectResult, chaptersResult] = await Promise.all([
        getProject(projectId),
        listChapters(projectId).catch(() => [])
      ]);
      setProject(projectResult);
      setChapters(chaptersResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载项目失败');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void refreshProject();
  }, [projectId]);

  if (loading && !project) {
    return <div className="panel"><p>加载中...</p></div>;
  }

  if (error) {
    return <div className="panel"><div className="error">{error}</div></div>;
  }

  if (!project) {
    return <div className="panel"><p className="muted">请选择一个项目。</p></div>;
  }

  return (
    <div className="workspace">
      <SectionTitle title={project.plan.title_candidates[0] ?? '未命名小说'} description={project.plan.core_hook} />
      <BookPlanView plan={project.plan} />
      <CatalogPanel projectId={project.project_id} onCatalogChanged={refreshProject} />
      <ChapterPanel projectId={project.project_id} chapters={chapters} onRefresh={refreshProject} />
    </div>
  );
}

export default function App() {
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState('');
  const [globalError, setGlobalError] = useState('');

  async function refreshProjects() {
    setGlobalError('');
    try {
      const result = await listProjects();
      setProjects(result);
      if (!selectedProjectId && result.length > 0) {
        setSelectedProjectId(result[0].project_id);
      }
    } catch (err) {
      setGlobalError(err instanceof Error ? err.message : '项目列表加载失败');
    }
  }

  useEffect(() => {
    void refreshProjects();
  }, []);

  async function handleCreated(projectId: string) {
    await refreshProjects();
    setSelectedProjectId(projectId);
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <h1>NovelForge</h1>
          <p>AI 小说创作工作台</p>
        </div>
        <ProjectList
          projects={projects}
          selectedProjectId={selectedProjectId}
          onRefresh={refreshProjects}
          onSelect={setSelectedProjectId}
        />
      </aside>

      <main className="main">
        {globalError ? <div className="error">{globalError}</div> : null}
        <ProjectCreator onCreated={handleCreated} />
        {selectedProjectId ? <Workspace projectId={selectedProjectId} /> : <div className="panel"><p className="muted">创建或选择一个项目后开始写作。</p></div>}
      </main>
    </div>
  );
}
