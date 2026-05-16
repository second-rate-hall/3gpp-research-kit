# 3GPP Research Kit

`3gpp-research-kit` is an evidence-first workbench for researching 3GPP standards with local files, official sources, and AI coding agents such as Codex, Claude CLI, or similar workspace agents.

It is not a chatbot and it does not claim to contain all 3GPP knowledge. Its purpose is narrower and more useful: help you turn a standards question into a reproducible research run with source inventory, evidence table, verification status, and a report that can be checked against official 3GPP material.

## Why This Exists

3GPP answers are rarely contained in one paragraph. A serious analysis often needs to connect:

```text
TS/TR clause
-> CR and reason for change
-> TDoc / contribution
-> Meeting Report
-> Work Item / Release context
```

This repository gives you a local project structure and CLI for that workflow:

- Download or reuse official 3GPP files.
- Parse ZIP / DOCX / TXT / MD / CSV / HTML files.
- Preserve Word track-change intent in DOCX parsing.
- Build a local SQLite FTS evidence database.
- Search evidence and inspect basic relation rows.
- Generate a conservative deep research report.
- Verify that `confirmed` claims have obvious source markers.

## Quick Start

Clone the repository and run commands from the project root.

```bash
python scripts/3gpp_research.py --help
```

Run a minimal evidence loop:

```bash
python scripts/3gpp_research.py fetch-spec --spec 38.331 --latest
python scripts/3gpp_research.py parse
python scripts/3gpp_research.py build-db
python scripts/3gpp_research.py search "RRCSetup fallback" --limit 5
```

Run one-click deep research:

```bash
python scripts/3gpp_research.py research "请分析 RRCSetup 在 RRC re-establishment fallback 场景中的作用" --spec 38.331 --latest
```

The report is written under `research-runs/` and then checked with the built-in evidence verifier.

## Use With Codex Or Another Workspace Agent

Open this repository in your agent tool and ask it to follow the project workflow:

```text
Read README.md, SKILL.md, workflows/, scripts/, sources/, TDoc/README.md,
then perform evidence-grounded 3GPP research for this question:

<your question>
```

The agent should use the local CLI and templates instead of answering from model memory.

## Local Materials

Put user-provided standards material here:

```text
TDoc/_incoming/
```

Then parse and index:

```bash
python scripts/3gpp_research.py parse
python scripts/3gpp_research.py build-db
```

Generated files are local working artifacts and are ignored by Git:

```text
TDoc/_processed/
TDoc/_index/metadata.csv
TDoc/_index/research.db
research-runs/<generated reports>
```

## CLI Commands

| Command | Purpose |
| --- | --- |
| `fetch --url <url>` | Download an official URL into `TDoc/_incoming/` |
| `fetch-list --file urls.txt` | Download a list of URLs |
| `fetch-spec --spec 38.331 --latest` | Download a ZIP from the 3GPP Specs archive |
| `parse` | Parse incoming files into Markdown/text artifacts |
| `build-db` | Build SQLite FTS and relation tables |
| `search <query>` | Search the local evidence database |
| `relations` | Show basic GraphRAG-style relation rows |
| `check-tools` | Check external tools configured in `tools.json` |
| `run-tool <name>` | Run an external tool configured in `tools.json` |
| `verify <file>` | Check a report for ungrounded `confirmed` claims |
| `research <question>` | Run a generic evidence-first research workflow |

## Project Layout

```text
3gpp-research-kit/
  README.md
  SKILL.md
  workflows/        # task, evidence, report, checklist, routing templates
  scripts/          # local CLI and parsers
  sources/          # official 3GPP / FTP / Forge notes
  mcp/              # MCP integration notes and examples
  rag/              # RAG integration notes
  graphrag/         # graph schema, relation template, KG notes
  TDoc/             # local source material workspace
  research-runs/    # report templates and generated runs
  example/          # sample research report
```

## Evidence Rules

Use these as final grounding sources whenever possible:

- Official TS/TR clause or specification archive.
- CR and reason for change.
- TDoc-carried meeting material.
- Meeting Report.
- Official 3GPP / ETSI / GSMA source.

If evidence is incomplete, mark the claim as `needs_verification`. Third-party pages, patents, and model outputs can guide investigation, but they are not final standards evidence.

## Relationship To 3GPP Research Agent

`3gpp-research-kit` is the reusable workbench and evidence layer.

`3gpp-research-agent` is a separate dedicated CLI agent that can build on this evidence layer while adding stronger planning, model calls, specialized report generation, and run management.

The kit should remain useful on its own: a human or a workspace agent can clone this repository and produce a report without installing the dedicated agent.

## Current Status

Executable MVP.

Implemented:

- Local project workflow and templates.
- 3GPP research skill instructions.
- Official source notes and tool-routing rules.
- CLI for download, parse, index, search, relations, verify, and one-click research.
- DOCX track-change aware parsing.
- External tool bridge through `tools.json`.
- Example report and report templates.

Not yet complete:

- Full CR / TDoc / Meeting Report portal-scale automation.
- Clause-aware parser with exact clause pointers for every chunk.
- Production GraphRAG database integration.
- Packaged Python API; the current stable interface is the CLI.

## Disclaimer

This project helps organize 3GPP standards research. It does not provide official standards conclusions. Always verify important claims against official 3GPP, ETSI, or other authoritative sources.
