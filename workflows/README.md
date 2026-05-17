# 3GPP Agentic Research 工作流

本目录用于把一次 3GPP 深度研究任务变成可执行、可复核、可版本管理的流程。新开 Codex / Claude CLI / WorkBuddy 会话时，可以先让 Agent 阅读本目录，再输入研究目标。

## 使用方式

在新会话中输入：

```text
请先阅读 workflows/3gpp-research-kit/ 目录，并按其中工作流执行以下研究任务：

<在这里粘贴研究目标>
```

例如：

```text
请先阅读 workflows/3gpp-research-kit/ 目录，并按其中工作流执行以下研究任务：

请分析 5G UE 开机后的搜网流程，并区分 NAS 层 PLMN selection、AS/RRC 层 cell selection 和后续 RRC establishment。
```

## 工作流文件

| 文件 | 用途 |
| --- | --- |
| `research-system.md` | 定义从研究目标到报告的整体状态机 |
| `tool-orchestration.md` | 把 MCP、RAG、GraphRAG、parser、online search、verifier 组织成工具角色 |
| `task-template.md` | 定义研究目标、范围、工具和输出要求 |
| `evidence-schema.md` | 规定证据表字段，避免只给泛泛结论 |
| `report-template.md` | 规定最终报告结构 |
| `checklist.md` | 研究前、研究中、交付前的自检清单 |
| `tool-routing.md` | 规定不同任务应优先调用 MCP、RAG、GraphRAG、官方资料入口或本地脚本 |

## 推荐执行流程

```text
1. 读取 research-system.md，确认本次研究状态机。
2. 读取 task-template.md，生成本次研究任务说明。
3. 按 checklist.md 做研究计划。
4. 按 tool-orchestration.md 和 tool-routing.md 选择 MCP、RAG、GraphRAG、官方资料入口、本地脚本或在线搜索。
5. 本地资料不足时，按 sources/online-search-playbook.md 和 sources/search-recipes.json 发现官方来源。
6. 检索 TS/TR、CR、TDoc 中的会议材料、Meeting Report 或官方网页。
7. 按 evidence-schema.md 记录证据。
8. 按 templates/research-report.md 或 report-template.md 生成报告。
9. 用 checklist.md 做最终自检。
```

## 质量原则

- 每个关键结论都要尽量回到官方来源。
- 不能确认的 clause、Release、CR、TDoc 或会议结论必须标注为“待核验”。
- 模型推断必须和标准事实分开写。
- 不要把第三方解释当作官方结论。
- 不要把 TDoc 和 TS/TR、CR、Meeting Report 简单并列；TDoc 是会议层面的文档提交与编号体系。
