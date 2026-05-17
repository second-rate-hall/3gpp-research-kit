# Tool Routing

本文件规定现成工作环境型 Agent 在不同 3GPP 研究任务下应优先调用哪些项目资产和工具。

工具能力的机器可读注册表见 `tools/registry.json`。本文件负责说明任务到工具的路由原则，`workflows/tool-orchestration.md` 负责说明完整编排链路。

| 任务 | 优先工具 / 目录 | 输出 |
| --- | --- | --- |
| 判断问题涉及哪些规范 | `mcp/3gpp-mcp-server.md`、`sources/3gpp-portal.md` | 候选 TS/TR、工作组、Release 范围 |
| 查询术语官方定义 | `mcp/teddi-mcp.md` | 术语定义、来源、待核验项 |
| 查 clause、procedure、IE 原文 | `rag/`、`TDoc/_index/`、`sources/3gpp-forge.md` | 原文片段、clause、版本 |
| 分析 CR 为什么引入 | `sources/3gpp-portal.md`、`TDoc/`、`workflows/evidence-schema.md` | CR reason、影响条款、会议状态 |
| 追踪功能演进 | `graphrag/`、`TDoc/_index/`、Meeting Report | TS -> CR -> TDoc -> Meeting 链路 |
| 分析公司立场 | `graphrag/`、TDoc 元数据、Meeting Report | 公司、提案、结论、立场变化 |
| 批量整理会议材料 | `scripts/`、`TDoc/_incoming/`、`TDoc/_processed/` | Markdown、CSV、SQLite 或索引文件 |
| 生成最终报告 | `workflows/report-template.md`、`workflows/checklist.md` | 带证据链的研究报告 |
| 本地资料不足 | `sources/online-search-playbook.md`、`sources/search-recipes.json` | 官方候选来源、下载清单、待核验项 |

## 调用顺序

```text
1. 先读任务和 workflow，判断任务类型。
2. 先查本地资料和索引，避免重复搜索。
3. 需要规范入口时调用 3GPP MCP Server 或 3GPP Portal。
4. 需要术语定义时调用 teddi-mcp。
5. 需要原文证据时调用 RAG 或本地索引。
6. 需要关系链时调用 GraphRAG 或图数据库。
7. 需要批量处理时运行 scripts/ 中的本地脚本。
8. 每个关键结论写入 evidence table。
```

## 兜底规则

- 没有工具配置时，必须在报告中标注对应证据为 `needs_verification`。
- 第三方解释只能作为辅助理解，不能替代官方来源。
- 如果 RAG、GraphRAG 和官方资料结论冲突，以官方 TS/TR、CR、TDoc 中的会议材料和 Meeting Report 为准。
