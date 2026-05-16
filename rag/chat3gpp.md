# Chat3GPP

Chat3GPP 可作为本地 3GPP RAG 问答系统的参考或接入口。

## 适合任务

- 查询 TS/TR 中的 clause、procedure、message、IE。
- 基于本地索引检索规范原文。
- 为 evidence table 提供初始候选证据。

## Agent 使用要求

每条 RAG 证据应记录：

```text
spec_id:
version:
release:
clause:
source_file:
retrieved_text:
why_relevant:
verification_status:
```

如果项目没有部署 Chat3GPP，可把本文档作为“本地 RAG 应如何返回证据”的接口约定。
