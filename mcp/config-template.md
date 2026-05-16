# MCP Config Template

不同客户端的 MCP 配置格式可能略有差异。下面是一个概念模板，实际使用时请按 Codex、Claude Desktop、Claude CLI、Cursor 或 VSCode 的配置要求调整。

```json
{
  "mcpServers": {
    "3gpp": {
      "command": "<your-3gpp-mcp-server-command>"
    },
    "teddi": {
      "command": "teddi-mcp"
    }
  }
}
```

## 推荐工具

- `3gpp`：用于搜索 3GPP 规范、获取规范详情、查找实现要求。
- `teddi`：用于查询 ETSI / 3GPP 官方术语定义。

## 使用原则

MCP 结果是结构化线索，不等于最终标准结论。关键结论仍应回到 TS/TR、CR、TDoc 中的会议材料、Meeting Report 或官方网页核验。

