---
name: 3gpp-research-kit
description: Execute reproducible 3GPP standards research with evidence tables, official-source grounding, workflow templates, and report generation. Use for CR tracing, clause explanation, release comparison, protocol procedure analysis, company-position analysis, and feature evolution research.
---

# 3GPP Research Kit Skill

Use this skill when the user asks for deep research on 3GPP standards, protocols, CRs, TDocs, meeting reports, Release evolution, protocol procedures, or standards design rationale.

## Core Rule

Do not produce a generic explanation. Execute a research workflow:

```text
Goal
-> classify task
-> scope sources
-> retrieve evidence
-> build evidence table
-> cross-check
-> write report
-> mark open verification items
```

## Required Source Discipline

Every key claim should be grounded in one of:

- TS/TR clause or official specification page.
- CR and its reason for change.
- TDoc-carried meeting material.
- Meeting Report.
- Official 3GPP / ETSI / GSMA source.

If a claim cannot be grounded, mark it as `needs_verification`.

## Task Types

Classify the task before researching:

- clause explanation
- CR trace
- Release comparison
- company-position analysis
- feature evolution
- protocol procedure analysis
- test-case draft
- ambiguity or conflict check

## Required Workflow Files

Before starting, read:

```text
workflows/task-template.md
workflows/evidence-schema.md
workflows/report-template.md
workflows/checklist.md
workflows/tool-routing.md
skills/external-skills.md
mcp/README.md
rag/README.md
graphrag/README.md
sources/README.md
scripts/README.md
TDoc/README.md
```

## Tool Priority

Use available tools in this order:

1. Local project files and existing research notes.
2. User-provided materials under `TDoc/_incoming/` and indexes under `TDoc/_index/`.
3. Follow `workflows/tool-routing.md` to choose tools.
4. 3GPP MCP Server for specification discovery and implementation requirements.
5. teddi-mcp / TEDDI for official terminology.
6. Local RAG / structured RAG for clause, procedure, IE, and original-text retrieval.
7. GraphRAG / graph database for relationship tracing.
8. 3GPP Portal, FTP, Forge, and official pages for final verification.
9. Local scripts for document conversion, metadata extraction, CSV/SQLite indexes, and evidence validation.
10. Web search only as auxiliary context.

## One-click Deep Research

When the user wants `3gpp-research-kit` itself to generate a report, prefer the upper-level command before manually chaining low-level tools:

```bash
python scripts/3gpp_research.py research "<研究问题>" --spec 38.331 --latest
```

This command should remain generic, evidence-first, and explainable. It may classify the task, infer or accept candidate specs, fetch/reuse official materials, parse/build the local index, retrieve evidence, write a report under `research-runs/`, and run evidence verification.

Do not make this command overlap completely with a dedicated product Agent. `3gpp-research-agent` can consume the kit as an evidence backend and add stronger Planner logic, multi-model report writing, specialized reporters, and productized CLI behavior. The kit must still work independently as a Codex skill/workspace.

## Output Contract

The final report must include:

- conclusion summary
- research scope
- standards basis table
- evidence table
- analysis by stage/topic
- common mistakes or boundary clarifications
- open verification items
- reusable summary

## Forbidden

- Do not answer from model memory alone.
- Do not treat third-party commentary as an official standard conclusion.
- Do not conflate TDoc with TS/TR, CR, or Meeting Report.
- Do not omit open verification items when source coverage is incomplete.
