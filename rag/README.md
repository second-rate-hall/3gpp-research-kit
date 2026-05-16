# RAG Entry Points

本目录记录结构化 RAG 或本地 RAG 系统的接入方式。RAG 的职责是从大量 TS/TR、CR、TDoc、Meeting Report 或已转换资料中检索原文证据。

## 可接入系统

| 系统 | 文件 | 用途 |
| --- | --- | --- |
| Telco-RAG | `telco-rag.md` | 查询增强、规范系列路由、标准问答 |
| Chat3GPP | `chat3gpp.md` | 本地 3GPP RAG 问答和原文检索 |
| 通用查询模板 | `query-template.md` | 统一记录问题、过滤条件、引用要求 |

## 使用原则

- RAG 返回的结果必须保留 `spec_id`、`version`、`release`、`clause`、来源文件或 URL。
- 不能只复制模型总结，应尽量记录原文片段和引用位置。
- 对 Release、RAT、工作组或协议层不确定的结果，标记为 `needs_verification`。
