# TDoc Materials

本目录是用户预下载 3GPP 材料的入口。用户可以把从 3GPP Portal / FTP 下载的 TDoc、CR、Meeting Report、LS、contribution、agenda、document list、ZIP、PDF、DOCX、XLSX 等文件放在这里，供 Agentic Research workflow 使用。

## 目录结构

```text
TDoc/
  README.md
  _incoming/
  _processed/
  _index/
    metadata-template.csv
```

## 用法

### 1. 放入原始资料

把原始下载文件放入：

```text
TDoc/_incoming/
```

例如：

```text
TDoc/_incoming/RAN2/
TDoc/_incoming/SA2/
TDoc/_incoming/Rel-18/
TDoc/_incoming/meeting-reports/
```

### 2. 处理后的资料

Agent 或脚本转换得到的 Markdown、纯文本、CSV、JSON 等中间结果应放入：

```text
TDoc/_processed/
```

不要覆盖或删除 `_incoming/` 中的原始文件。

### 3. 元数据索引

如果用户或 Agent 已经建立文件清单，应放入：

```text
TDoc/_index/
```

建议使用：

```text
TDoc/_index/metadata-template.csv
```

## Agent 读取规则

Agent 执行研究时应按以下顺序检查：

```text
1. TDoc/_index/ 中是否已有元数据索引。
2. TDoc/_processed/ 中是否已有可读文本。
3. TDoc/_incoming/ 中是否有原始文件。
4. 如仍缺证据，再查询 MCP、RAG、GraphRAG 或官方网页。
```

## 重要约定

- TDoc 是 3GPP 会议层面的文档提交与编号体系。
- TDoc 可以承载 CR、LS、提案、报告等会议材料。
- 写报告时不要把 TDoc 与 TS/TR、CR、Meeting Report 简单并列。
- 原始资料默认不提交到 GitHub，避免上传大文件或受权限限制的资料。

