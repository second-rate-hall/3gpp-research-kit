# External Skills

本文件记录可选外部 skill。它们不是本项目运行的硬依赖，但可以增强现成 Agent 的领域分析口径和深度研究流程。

## 3GPP 领域分析口径

```bash
npx skills add lugasia/3gpp-skill@3gpp-expert
```

用途：

- 补充 TS / TR / CR / TDoc / Meeting Report 的阅读顺序。
- 强化标准资料层级、证据链格式和可追溯要求。
- 帮助 Agent 避免把 TDoc、CR、TS/TR 和 Meeting Report 混为同一层级。

## 通用深度研究流程

```bash
npx skills add parcadei/continuous-claude-v3@research-agent
```

用途：

- 提供问题拆解、资料搜索、交叉验证和报告生成的通用流程。
- 用于复杂专题研究时的执行节奏控制。

## 组合方式

实际执行 3GPP 研究时，Agent 应合并使用：

```text
3GPP 领域 skill
+ 通用 research skill
+ 本项目 skills/3gpp-research-kit/SKILL.md
+ workflows/tool-routing.md
```

领域 skill 约束“怎么读 3GPP”，research skill 约束“怎么做深度研究”，本项目 workflow 约束“怎么记录证据和产出报告”。
