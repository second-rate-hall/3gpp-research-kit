# Research System

`3gpp-research-kit` 是给 Codex、Claude CLI 等工作环境型 Agent 使用的 3GPP 深度研究系统。它不是单个脚本，而是一套从研究目标到证据报告的状态机。

## 状态机

| 阶段 | 名称 | 主要输入 | 主要工具 | 主要输出 |
| --- | --- | --- | --- | --- |
| S0 | Intake | 用户研究目标 | `workflows/task-template.md` | 标准化任务说明 |
| S1 | Planning | 任务说明 | `config/research-taxonomy.json`、LLM | 任务类型、候选规范、证据需求 |
| S2 | Tool Routing | 研究计划 | `tools/registry.json`、`workflows/tool-orchestration.md` | 工具调用计划 |
| S3 | Source Discovery | 资料缺口 | MCP、Portal、FTP、Forge、`sources/search-recipes.json` | 候选来源清单 |
| S4 | Acquisition | 候选来源 | `scripts/3gpp_research.py fetch/fetch-spec/fetch-list` | 本地原始资料 |
| S5 | Parsing | ZIP/DOCX/PDF/HTML | `parse`、`docx_track_changes_parser.py` | Markdown/text、metadata |
| S6 | Indexing | parsed texts | `build-db` | SQLite FTS、relations |
| S7 | Retrieval | question/spec/task | local FTS、RAG、MCP、GraphRAG | evidence rows |
| S8 | Verification | evidence rows | `verify`、checklist | open verification items |
| S9 | Reporting | evidence package | `templates/research-report.md` | 完整研究报告 |

## 原则

- Python 代码只负责执行状态机，不承载 3GPP 领域知识或报告模板。
- 3GPP 术语、候选规范提示、检索扩展、排序权重放在 `config/research-taxonomy.json`。
- 报告结构放在 `templates/research-report.md`。
- 工具能力放在 `tools/registry.json`。
- 在线搜索方法放在 `sources/search-recipes.json` 和 `sources/online-search-playbook.md`。

## 最小闭环

```powershell
python scripts\3gpp_research.py research "请分析 RRCSetup 在 RRC re-establishment fallback 场景中的作用" --spec 38.331 --latest
```

该命令至少应产出：

- 下载或复用的资料
- 解析后的本地文本
- SQLite FTS 证据库
- evidence table
- 可复核研究报告
- verify 结果
