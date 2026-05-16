# 3GPP MCP Server

3GPP MCP Server 适合承担 Agentic Research 中的“规范入口查询”步骤。

## 适合做什么

- 搜索相关 3GPP TS/TR。
- 获取规范详情。
- 查找实现要求。
- 为后续 RAG / GraphRAG / 人工复核提供规范范围。

## 典型工具调用

```text
Used MCP tool: 3gpp-server/search_specifications
Used MCP tool: 3gpp-server/get_specification_details
Used MCP tool: 3gpp-server/find_implementation_requirements
```

## 典型问题

```text
请分析 5G UE 开机后的搜网流程，并区分 NAS 层 PLMN selection、AS/RRC 层 cell selection 和后续 RRC establishment。
```

可能返回的规范入口：

| 范围 | 相关规范 | 作用 |
| --- | --- | --- |
| PLMN selection | TS 23.122 | NAS 层网络选择规则 |
| Cell selection | TS 38.304 | Idle mode / RRC Inactive 下的小区选择 |
| RRC establishment | TS 38.331 | RRC 连接建立 |
| Registration | TS 24.501 / TS 23.502 | NAS 注册流程 |

## 注意事项

- MCP 返回的是研究入口和结构化线索。
- 最终报告仍应补充 clause、版本和原文证据。
- 若工具结果与官方页面或规范文本冲突，应以官方规范为准。

