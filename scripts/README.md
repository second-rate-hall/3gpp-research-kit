# Scripts

## Track Changes aware DOCX parsing

3GPP CR 和 TDoc 经常是 Word 修订模式文档。不要把 `.docx` 直接抽成普通纯文本后喂给 LLM，否则删除内容和新增内容可能混在一起，造成标准结论幻觉。

本项目新增：

```text
scripts/docx_track_changes_parser.py
```

它直接解析 WordprocessingML：

- `<w:ins>` 输出为 `+ inserted text`
- `<w:del>` / `<w:delText>` 输出为 `- deleted text`
- 普通文本保持原样

示例：

```powershell
python scripts\docx_track_changes_parser.py TDoc\_incoming\R2-xxxxxxx.docx --out TDoc\_processed\R2-xxxxxxx.trackchanges.md
```

`scripts/3gpp_research.py parse` 已默认使用该解析器处理 DOCX。

本目录包含本项目的本地自动化入口。现成工作环境型 Agent 可以调用这些脚本完成下载、解析、建库、检索和证据检查。

`scripts/3gpp_research.py` 不应承载 3GPP 领域知识和报告结构。可配置内容放在：

- `config/research-taxonomy.json`：任务分类、候选规范提示、检索扩展、排序和 claim 规则。
- `templates/research-report.md`：一键研究报告模板。
- `tools/registry.json`：MCP、RAG、GraphRAG、专利背景和本地 CLI 的工具角色。
- `sources/search-recipes.json`：本地资料不足时的在线搜索 recipes。

## CLI

```bash
python scripts/3gpp_research.py --help
```

常用命令：

```bash
python scripts/3gpp_research.py fetch-spec --spec 38.331 --latest
python scripts/3gpp_research.py fetch --url https://www.3gpp.org/ftp/tsg_ran/WG2_RL2/TSGR2_104/Docs/R2-1817862.zip
python scripts/3gpp_research.py fetch-list --file urls.txt
python scripts/3gpp_research.py parse
python scripts/3gpp_research.py build-db
python scripts/3gpp_research.py search "RRCSetup*" --limit 3
python scripts/3gpp_research.py relations --limit 10
python scripts/3gpp_research.py check-tools --config tools.example.json
python scripts/3gpp_research.py verify research-runs/_template/report.md
python scripts/3gpp_research.py research "请分析 RRCSetup 在 RRC re-establishment fallback 场景中的作用" --spec 38.331 --latest
```

外部工具桥接：

```bash
cp tools.example.json tools.json
python scripts/3gpp_research.py check-tools
python scripts/3gpp_research.py run-tool teddi search-term QoS --pattern exactmatch
```

说明：`teddi`、Telco-RAG、Chat3GPP、3GPP MCP wrapper 需要用户自行安装。本项目提供统一调用入口，但不捆绑这些外部系统。

## Files

| 文件 | 用途 |
| --- | --- |
| `3gpp_research.py` | 下载、解析、建库、检索、证据检查和模板渲染的本地 CLI |
| `convert-documents.md` | 描述 PDF / DOCX / ZIP 等资料转换为 Markdown、TXT、CSV、JSON 的目标接口 |
| `build-index.md` | 描述从原始资料和转换结果生成 `TDoc/_index/` 元数据索引的目标接口 |

## One-click Deep Research

`research` 是给独立工作区和 Codex 类 Agent 使用的上层入口。它会自动执行：

```text
question
-> classify task by config/research-taxonomy.json
-> infer or accept candidate specs by config/research-taxonomy.json
-> fetch or reuse official materials
-> parse
-> build-db
-> retrieve evidence by configured query expansion and ranking rules
-> render templates/research-report.md
-> write research-runs/<timestamp>-<topic>.md
-> verify report
```

示例：

```bash
python scripts/3gpp_research.py research "请对比 4G 和 5G RRC re-establishment 流程" --spec 36.331 --spec 38.331
python scripts/3gpp_research.py research "请分析 RRCSetup 在 RRC re-establishment fallback 场景中的作用" --spec 38.331 --no-fetch
```

这个入口是通用、证据优先、可解释的深度研究草案生成器。它会保守标注 `confirmed`、`evidence-grounded` 和 `needs_verification`，不会替代 `3gpp-research-agent` 中更强的 Planner、多模型 writer 或专项报告器。

## Generated Outputs

```text
TDoc/_processed/
TDoc/_index/metadata.csv
TDoc/_index/research.db
```

这些输出默认是本地生成物，不应直接提交到公开仓库。

## Design Rules

- 不删除 `TDoc/_incoming/` 中的原始资料。
- 中间结果写入 `TDoc/_processed/`。
- 元数据写入 `TDoc/_index/`。
- 输出应便于 Agent 读取，例如 CSV、JSON、Markdown、SQLite。
