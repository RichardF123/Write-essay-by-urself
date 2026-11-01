# Write essay by urself

**上传自己的写作样本、论文和作业要求，让 agent 先理解你怎样写、怎样想，再逐段细改。**

**Upload your writing samples, essay and assignment requirements. Let your agent learn how you write and reason, then refine the draft paragraph by paragraph.**

这套 skill 来自一次完整的论文修订实践。它研究作者如何观察、解释、比较和判断，把这些习惯落实到每段表达，同时保留论据、引用和评分要求。多轮检测报告用于追踪高亮变化，帮助找到值得继续检查的局部。

This skill grew out of a full essay revision process. It studies how the author observes, explains, compares and reaches a judgment, then applies those habits to each paragraph while preserving evidence, citations and assignment requirements. Reports from several rounds help track highlighted passages and identify areas for further review.

## 上传即可开始 / Upload and start

安装后，把手头资料上传到支持附件的 agent，发送下面一句即可。终端 agent 可以读取你放进工作目录的文件。文件分类、文字提取、版本匹配、文风分析、逐段诊断、修订记录和评分核查都交给 agent 完成。

After installation, attach your materials in an agent that supports uploads and send the request below. A terminal agent can read files placed in its working folder. The agent handles file classification, text extraction, version matching, voice analysis, paragraph review, revision records and rubric checks.

```text
用 essay-in-your-voice 处理我上传的资料：先分析我的写作习惯，
结合评分标准和多轮报告逐段检查，再按我的语言逻辑微调。
未高亮且表达自然的部分尽量保留，最后给我修订稿和简短说明。
```

```text
Use essay-in-your-voice with my uploaded materials. Study my writing habits,
review each paragraph against the rubric and available reports, then make
small edits in my voice. Preserve natural, unhighlighted passages where possible.
Return the revised draft and a short explanation of the changes.
```

用户上传现有文件就可以开始。agent 自动生成材料清单和版本记录；存在多个候选稿时，结合报告正文、日期和文字差异识别修改基底。遇到影响结果的缺项或冲突，再集中问一个简短问题。

Users can start with the files they already have. The agent creates the material inventory and version records. When several drafts are present, it uses report text, dates and textual differences to identify the revision base. It asks a concise, bundled question when a missing item or conflict materially affects the result.

## 上传哪些资料 / What to upload

先上传自己的写作样本、当前论文和作业要求。有检测报告、旧版本、参考文献或图片，也可以一起上传。保持原文件名和原有格式即可，材料说明由 agent 整理。

Start with your own writing samples, current essay and assignment requirements. Add reports, earlier drafts, references or images when available. Keep the original filenames and formats; the agent organizes the material descriptions.

| 资料 | 用途 |
| --- | --- |
| 自己的写作样本，建议 3–5 份 | 提取常用词、句式、解释方式与推理习惯；同语言、同文体的样本优先。 |
| 当前论文 | 确定逐段修订的基底，保留原稿副本。 |
| 作业题目、评分规则和提交模板 | 检查论点、分析、字数、来源、引注、图片与格式。 |
| 多轮 AI 检测报告 | 定位反复高亮、解除高亮和新增高亮的片段。 |
| 每轮送检稿、旧版本或修改记录 | 匹配报告与原文，比较文字变化和高亮变化。 |
| 引用文献、页码、原图或图像出处 | 核查事实、学者观点、图文对应与推断范围。 |
| 你认为自然或别扭的例子 | 校准 agent 对个人风格的理解。 |

| Material | Purpose |
| --- | --- |
| Your writing samples; 3–5 pieces are a useful starting point | Identify vocabulary, sentence patterns, explanations and reasoning habits. Prioritize the target language and genre. |
| Current essay | Establish the revision base and preserve the original. |
| Assignment brief, rubric and submission template | Check the argument, analysis, length, sources, citations, images and format. |
| AI reports from several rounds | Locate recurring, cleared and newly highlighted passages. |
| Submitted drafts, older versions or change records | Match reports to their text and compare edits with highlight changes. |
| References, page numbers, original images or image sources | Verify facts, scholarly views, visual evidence and the scope of interpretations. |
| Passages that feel natural or awkward to you | Calibrate the agent’s understanding of your voice. |

直接上传 PDF、DOCX、TXT、Markdown 或笔记本等宿主支持的格式。agent 使用可用的文件工具提取正文，区分本人论述、题干、引用、代码与输出。跨文体样本用于理解推理习惯，同文体样本用于细化表达。

