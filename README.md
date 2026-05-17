# 3GPP Research Kit

`3gpp-research-kit` 是一个证据优先的 3GPP 标准研究工作台，用于结合本地文件、官方来源，以及 Codex、Claude CLI 或类似的工作区 Agent 来开展标准研究。

它不是聊天机器人，也不声称内置了全部 3GPP 知识。它的目标更窄，也更实用：帮助你把一个标准问题转化为一次可复现的研究过程，包含资料清单、证据表、核验状态，以及可回到 3GPP 官方材料检查的研究报告。

## 为什么需要它

3GPP 问题的答案很少只藏在一个段落里。严肃分析通常需要串联：

```text
TS/TR clause
-> CR and reason for change
-> TDoc / contribution
-> Meeting Report
-> Work Item / Release context
```

本仓库为这套工作流提供本地项目结构和 CLI：

- 下载或复用 3GPP 官方文件。
- 本地资料不足时，按内置在线搜索 playbook 和 search recipes 发现官方来源。
- 解析 ZIP / DOCX / TXT / MD / CSV / HTML 文件。
- 在解析 DOCX 时保留 Word 修订痕迹的意图。
- 构建本地 SQLite FTS 证据数据库。
- 检索证据并查看基础关系行。
- 生成保守的深度研究报告。
- 检查 `confirmed` 结论是否带有明确来源标记。

领域规则和报告结构不写死在 Python 代码中：

- `config/research-taxonomy.json` 保存任务分类、候选规范提示、检索扩展、排序规则和 claim 规则。
- `templates/research-report.md` 保存一键研究报告模板。
- `tools/registry.json` 保存 MCP、RAG、GraphRAG、专利背景、本地 CLI 等工具角色。
- `sources/search-recipes.json` 和 `sources/online-search-playbook.md` 保存本地无资料时的在线搜索方法。

## 快速开始

克隆仓库，并在项目根目录运行命令。

```bash
python scripts/3gpp_research.py --help
```

运行一个最小证据闭环：

```bash
python scripts/3gpp_research.py fetch-spec --spec 38.331 --latest
python scripts/3gpp_research.py parse
python scripts/3gpp_research.py build-db
python scripts/3gpp_research.py search "RRCSetup fallback" --limit 5
```

运行一键深度研究：

```bash
python scripts/3gpp_research.py research "请分析 RRCSetup 在 RRC re-establishment fallback 场景中的作用" --spec 38.331 --latest
```

报告会写入 `research-runs/`，随后由内置证据核验器检查。

## 与 Codex 或其他工作区 Agent 配合使用

在你的 Agent 工具中打开本仓库，并要求它遵循项目工作流：

```text
Read README.md, SKILL.md, workflows/, scripts/, sources/, TDoc/README.md,
then perform evidence-grounded 3GPP research for this question:

<your question>
```

Agent 应使用本地 CLI 和模板，而不是直接依赖模型记忆回答。

## 本地资料

把用户提供的标准材料放在这里：

```text
TDoc/_incoming/
```

然后解析并建索引：

```bash
python scripts/3gpp_research.py parse
python scripts/3gpp_research.py build-db
```

生成文件属于本地工作产物，并会被 Git 忽略：

```text
TDoc/_processed/
TDoc/_index/metadata.csv
TDoc/_index/research.db
research-runs/<generated reports>
```

## CLI 命令

| 命令 | 用途 |
| --- | --- |
| `fetch --url <url>` | 将官方 URL 下载到 `TDoc/_incoming/` |
| `fetch-list --file urls.txt` | 下载 URL 列表中的文件 |
| `fetch-spec --spec 38.331 --latest` | 从 3GPP Specs archive 下载 ZIP |
| `parse` | 将 incoming 文件解析为 Markdown/text 产物 |
| `build-db` | 构建 SQLite FTS 和关系表 |
| `search <query>` | 检索本地证据数据库 |
| `relations` | 显示基础 GraphRAG 风格关系行 |
| `check-tools` | 检查 `tools.json` 中配置的外部工具 |
| `run-tool <name>` | 运行 `tools.json` 中配置的外部工具 |
| `verify <file>` | 检查报告中未落地到证据的 `confirmed` 结论 |
| `research <question>` | 运行通用的证据优先研究工作流 |

## 项目结构

```text
3gpp-research-kit/
  README.md
  SKILL.md
  config/           # 任务分类、规范提示、检索扩展、排序和 claim 规则
  templates/        # 报告模板
  tools/            # 工具注册表和角色定义
  workflows/        # 任务、证据、报告、检查清单、工具路由模板
  scripts/          # 本地 CLI 和解析器
  sources/          # 3GPP / FTP / Forge 官方来源说明
  mcp/              # MCP 接入说明和示例
  rag/              # RAG 接入说明
  graphrag/         # 图谱 schema、关系模板、知识图谱说明
  TDoc/             # 本地源材料工作区
  research-runs/    # 报告模板和生成的研究过程
  example/          # 示例研究报告
```

## 证据规则

只要条件允许，优先使用以下材料作为最终证据来源：

- 官方 TS/TR clause 或 specification archive。
- CR 及其 reason for change。
- TDoc 承载的会议材料。
- Meeting Report。
- 3GPP / ETSI / GSMA 官方来源。

如果证据不完整，应将结论标记为 `needs_verification`。第三方网页、专利和模型输出可以用于引导调查，但不能作为最终标准证据。

## 与 3GPP Research Agent 的关系

`3gpp-research-kit` 是可复用的工作台和证据层。

`3gpp-research-agent` 是一个独立的专用 CLI Agent，可以构建在这个证据层之上，同时增加更强的规划、模型调用、专项报告生成和运行管理能力。

这个 kit 本身应保持可独立使用：人类研究者或工作区 Agent 克隆本仓库后，即使不安装专用 Agent，也能生成研究报告。

## 当前状态

可执行 MVP。

已实现：

- 本地项目工作流和模板。
- 研究状态机、工具编排规则、工具注册表和在线搜索方法。
- 3GPP research skill 指令。
- 官方来源说明和工具路由规则。
- 用于下载、解析、建索引、检索、关系查看、核验和一键研究的 CLI。
- CLI 从 `config/research-taxonomy.json` 和 `templates/research-report.md` 加载领域规则与报告模板，避免把 3GPP 术语和文档结构硬编码在 Python 中。
- 感知 DOCX 修订痕迹的解析。
- 通过 `tools.json` 连接外部工具。
- 示例报告和报告模板。

尚未完成：

- 面向完整 CR / TDoc / Meeting Report 门户规模的自动化。
- 能为每个 chunk 提供精确 clause pointer 的 clause-aware parser。
- 生产级 GraphRAG 数据库集成。
- 打包后的 Python API；当前稳定接口是 CLI。

## 免责声明

本项目用于辅助组织 3GPP 标准研究，不提供官方标准结论。重要结论必须始终回到 3GPP、ETSI 或其他权威来源核验。
