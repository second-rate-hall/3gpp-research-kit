# Start Research Prompt

复制下面这段到 Codex、Claude CLI、WorkBuddy 或其他支持读取本地文件的 Agent：

```text
请先阅读 README.md、skills/3gpp-research-kit/SKILL.md、skills/external-skills.md、workflows/、mcp/、rag/、graphrag/、sources/、scripts/ 和 TDoc/README.md。

请按 3GPP Agentic Research 工作流执行以下研究任务：

<在这里粘贴研究目标>

要求：
1. 优先检查 TDoc/_index/、TDoc/_processed/ 和 TDoc/_incoming/ 中是否已有用户提供资料。
2. 按 workflows/tool-routing.md 选择 3GPP MCP Server、teddi-mcp、本地 RAG、GraphRAG、官方资料入口或本地脚本。
3. 必要时使用 sources/ 中的 3GPP Portal、FTP、Forge 入口做官方核验。
4. 按 workflows/evidence-schema.md 建立 evidence table。
5. 按 workflows/report-template.md 输出报告。
6. 按 workflows/checklist.md 做最终自检。
7. 无法确认的 clause、Release、CR、TDoc 或会议结论必须标注为“待核验”。
```
