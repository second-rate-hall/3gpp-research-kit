# MCP 配置说明

本目录记录 3GPP Research Kit 推荐使用的 MCP 工具。MCP 不是完整研究系统，而是 Agent 可调用的结构化工具接口。

## 推荐工具

| 工具 | 作用 |
| --- | --- |
| `3gpp-mcp-server` | 查询 3GPP 规范、规范详情和实现要求 |
| `teddi-mcp` | 查询 ETSI / 3GPP 官方术语定义 |
| `patent-mcp-server.py` | 查询专利并提取 Background 段落，用于辅助反推 feature 痛点 |

## 典型调用链

```text
用户目标
-> Agent Planner
-> MCP 查询规范 / 术语 / 专利背景
-> RAG / GraphRAG / 本地资料补充证据
-> Evidence table
-> 报告
```

## Patent background MCP

`patent-mcp-server.py` 用于把 Google Patents 等专利页面中的 `Background` / `Background Art` / `Technical Field` 段落提取出来，辅助分析某个 3GPP feature 背后的商业或工程痛点。

适用场景：

- CHO、RedCap、NTN、Relay、sidelink、power saving 等 feature 的动机不容易只从 TS/TR 看出来。
- 需要从专利背景中反推产业界关心的问题，再回到 CR/TDoc/Meeting Report 核验。

示例：

```powershell
@'
{"method":"tools/list"}
{"method":"tools/call","params":{"name":"search_patents","arguments":{"query":"3GPP RedCap reduced capability UE background","limit":3}}}
'@ | python mcp\patent-mcp-server.py
```

## 证据规则

- MCP 返回结果通常是结构化线索，不能直接替代最终标准证据。
- 关键结论仍应回到 TS/TR、CR、TDoc 中的会议材料、Meeting Report 或官方网页核验。
- 专利背景不是 3GPP 官方结论。
- 报告中必须放入“专利背景与痛点反推”章节。
- 专利来源的结论只能标注为 `auxiliary_background` 或 `inference`。
- 如果没有 CR/TDoc/Meeting Report 支撑，不能把专利背景写成“3GPP 官方设计动机”。