Upload PDFs, DOCX files, text, Markdown, notebooks or other formats supported by your host. The agent uses available file tools to extract prose and distinguish your writing from prompts, quotations, code and outputs. It uses cross-genre samples to understand reasoning and closer genre matches to refine expression.

## 安装本 skill / Install this skill

以下命令把 `essay-in-your-voice` 安装到你选择的 agent。先准备 [Node.js](https://nodejs.org/en/download) 和 [Git](https://git-scm.com/downloads)；按当前 [Skills CLI 文档](https://github.com/vercel-labs/skills)，Node.js 使用 22.20 或更新版本。`--global` 表示跨项目使用，删去它即可安装到当前项目。

The commands below install `essay-in-your-voice` for your chosen agent. Set up [Node.js](https://nodejs.org/en/download) and [Git](https://git-scm.com/downloads) first. The current [Skills CLI documentation](https://github.com/vercel-labs/skills) requires Node.js 22.20 or later. `--global` makes the skill available across projects; omit it for a project installation.

运行 `node --version` 确认当前终端使用的版本。更新 Node.js 后重新打开终端，让 `npx` 使用新版本。

Run `node --version` to check the version used by your current terminal. After updating Node.js, reopen the terminal so `npx` uses the new version.

### Codex

在 PowerShell、macOS 或 Linux 终端运行：

Run in PowerShell, a macOS terminal or a Linux terminal:

```sh
npx skills add RichardF123/Write-essay-by-urself --skill essay-in-your-voice --agent codex --global
```

### Claude Code

```sh
npx skills add RichardF123/Write-essay-by-urself --skill essay-in-your-voice --agent claude-code --global
```

### Cursor

```sh
npx skills add RichardF123/Write-essay-by-urself --skill essay-in-your-voice --agent cursor --global
```

### Gemini CLI

```sh
npx skills add RichardF123/Write-essay-by-urself --skill essay-in-your-voice --agent gemini-cli --global
```

### GitHub Copilot

```sh
npx skills add RichardF123/Write-essay-by-urself --skill essay-in-your-voice --agent github-copilot --global
```

### Windsurf

```sh
npx skills add RichardF123/Write-essay-by-urself --skill essay-in-your-voice --agent windsurf --global
```

### OpenCode

```sh
npx skills add RichardF123/Write-essay-by-urself --skill essay-in-your-voice --agent opencode --global
```

选择你正在使用的工具运行对应命令即可。安装器会显示目标路径；Windows 如需使用文件复制，可以在命令末尾加 `--copy`。安装后开启新会话，上传资料，再发送开始指令。支持技能选择器的宿主也可直接选择 `essay-in-your-voice`。

Run the command for the tool you use. The installer shows the destination; append `--copy` to use file copies on Windows when helpful. Start a new session after installation, upload your materials and send the starter request. Hosts with a skill selector can also select `essay-in-your-voice` directly.

### 查看与更新 / Inspect and update

查看仓库中的 skill、检查 Codex 的全局安装、获取更新：

List the repository’s skills, inspect the global Codex installation and update this skill:

```sh
npx skills add RichardF123/Write-essay-by-urself --list
npx skills list --global --agent codex
npx skills update essay-in-your-voice
```

### 手动下载 / Manual download

也可以下载仓库，再把 `skills/essay-in-your-voice` 整个文件夹复制到宿主的技能目录。Codex 当前的个人目录是 `~/.agents/skills/`，Claude Code 是 `~/.claude/skills/`。完整路径和 agent 标识见 [Skills CLI 支持列表](https://github.com/vercel-labs/skills/blob/main/docs/agents.md)及 [Codex 官方技能文档](https://developers.openai.com/codex/skills)。

You can also download the repository and copy the entire `skills/essay-in-your-voice` folder into your host’s skill directory. The current personal directory is `~/.agents/skills/` for Codex and `~/.claude/skills/` for Claude Code. See the [Skills CLI agent list](https://github.com/vercel-labs/skills/blob/main/docs/agents.md) and [official Codex skills documentation](https://developers.openai.com/codex/skills) for paths and agent identifiers.

```sh
git clone https://github.com/RichardF123/Write-essay-by-urself.git
```

[下载 ZIP / Download ZIP](https://github.com/RichardF123/Write-essay-by-urself/archive/refs/heads/main.zip)

## 安装 agent 工具 / Install an agent tool

已经有 agent 的用户可以直接使用上一节。刚开始使用的用户，可选择下面一种工具安装，按该工具提示完成登录，再安装本 skill。

If you already use an agent, follow the previous section. If you are starting fresh, choose a tool below, complete its sign-in flow and then install this skill.

**Codex CLI**：使用 npm 安装，运行 `codex` 启动。[官方安装文档](https://developers.openai.com/codex/cli)。

**Codex CLI**: Install with npm and run `codex` to start. See the [official installation guide](https://developers.openai.com/codex/cli).

```sh
npm install -g @openai/codex
codex
```

**Claude Code**：Windows PowerShell 使用下面第一段，macOS/Linux 使用第二段。[官方安装文档](https://code.claude.com/docs/en/setup)。

**Claude Code**: Use the first block in Windows PowerShell or the second on macOS/Linux. See the [official installation guide](https://code.claude.com/docs/en/setup).

```powershell
irm https://claude.ai/install.ps1 | iex
claude
```

```sh
curl -fsSL https://claude.ai/install.sh | bash
claude
```

**Gemini CLI**：安装后运行 `gemini`。[官方安装文档](https://geminicli.com/docs/get-started/installation/)。

**Gemini CLI**: Run `gemini` after installation. See the [official installation guide](https://geminicli.com/docs/get-started/installation/).

```sh
npm install -g @google/gemini-cli
gemini
```

**OpenCode**：以下为官方文档中的 OpenCode 1 npm 安装方式，运行 `opencode` 启动。[安装与版本说明](https://opencode.ai/docs/)。

**OpenCode**: The following npm command installs OpenCode 1 as documented upstream. Run `opencode` to start. See the [installation and version notes](https://opencode.ai/docs/).

```sh
npm install -g opencode-ai
opencode
```

**编辑器用户**：可从 [Cursor](https://cursor.com/downloads)、[Windsurf](https://windsurf.com/download) 或 [GitHub Copilot 设置指南](https://docs.github.com/en/copilot/quickstart)完成工具安装，再运行对应的 skill 安装命令。

**Editor users**: Set up your tool through [Cursor](https://cursor.com/downloads), [Windsurf](https://windsurf.com/download) or the [GitHub Copilot setup guide](https://docs.github.com/en/copilot/quickstart), then run the matching skill installation command.

## 自动完成的流程 / What the agent handles

**材料整理与文风研究。** agent 识别上传文件的用途，建立版本清单，再从原始样本研究用词、句法、段落推进、比较条件、证据使用与判断习惯。每项风格结论保留出处和适用范围。

**Material organization and voice research.** The agent identifies each file’s role, builds a version inventory and studies vocabulary, syntax, paragraph movement, comparison conditions, evidence use and judgment in original samples. Each finding retains its source and scope.

**多轮报告与逐段诊断。** agent 将报告匹配到实际送检文本，记录高亮变化，再逐段检查分析方法、图文关系、句式与个人风格。它也会检查未高亮段落的论据和逻辑。

**Report comparison and paragraph diagnosis.** The agent matches reports to submitted text, tracks highlight changes and reviews each paragraph’s analysis, visual evidence, sentence structure and personal voice. It also checks evidence and logic in unhighlighted passages.

**局部修订与评分复核。** agent 以确定的基底稿微调，保留自然表达，记录必要修改，再核查评分项、引用、字数、图片与格式。Word/PDF 交付时使用宿主的文档工具检查版面。

**Local revision and rubric review.** The agent makes small edits to the selected base draft, preserves natural wording, records necessary changes and checks the rubric, citations, length, images and formatting. For Word/PDF delivery, it uses the host’s document tools to review the layout.

最终提供修订稿和简短说明，详细依据保存在任务目录中的 `voice-profile.md`、`report-ledger.md`、`highlight-patterns.md`、`paragraph-audit.md`、`revision-log.md` 和 `rubric-check.md`。用户可以直接阅读结果，也可以继续追问任一段的修改理由。

The result is a revised draft and a short explanation. Detailed evidence stays in the task folder as `voice-profile.md`, `report-ledger.md`, `highlight-patterns.md`, `paragraph-audit.md`, `revision-log.md` and `rubric-check.md`. Users can read the finished draft or ask why any paragraph was changed.

## 从多轮高亮中学什么 / What repeated highlights reveal

反复高亮片段值得检查的共同问题包括：方法宣布多而应用少、观察后重复概括、`this shows` 指代模糊、段段采用对称对比、结论逐项清点而回答不足。agent 将这些现象与作者样本、图像和来源一起检查，决定是否值得修改。

Recurring highlighted passages can share issues such as announcing a method without applying it, restating observations, vague references like `this shows`, repeated balanced contrasts or conclusions that list findings without fully answering the question. The agent checks these features against the author’s samples, images and sources before recommending an edit.

同样保留反例：改过仍高亮、未改却新增高亮，以及短小普通句被高亮。文字质量改善和报告状态变化分别记录，帮助后续保留真正有价值的修改。详细方法见[报告对照协议](skills/essay-in-your-voice/references/report-comparison.md)和[候选问题与反例](skills/essay-in-your-voice/references/highlight-patterns.md)。

Counterexamples stay in the analysis: revised text that remains highlighted, unchanged text that becomes highlighted and short ordinary sentences that receive highlights. Writing improvements and report-state changes are recorded separately so later revisions retain useful edits. See the [report comparison protocol](skills/essay-in-your-voice/references/report-comparison.md) and [candidate patterns and counterexamples](skills/essay-in-your-voice/references/highlight-patterns.md).

## 可选文风能力集成 / Optional voice integrations

核心分析随本 skill 提供。已有文风工具时，agent 可以复用其可核查结果，再补充论文推理与评分检查。具体输入、输出与适用范围见[集成协议](skills/essay-in-your-voice/references/integrations.md)。

The core analysis ships with this skill. When a voice tool is already available, the agent can reuse its traceable findings and add academic reasoning and rubric checks. See the [integration protocol](skills/essay-in-your-voice/references/integrations.md) for inputs, outputs and scope.

| 工具 | 适合提供的能力 |
| --- | --- |
| [voice-builder](https://github.com/social-media-skills/skills/blob/main/skills/voice-builder/SKILL.md) | 从真实样本提取文风指南；导入后按学术语境校准。 |
| [voice-analyzer](https://github.com/lhh666-6/codex-skills/blob/main/skills/voice-analyzer/SKILL.md) | 复用已有 `VOICE.md`，结合原样本检验。 |
| [humanizer](https://github.com/blader/humanizer) | 局部套话与机械表达复查，按作者习惯取舍。 |
| 宿主已有的个人写作检索 | 获取用户授权的写作参考，遵循来源访问规则。 |

| Tool | Useful contribution |
| --- | --- |
| [voice-builder](https://github.com/social-media-skills/skills/blob/main/skills/voice-builder/SKILL.md) | Extract a voice guide from real samples, then calibrate it for academic use. |
| [voice-analyzer](https://github.com/lhh666-6/codex-skills/blob/main/skills/voice-analyzer/SKILL.md) | Reuse an existing `VOICE.md` and verify it against original samples. |
| [humanizer](https://github.com/blader/humanizer) | Review local formulaic expressions and evaluate edits against the author’s habits. |
| Personal-writing retrieval supplied by the host | Obtain authorized writing references under the provider’s access rules. |

## 开发与本地资料 / Development and local materials

用户上传文件由 agent 在本地任务目录处理。仓库中的 `.gitignore` 已覆盖 `inputs/`、`outputs/`、`private/` 等工作目录，公开内容以通用流程和工具为主。样本文字、报告编号、姓名学号及详细文风档案保留在私人任务中。

The agent handles uploaded files in the local task workspace. The repository’s `.gitignore` covers working folders such as `inputs/`, `outputs/` and `private/`. Public content focuses on the reusable workflow and tools; writing samples, report identifiers, student details and detailed voice profiles stay in private tasks.

开发者可用下面的辅助工具比较两个 UTF-8 TXT/Markdown 版本，得到文件哈希和段落文字差异。agent 可自行运行这个工具；一般用户只需提供文件。PDF 高亮另由 agent 视觉核查并记录页码。

Developers can use the helper below to compare two UTF-8 TXT/Markdown versions and obtain file hashes and paragraph differences. The agent can run it as needed; ordinary users supply the files. The agent separately checks PDF highlights visually and records page references.

```sh
python scripts/compare_versions.py --before inputs/v1.txt --after inputs/v2.txt --output outputs/version-diff.json
```

安装命令与资料链接核查日期：2026-11-01。skill 安装器参数依据 [Skills CLI 命令文档](https://github.com/vercel-labs/skills/blob/main/docs/commands.md)，各 agent 的安装方式依据上文链接的官方说明。

Installation commands and source links checked on 2026-11-01. Skill installer options follow the [Skills CLI command reference](https://github.com/vercel-labs/skills/blob/main/docs/commands.md); agent installation methods follow the official guides linked above.
