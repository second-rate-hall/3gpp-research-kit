# TDoc Index

本目录用于保存 TDoc、CR、Meeting Report、LS、contribution 等资料的元数据索引。

推荐使用 `metadata-template.csv` 作为起点。Agent 在研究前应优先读取这里的索引，以减少重复扫描和错误检索。

## 建议流程

```text
TDoc/_incoming/
-> 扫描文件
-> 抽取文件名、TDoc 编号、会议、公司、标题、文档类型
-> 写入 TDoc/_index/metadata.csv
-> 后续研究优先读取 metadata.csv
```

