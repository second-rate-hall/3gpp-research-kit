# 3GPP Research Kit

一个面向 3GPP 标准研究的 Agent 工作台，用于把“让 AI 帮我分析标准”变成可复核、可复跑、可沉淀的研究流程。

它不是一个声称内置全部 3GPP 知识的聊天机器人，也不是一个替代 3GPP Portal / FTP / Forge 的资料库。它的定位更朴素，也更实用：给 Codex、Claude CLI、WorkBuddy 等工作环境型 Agent 一套项目目录、研究 workflow、证据表、工具路由和报告模板，让 Agent 能围绕官方资料执行标准研究任务。

## What This Solves

3GPP 标准分析的难点通常不只是“文档太长”，而是答案分散在不同资料层级中：

```text
TS/TR clause
-> CR
-> TDoc
-> Meeting Report
-> Work Item / Release background
```

本项目帮助 Agent 做三件事：

- 找证据：定位 TS/TR、CR、TDoc、Meeting Report、Portal / FTP / Forge 资料。
- 组织证据：用 evidence table 记录来源、版本、条款、状态和待核验项。
- 生成报告：按固定结构输出结论、依据、分析过程、图示和 open verification items。

## Who It Is For

适合：

- 需要分析 3GPP TS/TR、CR、TDoc、Meeting Report 的标准研究人员。
- 希望用 Codex、Claude CLI、WorkBuddy 等 Agent 做可复现研究的工程师。
- 正在搭建 3GPP RAG、GraphRAG、MCP 或本地资料索引的小团队。
- 希望把一次性问答沉淀成研究记录、证据表和报告模板的人。

不适合：

- 只想要一个开箱即用的公网 3GPP 搜索网站。
- 希望模型直接给出无引用标准结论。
- 不准备核验官方来源的高风险标准判断。

## Quick Start

1. 打开本项目根目录。
2. 先跑一个最小闭环，自动下载 TS 38.331、解析、建库并检索：

```bash
python scripts/3gpp_research.py fetch-spec --spec 38.331 --latest
python scripts/3gpp_research.py parse
python scripts/3gpp_research.py build-db
python scripts/3gpp_research.py search "RRCSetup*" --limit 3
```

3. 如果希望直接生成一份证据优先的深度研究报告，可以使用一键入口：

```bash
python scripts/3gpp_research.py research "请分析 RRCSetup 在 RRC re-establishment fallback 场景中的作用" --spec 38.331 --latest
```

报告会保存到 `research-runs/`，并自动执行一次 evidence verification。这个入口偏通用、可解释、可由 Codex 类 Agent 接管；它不会把未检索到 CR、TDoc 或 Meeting Report 的内容写成最终标准结论。

4. 也可以把已有资料放入 `TDoc/_incoming/`，例如 TDoc、CR、Meeting Report、LS、agenda、document list，然后执行：

```bash
python scripts/3gpp_research.py parse
python scripts/3gpp_research.py build-db
```

5. 在 Codex、Claude CLI、WorkBuddy 或其他支持读取本地文件和运行命令的 Agent 中输入：

```text
请先阅读 README.md、skills/3gpp-research-kit/SKILL.md、skills/external-skills.md、workflows/、mcp/、rag/、graphrag/、sources/、scripts/ 和 TDoc/README.md，
并按其中工作流执行以下研究任务：

<粘贴你的 3GPP 研究目标>
```

示例：

```text
请分析 5G UE 开机后的搜网流程，并区分 NAS 层 PLMN selection、AS/RRC 层 cell selection 和后续 RRC establishment。
```

也可以直接复制：

```text
prompts/start-research.md
```

## How It Works

本项目把 Agentic Research 拆成几个可检查的部分：

| 部分 | 作用 |
| --- | --- |
| `skills/` | 固化 3GPP 研究口径、外部 skill 引用和证据约束 |
| `workflows/` | 固定任务模板、证据表、报告模板、自检清单和工具路由 |
| `TDoc/` | 存放用户预下载的 TDoc、CR、Meeting Report 等资料 |
| `mcp/` | 记录 3GPP MCP Server、teddi-mcp 等工具接入方式 |
| `rag/` | 记录 Telco-RAG、Chat3GPP 等 RAG 查询接口和返回格式 |
| `graphrag/` | 记录图谱 schema、关系模板和 GraphRAG 查询方式 |
| `sources/` | 记录 3GPP Portal、FTP、Forge 等官方资料入口 |
| `scripts/` | 提供下载、解析、索引、检索和证据检查的本地 CLI |
| `research-runs/` | 保存每次研究的问题、证据表和报告输出 |
| `example/` | 展示完整研究报告样例 |

