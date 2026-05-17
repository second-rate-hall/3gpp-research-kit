# Online Search Playbook

当 `TDoc/_incoming/` 和 `TDoc/_index/` 中没有足够资料时，Codex / Claude CLI 应按本文件执行在线资料发现。在线搜索的目标不是直接生成结论，而是找到可下载、可解析、可引用的官方或准官方来源。

## 搜索优先级

1. 3GPP Specs Archive：下载 TS/TR ZIP。
2. 3GPP FTP：下载会议目录、TDoc ZIP、Meeting Report。
3. 3GPP Portal：查询 CR、TDoc、会议、Work Item、版本状态。
4. 3GPP DynaReport / Work Plan：确认规范、Release 和 Work Item 背景。
5. ETSI 3GPP specification pages：辅助确认规范入口和版本。
6. Google Patents / Espacenet：只用于专利背景与痛点反推。
7. 第三方网页：只能作为线索，不能作为最终证据。

## 基本流程

```text
研究目标
-> 提取关键词、候选 spec、release、feature、TDoc/CR 编号
-> 按 sources/search-recipes.json 生成搜索式
-> 优先下载官方 ZIP / DOCX / PDF / HTML
-> 写入 TDoc/_incoming/
-> 运行 parse 和 build-db
-> 将在线来源写入 evidence package
```

## 状态规则

- 3GPP / ETSI 官方来源可以进入 `confirmed` 或 `evidence-grounded`。
- Portal / FTP 查询到的 CR、TDoc、Meeting Report 应保留 URL、编号、会议、版本。
- 专利背景必须标注为 `auxiliary_background` 或 `inference`。
- 普通网页只能作为 `needs_official_verification`。

## Codex 执行要求

- 搜索式和命中结果应记录到 `research-runs/<topic>/source-discovery.md`。
- 下载文件必须保存到 `TDoc/_incoming/` 或本次 run 目录下。
- 报告中的关键结论不得只引用搜索摘要，必须回到下载后的官方资料或 Portal/FTP 页面。
