# teddi-mcp

teddi-mcp 适合承担 Agentic Research 中的“术语核验”步骤。它用于查询 ETSI / 3GPP 官方术语定义，避免把工程口语、第三方解释和官方定义混在一起。

## 适合查询

- QoS
- 5QI
- PDU Session
- network slicing
- RRC
- PLMN
- NAS

## 命令示例

```bash
teddi search-term "QoS" --pattern exactmatch
```

## 在研究流程中的位置

```text
术语出现歧义
-> 调用 teddi-mcp
-> 获取官方术语定义
-> 写入 evidence table
-> 在报告中区分官方定义与工程解释
```

