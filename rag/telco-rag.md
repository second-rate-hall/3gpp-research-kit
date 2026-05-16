# Telco-RAG

Telco-RAG 可作为研究型 RAG 入口，用于电信标准问答、查询增强和规范系列路由。

## 适合任务

- 判断问题可能属于哪些规范系列。
- 对概念性问题生成增强查询。
- 缩小 3GPP 全库检索范围。

## Agent 使用要求

记录每次查询：

```text
question:
expanded_query:
candidate_specs:
retrieved_passages:
citations:
open_issues:
```

如果 Telco-RAG 返回的是候选答案，Agent 仍需回到官方 TS/TR、CR、TDoc 或 Meeting Report 做最终核验。
