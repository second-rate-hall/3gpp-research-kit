# Publishing Checklist

## Skill Packaging

This repository is also a valid Codex skill folder. The root contains:

```text
SKILL.md
agents/openai.yaml
```

Validation:

```bash
python C:\Users\lzh\.codex\skills\.system\skill-creator\scripts\quick_validate.py .
```

Use as a local skill by copying or symlinking the repository folder into:

```text
%USERPROFILE%\.codex\skills\3gpp-research-kit
```

The skill packaging is additive. Do not remove the standalone project assets when publishing:

- `scripts/3gpp_research.py`
- `workflows/`
- `TDoc/`
- `mcp/`
- `rag/`
- `graphrag/`
- `sources/`
- `research-runs/`

本文件用于把 `3gpp-research-kit` 从本地项目骨架整理成可正式发布的 GitHub 仓库。

## Required Before Public Release

- Choose a repository owner and final URL.
- Choose a license and add `LICENSE`.
- Review all example content and confirm it does not include private, confidential, or copyrighted non-redistributable material.
- Confirm `.gitignore` excludes large local 3GPP downloads under `TDoc/_incoming/` and generated conversions under `TDoc/_processed/`.
- Confirm tracked files are only templates, instructions, examples, and small metadata samples.
- Run a fresh-agent test using `prompts/start-research.md`.
- Check that every README link points to an existing file.

## Recommended Before v0.1.0

- Add `CONTRIBUTING.md`.
- Add `CHANGELOG.md`.
- Add a short English summary or bilingual README section.
- Add one minimal fake/sample TDoc metadata row that does not depend on downloaded 3GPP files.
- Add screenshots or terminal snippets showing a completed research run.
- Add GitHub topics such as `3gpp`, `agentic-research`, `rag`, `graphrag`, `standards`, `telecom`.

## Release Positioning

Recommended GitHub description:

```text
Agent workflow kit for reproducible 3GPP standards research with evidence tables, MCP/RAG/GraphRAG hooks, and report templates.
```

Recommended first release tag:

```text
v0.1.0
```

Recommended release title:

```text
Initial scaffold for evidence-grounded 3GPP agentic research
```

## License Decision

Pick one before public release:

| License | When to choose |
| --- | --- |
| MIT | You want broad reuse with minimal restrictions |
| Apache-2.0 | You want broad reuse plus explicit patent language |
| CC BY 4.0 | You view this mainly as documentation/templates rather than software |
| No license yet | You are not ready for public reuse |

Do not publish as an open-source project without a license. Without a license, others can view the code on GitHub but do not receive clear reuse rights.
