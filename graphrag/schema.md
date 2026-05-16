# Graph Schema

## Core Entities

| Entity          | Description                              |
| --------------- | ---------------------------------------- |
| `Specification` | TS/TR 等标准文档                              |
| `Clause`        | 条款级知识单元                                  |
| `CR`            | Change Request                           |
| `TDoc`          | 会议提交文档编号与承载材料                            |
| `Meeting`       | 3GPP 会议                                  |
| `Company`       | 提案主体或参与方                                 |
| `Feature`       | 技术特性或功能点                                 |
| `WorkItem`      | SI/WI/Work Item                          |
| `Release`       | Rel-15、Rel-18、Rel-19 等                   |
| `Decision`      | agreed、approved、revised、noted、rejected 等 |

## Core Relations

| Relation | Description |
| --- | --- |
| `contains_clause` | TS/TR 包含 clause |
| `references` | 条款或文档引用另一个条款或文档 |
| `modifies` | CR 修改 clause |
| `carried_by` | CR、LS 或提案由 TDoc 承载 |
| `submitted_by` | TDoc 或 CR 由公司提交 |
| `discussed_in` | TDoc、CR 或议题在会议中讨论 |
| `decided_as` | 会议对材料给出处理结论 |
| `belongs_to` | 文档、功能、CR 属于 Release、WI 或 Feature |
| `supersedes` | TDoc revision 替代前一版本 |
| `motivates` | 会议讨论或设计问题促成后续 CR |

低确定性的关系应先标记为 `candidate_relation`，人工复核后再提升为正式关系。
