# Patent MCP Server

`patent-mcp-server.py` is a lightweight local tool for reverse-inferencing feature pain points from patent background text.

Use it when a 3GPP feature name is hard to interpret from standards text alone, for example CHO, RedCap, NTN, sidelink relay, or power-saving features.

## Tools

- `search_patents`: search Google Patents by keyword.
- `fetch_patent_background`: fetch a patent page and extract the Background/description text.

## Example

```powershell
@'
{"method":"tools/list"}
{"method":"tools/call","params":{"name":"search_patents","arguments":{"query":"3GPP RedCap reduced capability UE background","limit":3}}}
'@ | python mcp\patent-mcp-server.py
```

## Evidence Rule

Patent background is **auxiliary pain-point evidence**, not official 3GPP standards evidence.

Reports must label patent-derived claims as `auxiliary_background` or `inference`, and must not mark them as `confirmed` unless they are separately verified by TS/TR, CR, TDoc, Meeting Report, or official 3GPP/ETSI/GSMA source.