推荐执行链路：

```text
Research question
-> classify task
-> route tools
-> retrieve official evidence
-> fill evidence table
-> cross-check
-> write report
-> list open verification items
```

## Tool Routing

Agent 不应只靠模型记忆回答。不同任务应调用不同工具或资料入口：

| 任务 | 优先入口 |
| --- | --- |
| 判断问题涉及哪些规范 | `mcp/3gpp-mcp-server.md`、`sources/3gpp-portal.md` |
| 查询术语官方定义 | `mcp/teddi-mcp.md` |
| 查 clause、procedure、IE 原文 | `rag/`、`TDoc/_index/`、`sources/3gpp-forge.md` |
| 分析 CR 为什么引入 | `sources/3gpp-portal.md`、`TDoc/`、`workflows/evidence-schema.md` |
| 追踪功能演进或公司立场 | `graphrag/`、TDoc 元数据、Meeting Report |
| 批量整理会议材料 | `scripts/`、`TDoc/_incoming/`、`TDoc/_processed/` |

详细规则见：

```text
workflows/tool-routing.md
```

## Local CLI

本项目已经包含一个可执行 CLI：

```text
scripts/3gpp_research.py
```

当前支持：

| 命令 | 作用 |
| --- | --- |
| `fetch --url <url>` | 下载官方 URL 到 `TDoc/_incoming/` |
| `fetch-list --file urls.txt` | 批量下载 URL 列表 |
| `fetch-spec --spec 38.331 --latest` | 从 3GPP Specs archive 下载指定规范 ZIP |
| `parse` | 解析 ZIP / DOCX / TXT / MD / CSV / HTML；PDF 需可选依赖 `pypdf` |
| `build-db` | 建立 SQLite FTS 检索库和基础关系表 |
| `search <query>` | 检索本地证据库 |
| `relations` | 查看基础 GraphRAG-style 关系表 |
| `check-tools` | 检查 `tools.json` 中配置的外部工具是否可用 |
| `run-tool <name>` | 调用 `tools.json` 中配置的外部工具 |
| `verify <file>` | 检查报告中显式 confirmed 但缺少明显来源标记的行 |
| `research <question>` | 一键执行通用深度研究，生成 evidence table 和报告 |

示例：

```bash
python scripts/3gpp_research.py fetch --url https://www.3gpp.org/ftp/tsg_ran/WG2_RL2/TSGR2_104/Docs/R2-1817862.zip
python scripts/3gpp_research.py fetch-list --file urls.txt
python scripts/3gpp_research.py parse
python scripts/3gpp_research.py build-db
python scripts/3gpp_research.py search "fallback RRCSetup" --limit 5
python scripts/3gpp_research.py relations --limit 10
python scripts/3gpp_research.py research "请对比 4G 和 5G RRC re-establishment 流程" --spec 36.331 --spec 38.331
```

外部工具配置：

```bash
cp tools.example.json tools.json
python scripts/3gpp_research.py check-tools
python scripts/3gpp_research.py run-tool teddi search-term QoS --pattern exactmatch
```

生成文件：

```text
TDoc/_processed/         # 转换后的文本或解包结果
TDoc/_index/metadata.csv # 文档元数据
TDoc/_index/research.db  # SQLite FTS 和关系表
```

这些生成文件默认不发布到 GitHub。

## Evidence First

每个关键结论都应尽量回到以下来源：

- TS/TR clause 或官方 specification 页面。
- CR 及其 reason for change。
- TDoc 承载的会议材料。
- Meeting Report。
- 3GPP / ETSI / GSMA 等官方来源。

无法确认的内容必须标注为 `needs_verification` 或“待核验”。第三方解释和模型总结只能作为辅助理解，不能作为最终标准事实。

## Project Layout

