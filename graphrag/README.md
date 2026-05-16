# GraphRAG Entry Points

本目录记录知识图谱 / GraphRAG 接入方式。GraphRAG 的职责是组织实体关系和证据链，而不是替代官方来源。

适合任务：

- 从 TS clause 追溯到 CR、TDoc、会议和 Work Item。
- 追踪公司在某个议题上的多次提案和会议结果。
- 分析功能从 SI/WI 到 TS 的演进链路。

最小证据链：

```text
TS/TR clause
<- modifies
CR
<- carried_by
TDoc
<- discussed_in
Meeting
<- submitted_by
Company
```

## Existing 3GPP KG Assets

可直接参考的 3GPP 知识图谱资源目前主要是数据集和转换工具，而不是完整 GraphRAG 应用：

| 资源 | 类型 | 用法 |
| --- | --- | --- |
| `GSMA/telecom-kg-rel19` | 3GPP Rel-19 GraphML KG | 可下载 `tkg/rel19_3gpp_telecom_kg.graphml`，用于实体/关系探索和图数据库导入 |
| `otellm/3gpp_knowledgeGraph` | 3GPP Rel-13 GraphML KG | 访问受限，可作为建模参考 |
| `openapi-to-rdf` | OpenAPI -> RDF / SHACL | 适合 3GPP SA5 MnS OpenAPI schema，不是全量 3GPP KG |

本机验证过的 `GSMA/telecom-kg-rel19` 部署位置：

```text
E:\09_KNOWLEDGE\3gpp-kg\telecom-kg-rel19
```

验证结论：GraphML 和 `mappings/entities.json` 可读取，统计为 21,540 nodes、31,718 edges、6,044 entities；`chunks/rel19_text_chunks.jsonl` 有 896,453 行，但当前下载版本的 `text` 字段为空，因此不能直接当作 RAG 文本库使用。推荐把它作为关系导航和候选证据定位入口，再回到官方 TS/TR 原文核验。

最小查询脚本：

```powershell
cd E:\09_KNOWLEDGE\3gpp-kg\telecom-kg-rel19
python query_graphml.py --query handover --limit 3
python query_graphml.py --neighbors SRVCC --limit 5
```
