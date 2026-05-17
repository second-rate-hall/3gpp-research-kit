# Tool Orchestration

本文件把 kit 中列出的工具组织成可执行的研究编排规则。Codex / Claude CLI 在执行 3GPP 深度研究时，应按角色调用工具，而不是按目录随意挑选。

## 工具角色

| 角色 | 目的 | 首选工具 |
| --- | --- | --- |
| Planner | 判断任务类型、证据需求、候选规范 | `config/research-taxonomy.json`、LLM |
| Source Discovery | 找官方资料入口 | `3gpp_mcp`、3GPP Portal、FTP、Forge、online search |
| Terminology | 查官方术语 | `teddi`、TS/TR glossary |
| Acquisition | 下载或导入资料 | `fetch`、`fetch-spec`、`fetch-list` |
| Parser | 解析 ZIP/DOCX/PDF/HTML | `parse`、`docx_track_changes_parser.py` |
| Retriever | 查 clause、procedure、IE、CR 片段 | local FTS、Chat3GPP、Telco-RAG |
| Relation Builder | 串联 TS/TR、CR、TDoc、Meeting、Company、Release | `relations`、GraphRAG schema |
| Auxiliary Background | 反推技术/商业痛点 | `patent_mcp` |
| Verifier | 检查 confirmed claim 是否有官方证据 | `verify`、`checklist.md` |
| Reporter | 生成完整报告 | `templates/research-report.md`、evidence rows |

## 调用策略

```text
本地资料足够
-> parse / build-db / search / relations / report / verify

本地资料不足
-> online search recipes
-> fetch / fetch-list / fetch-spec
-> parse / build-db / search / relations / report / verify

术语不明确
-> teddi / glossary

规范范围不明确
-> 3gpp_mcp / Portal / DynaReport

需要演进链路或公司立场
-> CR / TDoc / Meeting Report
-> GraphRAG relation table

需要动机或痛点背景
-> patent_mcp
-> 标注 auxiliary_background
```

## 冲突处理

- 官方 TS/TR、CR、TDoc、Meeting Report 优先于 RAG 摘要。
- Portal/FTP 元数据优先于第三方网页。
- 专利背景不能升级为 3GPP 官方动机，除非 CR/TDoc/Meeting Report 另有支撑。
- 工具缺失时，报告中对应证据状态保持 `needs_verification`。
