# GraphRAG Query Template

```yaml
question:
start_entities:
  - type:
    id:
target_entities:
  - type:
    id:
allowed_relations:
  - modifies
  - carried_by
  - discussed_in
  - submitted_by
  - decided_as
  - belongs_to
evidence_required:
  - source_document
  - meeting
  - decision
  - original_text_or_metadata
output:
  - relationship_chain
  - evidence_table_rows
  - open_verification_items
```
