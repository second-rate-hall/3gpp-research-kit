# Roadmap

`3gpp-research-kit` 的目标是从 executable MVP 演进为可由现成工作环境型 Agent 驱动的本地 3GPP 标准研究引擎。

## v0.1.0: Executable MVP

Status: in progress.

- Download official 3GPP spec archive ZIPs.
- Download official TDoc / CR / Meeting Report URLs.
- Batch download official URL lists.
- Extract ZIP files.
- Parse DOCX / TXT / MD / CSV / HTML.
- Optionally parse PDF when `pypdf` is installed.
- Generate `TDoc/_index/metadata.csv`.
- Build SQLite FTS local RAG database.
- Build basic GraphRAG-style relation table.
- Search local evidence.
- Check external tool availability through `tools.json`.
- Run configured external tools.
- Verify that confirmed report lines include obvious source markers.

## v0.2.0: Better 3GPP Metadata Extraction

- Extract spec version from 3GPP archive filenames.
- Extract TS/TR clauses from converted documents.
- Extract CR fields: reason for change, summary, affected clauses, category, release.
- Extract TDoc metadata: meeting, WG, company, title, status.
- Extract Meeting Report decisions: agreed, approved, revised, noted, rejected.
- Improve source URL propagation from downloaded ZIP to extracted members.

## v0.3.0: RAG Improvements

- Add parent-child chunking for clauses.
- Preserve clause path, title path, table id, and figure id.
- Add optional vector store backends such as Chroma or Qdrant.
- Add reranking hook.
- Export retrieved evidence rows directly to `research-runs/<run>/evidence.md`.

## v0.4.0: GraphRAG Improvements

- Promote high-confidence relations from metadata.
- Add import/export for Neo4j-compatible CSV.
- Add relation verification workflow.
- Add feature evolution queries:

```text
Feature -> Work Item -> TDoc -> CR -> TS clause
```

## v0.5.0: Tool Integrations

- Provide wrappers for teddi CLI / teddi-mcp.
- Provide a documented MCP client wrapper pattern for 3GPP MCP Server.
- Provide Telco-RAG and Chat3GPP adapter examples.
- Add `tools.example.json` profiles for common local setups.

## Non-goals

- No public web chatbot.
- No claim that model output is official standard interpretation.
- No redistribution of large downloaded 3GPP material by default.
- No confirmed conclusion without official-source evidence.