```text
3gpp-research-kit/
  README.md
  ROADMAP.md
  PUBLISHING.md
  tools.example.json
  .gitignore
  skills/
    3gpp-research-kit/
      SKILL.md
    external-skills.md
  workflows/
    README.md
    task-template.md
    evidence-schema.md
    report-template.md
    checklist.md
    tool-routing.md
  TDoc/
    README.md
    _incoming/
    _processed/
    _index/
      metadata-template.csv
  mcp/
    README.md
    3gpp-mcp-server.md
    teddi-mcp.md
    config-template.md
  rag/
    README.md
    telco-rag.md
    chat3gpp.md
    query-template.md
  graphrag/
    README.md
    schema.md
    relationship-template.csv
    query-template.md
  sources/
    README.md
    3gpp-portal.md
    3gpp-ftp.md
    3gpp-forge.md
  prompts/
    start-research.md
  scripts/
    README.md
    3gpp_research.py
    convert-documents.md
    build-index.md
  example/
    5G-UE-开机搜网流程分析报告.md
  research-runs/
    README.md
    _template/
      task.md
      evidence.md
      report.md
```

## Example Output

参考：

```text
example/5G-UE-开机搜网流程分析报告.md
```

一个合格报告至少应包含：

- 结论摘要。
- 研究范围与问题拆解。
- 规范依据表。
- Evidence table。
- 分阶段或分主题分析。
- Mermaid 图示，如适用。
- 常见误区和边界澄清。
- 未确认点与后续核验建议。

## Optional Integrations

本项目内置本地 CLI，也可以逐步接入更多外部工具：

- 3GPP MCP Server：规范搜索、规范详情、实现要求。
- teddi-mcp：ETSI / 3GPP 术语核验。
- Telco-RAG / Chat3GPP：规范原文检索和问答。
- GraphRAG / Neo4j / LightRAG：TS、CR、TDoc、会议、公司、Feature 关系追踪。
- 本地脚本：文档转换、TDoc 元数据抽取、CSV/SQLite 索引生成。

外部 skill 说明见：

```text
skills/external-skills.md
```

## Relationship to 3GPP Research Agent

`3gpp-research-kit` 不是 `3gpp-research-agent` 的内部库，而是上游研究工作台和证据底座。它应同时支持三种使用方式：

- 作为独立目录：用户或 Codex 类 Agent 打开本仓库，使用 workflow、模板和 `research` 命令生成报告。
- 作为 Codex skill：让 Agent 读取 `SKILL.md`，按证据优先规则完成研究。
- 作为可调用工具包：被 `3gpp-research-agent` 或其他程序调用，用于 fetch、parse、index、search、relations、verify。

两者分工建议保持清晰：

| 能力 | 3gpp-research-kit | 3gpp-research-agent |
| --- | --- | --- |
| 定位 | 通用研究工作台、skill、证据引擎 | 产品化专用 CLI Agent |
| 一键研究 | 有，偏证据优先、可解释、可人工接管 | 有，偏自动规划、多模型调用和专项报告器 |
| 资料处理 | 定义并实现 fetch / parse / index / search / verify | 优先调用 kit |
| 报告生成 | 模板驱动，保守标注证据状态 | 模型驱动，可做多阶段 writer / verifier |
| 质量约束 | evidence schema、report template、verification | 遵循并复用 kit 的证据约束 |

## Roadmap

本项目的目标是逐步从 executable MVP 发展为本地 3GPP 研究引擎。详细计划见：

```text
ROADMAP.md
```

## Status

当前状态：executable MVP。

已经具备：

- 项目目录约定。
- 3GPP research skill。
- 任务、证据表、报告和自检模板。
- MCP、RAG、GraphRAG、官方资料入口和脚本接口说明。
- 示例报告。
- 可执行 CLI：官方下载、ZIP/DOCX/TXT/HTML 解析、metadata 生成、SQLite FTS 建库、检索和基础证据检查。
- 一键 `research` 命令：自动串联资料获取/复用、解析、建库、检索、报告生成和 evidence verification。
- 外部工具桥接：通过 `tools.json` 调用本地安装的 teddi、Telco-RAG、Chat3GPP 或 MCP wrapper。

发布到 GitHub 前建议补齐：

- `CONTRIBUTING.md`：说明如何提交工具适配、模板和示例。
- `CHANGELOG.md`：记录版本变化。
- 至少一个英文版 README 或双语摘要，如果希望被更广泛使用。
- fake/sample metadata 示例，避免所有 demo 都依赖真实 3GPP 下载资料。
- fresh-agent test，验证新 Agent 只读 README 和 workflow 能否跑通示例任务。

## Disclaimer

本项目帮助组织 3GPP 标准研究流程，但不提供官方标准结论。所有关键判断都应回到 3GPP、ETSI 或其他官方来源核验。
