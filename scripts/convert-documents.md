# Convert Documents

本文件描述文档转换脚本的目标接口。具体实现可以使用 Python、Pandoc、LibreOffice、docx2txt、pdfplumber 或团队已有工具。

输入：

```text
TDoc/_incoming/
```

输出：

```text
TDoc/_processed/
```

推荐输出格式：

- Markdown：便于 Agent 阅读。
- Plain text：便于全文索引。
- JSON / CSV：便于结构化抽取。

要求：

- 不删除原始文件。
- 保留原始文件名、路径、会议目录和 TDoc 编号。
- 转换失败时生成错误记录，方便人工补处理。
