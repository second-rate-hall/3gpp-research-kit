# Evidence Schema

本文件规定 3GPP 研究中的证据表结构。Agent 在研究过程中应维护一张 evidence table，避免只输出不可复核的自然语言结论。

## 推荐字段

| 字段 | 含义 | 示例 |
| --- | --- | --- |
| `id` | 证据编号 | E001 |
| `claim` | 支撑的结论 | UE cell selection 主要由 TS 38.304 规定 |
| `source_type` | 来源类型 | TS、TR、CR、TDoc、Meeting Report、Portal、FTP、Patent、第三方 |
| `source_id` | 来源编号 | TS 38.304、R2-1817862、USxxxx |
| `version_or_release` | 版本或 Release | Rel-18、v18.4.0、待核验 |
| `clause_or_section` | clause 或章节 | 5.2.3.2、Background、待核验 |
| `title` | 来源标题或材料标题 | UE procedures in Idle mode |
| `evidence_summary` | 证据摘要 | 该规范描述 UE 在 idle mode 下的小区选择流程 |
| `quote_or_pointer` | 原文短摘或定位线索 | clause、页码、URL、文件路径、chunk_index |
| `status` | 证据状态 | confirmed、needs_verification、conflicting、inference、auxiliary_background |
| `notes` | 备注 | 需要核验具体 clause |

## Markdown 表格模板

```markdown
| id | claim | source_type | source_id | version_or_release | clause_or_section | evidence_summary | quote_or_pointer | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E001 |  |  |  |  |  |  |  | needs_verification |
```

## 专利背景字段

专利材料只用于反向理解商业或工程痛点，不能单独确认 3GPP 标准事实。

```markdown
| id | feature | patent_source | assignee_or_inventor | background_excerpt | inferred_pain_point | linked_3gpp_evidence | status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P001 |  |  |  |  |  |  | auxiliary_background |
```

## 证据状态约定

- `confirmed`：已回到官方来源，或本地资料保留了可追溯的官方来源 URL、文件路径和 hash。
- `needs_verification`：方向合理，但缺 clause、版本、原文或官方链接。
- `conflicting`：不同来源之间存在冲突，需要人工复核。
- `inference`：基于证据的推断，不能写成标准事实。
- `auxiliary_background`：来自专利、论文、博客、厂商材料等辅助背景，只能用于解释可能痛点或动机。

## 强制规则

- 关键结论不能只有 `inference` 或 `auxiliary_background`，必须至少有一个官方或准官方来源支撑。
- 第三方解释只能作为辅助理解，不能作为最终标准事实。
- 如果来源是 TDoc，要说明它承载的是 CR、LS、提案、报告还是其他会议材料。
- 如果来源是 Patent，要说明它提取的是 `Background`、`Background Art`、`Technical Field` 还是说明书其他部分。
- `confirmed` 行必须能指出 TS/TR、CR、TDoc、Meeting Report、3GPP Portal、3GPP FTP、3GPP Forge 或 ETSI/TEDDI 等官方来源；否则应降级为 `needs_verification`。
