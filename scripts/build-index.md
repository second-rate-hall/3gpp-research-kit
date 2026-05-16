# Build Index

本文件描述索引生成脚本的目标接口。

输入：

```text
TDoc/_processed/
TDoc/_incoming/
```

输出：

```text
TDoc/_index/
```

推荐索引字段：

```text
tdoc_id
title
meeting
working_group
company
document_type
related_spec
related_cr
status
source_path
processed_path
notes
```

索引用途：

- 帮助 Agent 快速定位 TDoc、CR、Meeting Report。
- 为 RAG / GraphRAG 提供元数据过滤。
- 为 evidence table 自动填充来源字段。
