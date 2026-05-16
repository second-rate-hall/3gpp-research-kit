---
name: 3gpp-research-kit
description: Execute evidence-grounded 3GPP standards research using official TS/TR archives, TDocs, CRs, meeting reports, local parsing/indexing, RAG/GraphRAG assets, MCP/tool adapters, evidence tables, and reproducible report workflows. Use when Codex needs to analyze 3GPP clauses, protocol procedures, release evolution, CR/TDoc rationale, company positions, or standards ambiguities with verifiable sources rather than model memory.
---

# 3GPP Research Kit

Use this skill as the Route 1 workbench for 3GPP standards research. Keep the existing project functionality intact: the CLI, workflow files, source notes, MCP/RAG/GraphRAG adapters, TDoc directories, and report templates are all part of the skill's usable resources.

## Operating Rule

Do not answer from model memory alone. Run an evidence workflow:

```text
research question
-> classify task
-> scope official sources
-> fetch or reuse materials
-> parse and index evidence
-> retrieve clause/TDoc/CR/Meeting evidence
-> fill evidence table
-> cross-check claims
-> write report with open verification items
```

Mark unsupported claims as `needs_verification`.

## First Files To Read

Read only what is needed for the task:

- For command usage: `scripts/README.md`
- For task framing: `workflows/task-template.md`
- For evidence rows: `workflows/evidence-schema.md`
- For reports: `workflows/report-template.md`
- For self-checks: `workflows/checklist.md`
- For tool routing: `workflows/tool-routing.md`
- For official source entry points: `sources/README.md`
- For local materials: `TDoc/README.md`
- For MCP/RAG/GraphRAG integration: `mcp/README.md`, `rag/README.md`, `graphrag/README.md`
- For optional external skills/tools: `skills/external-skills.md`

Avoid bulk-loading every file. Use targeted reads and searches.

## Local CLI

Run commands from the project root:

```bash
python scripts/3gpp_research.py --help
```

Core commands:

```bash
python scripts/3gpp_research.py fetch --url <official-url>
python scripts/3gpp_research.py fetch-list --file urls.txt
python scripts/3gpp_research.py fetch-spec --spec 38.331 --latest
python scripts/3gpp_research.py parse
python scripts/3gpp_research.py build-db
python scripts/3gpp_research.py search "RRCSetup*" --limit 5
python scripts/3gpp_research.py relations --limit 20
python scripts/3gpp_research.py check-tools --config tools.example.json
python scripts/3gpp_research.py run-tool <name> <args...>
python scripts/3gpp_research.py verify research-runs/_template/report.md
python scripts/3gpp_research.py research "请分析 RRCSetup 在 RRC re-establishment fallback 场景中的作用" --spec 38.331 --latest
```

Generated artifacts live under `TDoc/_processed/` and `TDoc/_index/`. Do not treat generated indexes as source truth; use them to point back to official documents.

## One-click Deep Research

Use `research` when the user wants the kit itself to produce a deep report without manually running each low-level command. This command is intentionally generic and evidence-first:

```text
question
-> classify task
-> infer/accept candidate specs
-> fetch or reuse official materials
-> parse and build SQLite FTS
-> retrieve evidence
-> generate evidence table and report
-> run verification
```

The report is a professional research draft, not a final standards ruling. If CR/TDoc/Meeting Report coverage is incomplete, keep motivation, company-position, and release-evolution claims as `needs_verification`.

Keep the distinction clear: `3gpp-research-kit` may independently generate reports as a skill/workspace, while `3gpp-research-agent` may call the kit as its evidence backend and add stronger planning, multi-model writing, specialized reporters, and productized CLI behavior.

## Tool Routing

Prefer this order:

1. Existing local materials and indexes in `TDoc/`.
2. `scripts/3gpp_research.py research` for one-click deep research, or lower-level fetch, parse, build-db, search, relations, verify when manual control is needed.
3. `mcp/` notes and configured MCP wrappers for spec discovery or implementation requirements.
4. `rag/` notes or configured RAG tools for clause/procedure/IE retrieval.
5. `graphrag/` assets for TS -> CR -> TDoc -> meeting/company/release relationships.
6. `sources/` official 3GPP Portal, FTP, Forge, ETSI entry points.
7. Web search only as auxiliary context; verify final claims against official sources.

If an external tool is configured in `tools.json`, check it first:

```bash
python scripts/3gpp_research.py check-tools
```

Then run it through:

```bash
python scripts/3gpp_research.py run-tool <tool-name> <tool-args...>
```

## Report Contract

Every final report should include:

- conclusion summary with confidence labels
- research scope and exclusions
- standards/source inventory
- evidence table with official URL, version, pointer, and status
- analysis by clause/procedure/stage/topic
- similarities, differences, and boundary conditions when comparing specs/releases
- open verification items
- reusable engineering brief

Use `workflows/report-template.md` and `workflows/checklist.md` before finalizing.

## Source Discipline

Treat these as acceptable grounding sources:

- official TS/TR clause or specification archive
- CR and reason for change
- TDoc-carried meeting material
- Meeting Report
- official 3GPP / ETSI / GSMA source

Third-party commentary can guide investigation but cannot be final evidence.

## Preservation Contract

This skill is also a full project. Do not remove or weaken existing capabilities when updating it:

- keep the CLI commands working
- keep workflow templates available
- keep MCP/RAG/GraphRAG adapter notes available
- keep local TDoc directories and generated-output conventions
- keep report verification behavior
- add enhancements as new scripts, references, templates, or skill instructions
