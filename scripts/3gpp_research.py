#!/usr/bin/env python3
"""
Local CLI for evidence-grounded 3GPP agentic research.

This script intentionally uses the Python standard library for the core path:
download -> extract/parse -> index -> search -> verify.

PDF extraction is supported when `pypdf` is installed; otherwise PDFs are
recorded as sources and marked for manual/optional parsing.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import html.parser
import json
import os
import re
import shutil
import sqlite3
import sys
import textwrap
import urllib.parse
import urllib.request
import zipfile
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable
from xml.etree import ElementTree

from docx_track_changes_parser import docx_to_markdown


ROOT = Path(__file__).resolve().parents[1]
TDOC_INCOMING = ROOT / "TDoc" / "_incoming"
TDOC_PROCESSED = ROOT / "TDoc" / "_processed"
TDOC_INDEX = ROOT / "TDoc" / "_index"
DEFAULT_DB = TDOC_INDEX / "research.db"
METADATA_CSV = TDOC_INDEX / "metadata.csv"
TOOL_CONFIG = ROOT / "tools.json"

OFFICIAL_HOSTS = {
    "3gpp.org",
    "www.3gpp.org",
    "ftp.3gpp.org",
    "portal.3gpp.org",
    "portal.etsi.org",
    "www.etsi.org",
}

USER_AGENT = "3gpp-research-kit/0.1 (+https://github.com/second-rate-hall/3gpp-research-kit)"


class LinkParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        for key, value in attrs:
            if key.lower() == "href" and value:
                self.links.append(value)


@dataclass
class DocumentRecord:
    source_id: str
    source_path: str
    processed_path: str
    title: str
    document_type: str
    tdoc_id: str
    spec_id: str
    cr_id: str
    meeting: str
    working_group: str
    company: str
    official_url: str
    sha256: str
    parser: str
    parse_status: str
    notes: str = ""


def ensure_dirs() -> None:
    for path in [TDOC_INCOMING, TDOC_PROCESSED, TDOC_INDEX]:
        path.mkdir(parents=True, exist_ok=True)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_name(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", name.strip())
    return cleaned[:180] or "downloaded"


def is_official_url(url: str) -> bool:
    host = urllib.parse.urlparse(url).netloc.lower()
    if "@" in host:
        host = host.rsplit("@", 1)[-1]
    return any(host == h or host.endswith("." + h) for h in OFFICIAL_HOSTS)


def download_url(url: str, out_dir: Path = TDOC_INCOMING) -> Path:
    ensure_dirs()
    parsed = urllib.parse.urlparse(url)
    name = Path(urllib.parse.unquote(parsed.path)).name or "index.html"
    target = out_dir / safe_name(name)
    print(f"Downloading {url}", file=sys.stderr)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        with target.open("wb") as fh:
            shutil.copyfileobj(response, fh)
    sidecar = target.with_suffix(target.suffix + ".source.json")
    sidecar.write_text(json.dumps({"url": url, "official": is_official_url(url)}, indent=2), encoding="utf-8")
    return target


def read_listing(url: str) -> list[str]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        html = response.read().decode("utf-8", errors="replace")
    parser = LinkParser()
    parser.feed(html)
    return [urllib.parse.urljoin(url.rstrip("/") + "/", link) for link in parser.links]


def spec_archive_url(spec: str) -> str:
    normalized = spec.strip().replace("TS", "").replace("TR", "").replace(" ", "")
    match = re.fullmatch(r"(\d{2})\.?(\d{3})", normalized)
    if not match:
        raise ValueError("spec must look like 38.331 or 38331")
    series, rest = match.groups()
    spec_id = f"{series}.{rest}"
    return f"https://www.3gpp.org/ftp/Specs/archive/{series}_series/{spec_id}/"


def download_spec_archive(spec: str, version: str | None, latest: bool, out_dir: Path = TDOC_INCOMING) -> Path:
    base = spec_archive_url(spec)
    links = [link for link in read_listing(base) if link.lower().endswith(".zip")]
    if not links:
        raise RuntimeError(f"No ZIP files found at {base}")
    if version:
        version_clean = version.lower().replace(".", "")
        candidates = [link for link in links if version_clean in Path(urllib.parse.urlparse(link).path).stem.lower()]
        if not candidates:
            raise RuntimeError(f"No spec ZIP matching version {version!r} at {base}")
        chosen = sorted(candidates)[-1]
    else:
        chosen = sorted(links)[-1] if latest else sorted(links)[0]
    return download_url(chosen, out_dir)


def text_from_docx(path: Path) -> str:
    return docx_to_markdown(path)


def text_from_pdf(path: Path) -> tuple[str, str]:
    try:
        from pypdf import PdfReader  # type: ignore
    except Exception:
        return "", "pdf_parser_missing"
    reader = PdfReader(str(path))
    text = "\n\n".join(page.extract_text() or "" for page in reader.pages)
    return text, "ok"


def text_from_html(path: Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="replace")
    raw = re.sub(r"<script\b[^>]*>.*?</script>", " ", raw, flags=re.I | re.S)
    raw = re.sub(r"<style\b[^>]*>.*?</style>", " ", raw, flags=re.I | re.S)
    raw = re.sub(r"<[^>]+>", " ", raw)
    raw = raw.replace("&nbsp;", " ").replace("&amp;", "&")
    return re.sub(r"\s+\n", "\n", re.sub(r"[ \t]+", " ", raw)).strip()


def classify(path: Path) -> dict[str, str]:
    name = path.name
    lower = name.lower()
    tdoc = re.search(r"\b([RSCGP]\d-\d{6,7})\b", name, flags=re.I)
    spec = re.search(r"\b(?:TS|TR)?\s?(\d{2}\.\d{3})\b", name, flags=re.I)
    compact_spec = re.search(r"\b(\d{2})(\d{3})[-_.]", name, flags=re.I)
    cr = re.search(r"\bCR[_ -]?(\d{3,5})\b", name, flags=re.I)
    doc_type = "unknown"
    if "meeting" in lower and "report" in lower:
        doc_type = "meeting_report"
    elif "cr" in lower or cr:
        doc_type = "cr"
    elif "ls" in lower:
        doc_type = "ls"
    elif tdoc:
        doc_type = "tdoc"
    elif spec or compact_spec:
        doc_type = "spec"
    spec_id = ""
    if spec:
        spec_id = spec.group(1)
    elif compact_spec:
        spec_id = f"{compact_spec.group(1)}.{compact_spec.group(2)}"
    return {
        "tdoc_id": tdoc.group(1).upper() if tdoc else "",
        "spec_id": spec_id,
        "cr_id": cr.group(1) if cr else "",
        "document_type": doc_type,
    }


def source_sidecar_url(path: Path) -> str:
    sidecar = path.with_suffix(path.suffix + ".source.json")
    if sidecar.exists():
        try:
            return json.loads(sidecar.read_text(encoding="utf-8")).get("url", "")
        except Exception:
            return ""
    return ""


def write_processed_text(source: Path, text: str) -> Path:
    rel_hash = hashlib.sha1(str(source).encode("utf-8")).hexdigest()[:10]
    target = TDOC_PROCESSED / f"{source.stem}.{rel_hash}.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    return target


def parse_file(path: Path, inherited_url: str = "") -> list[DocumentRecord]:
    records: list[DocumentRecord] = []
    suffix = path.suffix.lower()
    source_url = source_sidecar_url(path) or inherited_url
    parser = suffix.lstrip(".") or "unknown"
    status = "ok"
    text = ""

    if suffix == ".zip":
        extract_dir = TDOC_PROCESSED / f"{path.stem}.extracted"
        extract_dir.mkdir(parents=True, exist_ok=True)
        nested_records: list[DocumentRecord] = []
        with zipfile.ZipFile(path) as zf:
            for member in zf.namelist():
                if member.endswith("/"):
                    continue
                target = extract_dir / safe_name(member.replace("/", "_"))
                target.write_bytes(zf.read(member))
                nested_records.extend(parse_file(target, source_url))
        return nested_records
    if suffix in {".txt", ".md", ".csv"}:
        text = path.read_text(encoding="utf-8", errors="replace")
    elif suffix == ".docx":
        text = text_from_docx(path)
    elif suffix == ".pdf":
        text, status = text_from_pdf(path)
    elif suffix in {".html", ".htm"}:
        text = text_from_html(path)
    else:
        status = "unsupported"

    processed = write_processed_text(path, text) if text else Path("")
    meta = classify(path)
    title = first_title(text) or path.stem
    records.append(
        DocumentRecord(
            source_id=hashlib.sha1(str(path).encode("utf-8")).hexdigest()[:16],
            source_path=str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path),
            processed_path=str(processed.relative_to(ROOT)) if processed else "",
            title=title,
            document_type=meta["document_type"],
            tdoc_id=meta["tdoc_id"],
            spec_id=meta["spec_id"],
            cr_id=meta["cr_id"],
            meeting=infer_meeting(path),
            working_group=infer_working_group(path),
            company="",
            official_url=source_url,
            sha256=sha256_file(path),
            parser=parser,
            parse_status=status if text or status != "ok" else "empty",
        )
    )
    return records


def first_title(text: str) -> str:
    for line in text.splitlines():
        clean = line.strip().strip("#").strip()
        if 8 <= len(clean) <= 180:
            return clean
    return ""


def infer_meeting(path: Path) -> str:
    match = re.search(r"(TSG[A-Z0-9_ -]*\d{2,3}[A-Za-z-]*)", str(path), flags=re.I)
    return match.group(1) if match else ""


def infer_working_group(path: Path) -> str:
    text = str(path).upper()
    for wg in ["WG1_RAN1", "WG2_RL2", "WG3_IU", "WG4_RAD", "WG5_TEST", "SA2", "SA3", "CT1", "CT3", "RAN"]:
        if wg in text:
            return wg
    return ""


def parse_tree(input_dir: Path = TDOC_INCOMING, metadata_csv: Path = METADATA_CSV) -> list[DocumentRecord]:
    ensure_dirs()
    records: list[DocumentRecord] = []
    for path in sorted(input_dir.rglob("*")):
        if not path.is_file() or path.name.endswith(".source.json") or path.name == ".gitkeep":
            continue
        records.extend(parse_file(path))
    write_metadata(records, metadata_csv)
    return records


def write_metadata(records: list[DocumentRecord], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(asdict(records[0]).keys()) if records else [field.name for field in DocumentRecord.__dataclass_fields__.values()]
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for record in records:
            writer.writerow(asdict(record))


def read_metadata(path: Path = METADATA_CSV) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def chunk_text(text: str, size: int = 1800, overlap: int = 250) -> Iterable[tuple[int, str]]:
    text = re.sub(r"\n{3,}", "\n\n", text)
    if len(text) <= size:
        yield 0, text
        return
    start = 0
    idx = 0
    while start < len(text):
        end = min(len(text), start + size)
        yield idx, text[start:end]
        if end == len(text):
            break
        start = max(0, end - overlap)
        idx += 1


def build_db(metadata_csv: Path = METADATA_CSV, db_path: Path = DEFAULT_DB) -> None:
    ensure_dirs()
    rows = read_metadata(metadata_csv)
    con = sqlite3.connect(db_path)
    con.execute("PRAGMA journal_mode=WAL")
    con.executescript(
        """
        DROP TABLE IF EXISTS chunks_fts;
        DROP TABLE IF EXISTS chunks;
        DROP TABLE IF EXISTS documents;
        DROP TABLE IF EXISTS relations;
        CREATE TABLE documents (
          source_id TEXT PRIMARY KEY,
          source_path TEXT,
          processed_path TEXT,
          title TEXT,
          document_type TEXT,
          tdoc_id TEXT,
          spec_id TEXT,
          cr_id TEXT,
          meeting TEXT,
          working_group TEXT,
          company TEXT,
          official_url TEXT,
          sha256 TEXT,
          parser TEXT,
          parse_status TEXT,
          notes TEXT
        );
        CREATE TABLE chunks (
          chunk_id TEXT PRIMARY KEY,
          source_id TEXT,
          chunk_index INTEGER,
          text TEXT
        );
        CREATE VIRTUAL TABLE chunks_fts USING fts5(text, source_id UNINDEXED, chunk_id UNINDEXED);
        CREATE TABLE relations (
          source_type TEXT,
          source_id TEXT,
          relation TEXT,
          target_type TEXT,
          target_id TEXT,
          evidence_source TEXT,
          confidence TEXT,
          verification_status TEXT
        );
        """
    )
    for row in rows:
        con.execute(
            "INSERT OR REPLACE INTO documents VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            [row.get(k, "") for k in DocumentRecord.__dataclass_fields__.keys()],
        )
        processed = ROOT / row.get("processed_path", "")
        if processed.exists():
            text = processed.read_text(encoding="utf-8", errors="replace")
            for chunk_index, chunk in chunk_text(text):
                chunk_id = f"{row['source_id']}:{chunk_index}"
                con.execute("INSERT INTO chunks VALUES (?,?,?,?)", (chunk_id, row["source_id"], chunk_index, chunk))
                con.execute("INSERT INTO chunks_fts VALUES (?,?,?)", (chunk, row["source_id"], chunk_id))
        add_basic_relations(con, row)
    con.commit()
    con.close()


def add_basic_relations(con: sqlite3.Connection, row: dict[str, str]) -> None:
    source_id = row.get("source_id", "")
    evidence = row.get("official_url") or row.get("source_path", "")
    if source_id and row.get("spec_id"):
        con.execute(
            "INSERT INTO relations VALUES (?,?,?,?,?,?,?,?)",
            ("Document", source_id, "represents", "Specification", row["spec_id"], evidence, "high", "confirmed" if row.get("official_url") else "needs_verification"),
        )
    if row.get("cr_id") and row.get("spec_id"):
        con.execute(
            "INSERT INTO relations VALUES (?,?,?,?,?,?,?,?)",
            ("CR", row["cr_id"], "modifies", "Specification", row["spec_id"], evidence, "low", "needs_verification"),
        )
    if row.get("tdoc_id") and row.get("meeting"):
        con.execute(
            "INSERT INTO relations VALUES (?,?,?,?,?,?,?,?)",
            ("TDoc", row["tdoc_id"], "discussed_in", "Meeting", row["meeting"], evidence, "low", "needs_verification"),
        )
    if row.get("tdoc_id") and source_id:
        con.execute(
            "INSERT INTO relations VALUES (?,?,?,?,?,?,?,?)",
            ("Document", source_id, "carried_by", "TDoc", row["tdoc_id"], evidence, "medium", "needs_verification"),
        )


def search_db(query: str, db_path: Path = DEFAULT_DB, limit: int = 10) -> list[dict[str, str]]:
    return search_db_filtered(query, db_path=db_path, limit=limit)


def fts_query(text: str, match_all: bool = False) -> str:
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9*._-]{1,}|[\u4e00-\u9fff]{2,}", text)
    if not tokens:
        return f'"{text.replace(chr(34), chr(34) * 2)}"'
    operator = " AND " if match_all else " OR "
    return operator.join(f'"{token.replace(chr(34), chr(34) * 2)}"' for token in tokens[:16])


def search_db_filtered(
    query: str,
    db_path: Path = DEFAULT_DB,
    limit: int = 10,
    spec_id: str | None = None,
    match_all: bool = False,
) -> list[dict[str, str]]:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    where = "WHERE chunks_fts MATCH ?"
    params: list[object] = [fts_query(query, match_all=match_all)]
    if spec_id:
        where += " AND documents.spec_id = ?"
        params.append(spec_id)
    params.append(limit)
    rows = con.execute(
        """
        SELECT bm25(chunks_fts) AS score, documents.*, chunks.chunk_index, chunks.text,
               snippet(chunks_fts, 0, '[', ']', '...', 20) AS snippet
        FROM chunks_fts
        JOIN chunks ON chunks_fts.chunk_id = chunks.chunk_id
        JOIN documents ON documents.source_id = chunks.source_id
        {where}
        ORDER BY score
        LIMIT ?
        """.format(where=where),
        params,
    ).fetchall()
    con.close()
    if not rows and match_all:
        return search_db_filtered(query, db_path=db_path, limit=limit, spec_id=spec_id, match_all=False)
    return [dict(row) for row in rows]


def relation_rows(db_path: Path = DEFAULT_DB, limit: int = 50) -> list[dict[str, str]]:
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        """
        SELECT *
        FROM relations
        ORDER BY verification_status, source_type, source_id
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    con.close()
    return [dict(row) for row in rows]


TASK_TYPES = {
    "cr_trace": ["cr", "change request", "reason for change", "修改请求", "变更原因", "溯源"],
    "release_comparison": ["release", "rel-", "rel ", "版本", "对比", "差异", "比较"],
    "company_position": ["company", "公司", "厂商", "立场", "proposal", "contribution"],
    "feature_evolution": ["evolution", "演进", "引入", "背景", "feature", "work item", "wi"],
    "protocol_procedure": ["procedure", "流程", "handover", "re-establishment", "registration", "rrc", "nas"],
    "ambiguity_or_conflict_check": ["ambiguity", "conflict", "歧义", "冲突", "不一致"],
    "test_case_draft": ["test case", "测试用例", "tc"],
}


SPEC_HINTS = [
    ("38.331", ["38.331", "38331", "nr rrc", "5g rrc", "rrcsetup", "rrcreestablishment", "rrc re-establishment"]),
    ("36.331", ["36.331", "36331", "lte rrc", "4g rrc", "rrcconnectionreestablishment"]),
    ("38.300", ["38.300", "38300", "nr overall", "ng-ran", "5g architecture"]),
    ("36.300", ["36.300", "36300", "e-utran", "lte overall", "4g architecture"]),
    ("38.304", ["38.304", "38304", "nr cell selection", "cell reselection", "s-search", "小区选择", "小区重选"]),
    ("36.304", ["36.304", "36304", "e-utra cell selection", "lte cell selection"]),
    ("24.501", ["24.501", "24501", "5g nas", "registration", "pdu session", "amf", "5gc"]),
    ("24.301", ["24.301", "24301", "eps nas", "attach", "tau", "mme", "4g nas"]),
    ("38.413", ["38.413", "38413", "ngap", "n2", "amf"]),
    ("36.413", ["36.413", "36413", "s1ap", "mme"]),
    ("23.501", ["23.501", "23501", "system architecture", "5gs", "5gc", "slicing", "qos"]),
    ("23.502", ["23.502", "23502", "5gs procedure", "service based", "registration procedure"]),
]


def classify_task(question: str) -> str:
    lower = question.lower()
    for task_type, needles in TASK_TYPES.items():
        if any(needle in lower for needle in needles):
            return task_type
    return "clause_explanation" if re.search(r"\b\d+(?:\.\d+){1,4}\b", question) else "general_research"


def infer_specs(question: str, explicit_specs: list[str] | None = None) -> list[str]:
    specs = normalize_specs(explicit_specs or [])
    lower = question.lower()
    for match in re.finditer(r"\b(?:TS|TR)?\s?(\d{2})\.?(\d{3})\b", question, flags=re.I):
        specs.append(f"{match.group(1)}.{match.group(2)}")
    for spec, hints in SPEC_HINTS:
        if any(hint in lower for hint in hints):
            specs.append(spec)
    if ("4g" in lower or "lte" in lower) and "rrc" in lower:
        specs.append("36.331")
    if ("5g" in lower or "nr" in lower) and "rrc" in lower:
        specs.append("38.331")
    return sorted(set(specs))


def normalize_specs(values: list[str]) -> list[str]:
    specs: list[str] = []
    for value in values:
        match = re.search(r"\b(\d{2})\.?(\d{3})\b", str(value))
        if match:
            specs.append(f"{match.group(1)}.{match.group(2)}")
    return sorted(set(specs))


def research_queries(question: str, task_type: str, specs: list[str]) -> list[str]:
    queries = [question]
    lower = question.lower()
    if "rrcsetup" in lower or "rrc setup" in lower:
        queries.extend(["RRCSetup", "RRCSetup fallback", "RRC establishment"])
    if "re-establishment" in lower or "reestablishment" in lower or "重建" in lower:
        queries.extend(
            [
                "RRC re-establishment",
                "RRC connection re-establishment",
                "RRCReestablishmentRequest RRCReestablishment RRCReestablishmentComplete",
                "RRCConnectionReestablishmentRequest RRCConnectionReestablishment RRCConnectionReestablishmentComplete",
                "fallback RRCSetup",
                "valid UE context",
                "AS security activated",
            ]
        )
    if "cell selection" in lower or "小区选择" in question:
        queries.extend(["cell selection", "cell reselection", "suitable cell", "acceptable cell"])
    if "registration" in lower or "注册" in question:
        queries.extend(["registration procedure", "Registration Request", "Registration Accept"])
    if task_type == "cr_trace":
        queries.extend(["reason for change", "change request", "affected clauses"])
    if task_type == "release_comparison":
        queries.extend(["release", "introduced", "modified", "change"])
    for spec in specs:
        queries.append(spec)
    deduped: list[str] = []
    seen: set[str] = set()
    for query in queries:
        cleaned = re.sub(r"\s+", " ", query).strip()
        if cleaned and cleaned.lower() not in seen:
            seen.add(cleaned.lower())
            deduped.append(cleaned)
    return deduped


def evidence_rank(row: dict[str, str]) -> int:
    text = f"{row.get('query', '')} {row.get('title', '')} {row.get('snippet', '')} {row.get('text', '')}".lower()
    score = 0
    for needle, value in {
        "procedure": 15,
        "purpose": 12,
        "shall": 10,
        "rrcsetup": 18,
        "re-establishment": 18,
        "valid ue context": 20,
        "reason for change": 22,
        "change request": 18,
        "meeting report": 18,
        "approved": 12,
        "agreed": 12,
    }.items():
        if needle in text:
            score += value
    if row.get("official_url"):
        score += 20
    if row.get("spec_id"):
        score += 8
    if row.get("tdoc_id") or row.get("cr_id"):
        score += 10
    return score


def collect_research_evidence(question: str, task_type: str, specs: list[str], db_path: Path, limit: int) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    queries = research_queries(question, task_type, specs)
    for query in queries:
        if specs:
            for spec in specs:
                for row in search_db_filtered(query, db_path=db_path, limit=limit, spec_id=spec, match_all=True):
                    row["query"] = query
                    rows.append(row)
        for row in search_db_filtered(query, db_path=db_path, limit=limit, match_all=True):
            row["query"] = query
            rows.append(row)
    deduped: dict[tuple[str, int], dict[str, str]] = {}
    for row in rows:
        key = (str(row.get("source_id", "")), int(row.get("chunk_index", 0)))
        if key not in deduped:
            deduped[key] = row
    return sorted(deduped.values(), key=evidence_rank, reverse=True)[: max(limit * 3, 12)]


def clean_md(value: object, length: int = 260) -> str:
    text = str(value or "").replace("\r", " ").replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace("|", "\\|")
    return text[:length].rstrip() + "..." if len(text) > length else text


def source_type(row: dict[str, str]) -> str:
    doc_type = (row.get("document_type") or "").lower()
    if doc_type == "spec":
        return "TS"
    if doc_type == "cr":
        return "CR"
    if doc_type == "tdoc":
        return "TDoc"
    if doc_type == "meeting_report":
        return "Meeting Report"
    return doc_type or "document"


def evidence_status(row: dict[str, str]) -> str:
    if row.get("official_url") and source_type(row) in {"TS", "TR", "CR", "TDoc", "Meeting Report"}:
        return "confirmed"
    if row.get("official_url"):
        return "evidence-grounded"
    return "needs_verification"


def evidence_claim(row: dict[str, str]) -> str:
    text = f"{row.get('snippet', '')} {row.get('text', '')}".lower()
    spec = row.get("spec_id") or row.get("source_id") or "本地资料"
    if "fallback" in text and "rrc establishment" in text and "successful" in text:
        return f"{spec} 中出现 RRC re-establishment fallback to RRC establishment 的成功路径线索。"
    if "not able to retrieve or verify" in text and "rrcsetup" in text:
        return f"{spec} 中出现网络无法 retrieve/verify UE context 时由 RRCSetup 承接的证据线索。"
    if "valid ue context" in text and "connection re-establishment succeeds" in text:
        return f"{spec} 中出现 connection re-establishment 成功依赖 valid UE context 的证据线索。"
    if "rrcsetup ::=" in text or "network to ue rrcsetup" in text:
        return f"{spec} 中包含 RRCSetup 消息定义，可用于核验 fallback 分支中的消息语义。"
    if "rrcreestablishmentrequest" in text or "rrcconnectionreestablishmentrequest" in text:
        return f"{spec} 中包含 RRC re-establishment 请求/响应消息相关证据。"
    if "reason for change" in text:
        return f"{spec} 中出现 CR reason for change 线索，可用于追踪修改动机。"
    return f"{spec} 中存在与检索问题 `{row.get('query')}` 相关的证据片段。"


def infer_pointer(row: dict[str, str]) -> str:
    text = f"{row.get('snippet', '')} {row.get('text', '')}"
    match = re.search(r"\b(\d+(?:\.\d+){1,4}[a-z]?)\b", text, flags=re.I)
    if match:
        return f"clause_or_nearby_section={match.group(1)}; chunk_index={row.get('chunk_index')}"
    return f"chunk_index={row.get('chunk_index')}"


def report_path_for(question: str, output: str | None) -> Path:
    if output:
        return Path(output)
    runs = ROOT / "research-runs"
    runs.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^A-Za-z0-9\u4e00-\u9fff]+", "-", question).strip("-")[:70] or "research"
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    return runs / f"{stamp}-{slug}.md"


def generate_research_report(
    question: str,
    task_type: str,
    specs: list[str],
    evidence: list[dict[str, str]],
    relations: list[dict[str, str]],
    downloaded: list[str],
) -> str:
    source_rows: dict[str, dict[str, str]] = {}
    for row in evidence:
        source_rows.setdefault(str(row.get("source_id", "")), row)
    source_inventory = list(source_rows.values())
    evidence_ids = {id(row): f"E{idx:03d}" for idx, row in enumerate(evidence, start=1)}
    has_cr_or_tdoc = any(source_type(row) in {"CR", "TDoc", "Meeting Report"} for row in evidence)

    lines = [
        f"# {question} 深度研究报告",
        "",
        "> 本报告由 `3gpp-research-kit research` 生成。它是证据优先的深度研究草案：只把已检索到官方 URL 或本地可追溯来源的内容列为 confirmed/evidence-grounded；CR、TDoc、Meeting Report 覆盖不足时，相关结论保持待核验。",
        "",
        "## 1. 结论摘要",
        "",
    ]
    if evidence:
        lines.extend(
            [
                f"- `evidence-grounded` 本次研究已建立本地 evidence database，并检索到 {len(evidence)} 条候选证据片段；主要候选规范为：{', '.join(specs) if specs else '未由问题自动识别，需人工补充'}。",
                f"- `evidence-grounded` 最高相关证据来自 {clean_md(evidence[0].get('spec_id') or source_type(evidence[0]))}，定位为 `chunk_index={clean_md(evidence[0].get('chunk_index'))}`，应作为人工精读的第一入口。",
                "- `evidence-grounded` 当前报告可以支持资料定位、证据表整理和初步主题分析；最终标准判断仍应回到具体 clause、CR reason for change、TDoc 或 Meeting Report 复核。",
            ]
        )
    else:
        lines.append("- `needs_verification` 本次未检索到足够证据，不能生成 confirmed 标准结论。")
    if not has_cr_or_tdoc:
        lines.append("- `needs_verification` 当前证据集中未覆盖足够 CR、TDoc 或 Meeting Report，不能确认设计动机、会议结论或公司立场。")
    lines.append("- `needs_verification` 如果本问题涉及 Release 演进或规范差异，还需要补充版本 diff 或 CR 级证据。")

    lines.extend(
        [
            "",
            "## 2. 研究范围与问题拆解",
            "",
            f"- 研究问题：{question}",
            f"- 任务类型：{task_type}",
            f"- 候选 TS/TR：{', '.join(specs) if specs else '未自动识别，需要人工指定 `--spec`'}",
            f"- 本次下载动作：{'; '.join(clean_md(item, 180) for item in downloaded) if downloaded else '未下载新资料，复用本地 incoming/index'}",
            "- 覆盖范围：本地 incoming 资料、已解析文本、SQLite FTS 检索库和基础关系表。",
            "- 排除范围：未被下载或导入的 CR/TDoc/Meeting Report、未解析成功的 PDF/扫描件、厂商实现差异和外场日志。",
            "",
            "## 3. 规范依据",
            "",
            "| 功能 / 子问题 | 主要规范或资料 | 作用 | 证据状态 |",
            "| --- | --- | --- | --- |",
        ]
    )
    if source_inventory:
        for row in source_inventory[:10]:
            role = "主要证据" if row.get("spec_id") in specs else "辅助证据"
            status = "evidence-grounded" if evidence_status(row) == "confirmed" else evidence_status(row)
            lines.append(
                f"| {clean_md(row.get('query'), 120)} | {clean_md(row.get('spec_id') or row.get('tdoc_id') or row.get('title'))} | {role} | {status} |"
            )
    else:
        lines.append("| 资料定位 | 待补充 | 当前证据不足 | needs_verification |")

    lines.extend(
        [
            "",
            "## 4. Evidence Table / 证据表",
            "",
            "| id | claim | source_type | source_id | version_or_release | clause_or_section | evidence_summary | quote_or_pointer | status |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for idx, row in enumerate(evidence[:18], start=1):
        eid = f"E{idx:03d}"
        claim = evidence_claim(row)
        source_id = row.get("spec_id") or row.get("tdoc_id") or row.get("cr_id") or row.get("source_id")
        pointer = f"{row.get('official_url') or row.get('source_path')}; {infer_pointer(row)}"
        lines.append(
            f"| {eid} | {clean_md(claim, 220)} | {clean_md(source_type(row))} | {clean_md(source_id)} | 待核验 | {clean_md(infer_pointer(row), 120)} | {clean_md(row.get('snippet') or row.get('text'), 360)} | {clean_md(pointer, 360)} | {evidence_status(row)} |"
        )

    lines.extend(
        [
            "",
            "## 5. 分主题分析",
            "",
            "### 5.1 直接证据解读",
            "",
        ]
    )
    if evidence:
        for idx, row in enumerate(evidence[:6], start=1):
            lines.append(
                f"- E{idx:03d}: {clean_md(evidence_claim(row), 240)} 该线索来自 `{clean_md(row.get('spec_id') or row.get('source_id'))}`，定位为 `{clean_md(infer_pointer(row), 120)}`。"
            )
    else:
        lines.append("- 当前无足够证据，不能做直接证据解读。")

    lines.extend(
        [
            "",
            "### 5.2 资料覆盖度",
            "",
        ]
    )
    if source_inventory:
        for row in source_inventory[:8]:
            eid = next((evidence_ids[id(item)] for item in evidence if item.get("source_id") == row.get("source_id")), "")
            lines.append(
                f"- {eid}: `{clean_md(row.get('spec_id') or row.get('tdoc_id') or row.get('source_id'))}` 提供了与 `{clean_md(row.get('query'), 100)}` 相关的证据入口；证据表状态见第 4 节。"
            )
    else:
        lines.append("- 当前资料覆盖不足，需要先补充 TS/TR、CR、TDoc 或 Meeting Report。")

    lines.extend(["", "### 5.3 标准事实与解释边界", ""])
    lines.append("- 标准事实只能来自 Evidence Table 中可追溯的来源；本报告不把未定位到 clause/CR/TDoc 的内容写成最终结论。")
    lines.append("- 检索片段可用于定位精读范围，但 chunk 命中不等于完整 clause 解释；专业交付前应回到原文上下文复核。")
    if has_cr_or_tdoc:
        lines.append("- 当前证据中已出现 CR/TDoc/Meeting 类型材料，可继续追踪 reason for change、会议状态和关联规范修改。")
    else:
        lines.append("- 当前证据尚未充分覆盖 CR/TDoc/Meeting Report，因此设计动机、公司立场和会议结论均保持待核验。")

    lines.extend(
        [
            "",
            "### 5.4 关系线索",
            "",
            "| source_type | source_id | relation | target_type | target_id | status |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    if relations:
        for row in relations[:12]:
            relation_status = row.get("verification_status")
            if relation_status == "confirmed":
                relation_status = "evidence-grounded"
            lines.append(
                f"| {clean_md(row.get('source_type'))} | {clean_md(row.get('source_id'))} | {clean_md(row.get('relation'))} | {clean_md(row.get('target_type'))} | {clean_md(row.get('target_id'))} | {clean_md(relation_status)} |"
            )
    else:
        lines.append("| 待补充 | 待补充 | 待补充 | 待补充 | 待补充 | needs_verification |")

    lines.extend(
        [
            "",
            "## 6. 对比矩阵",
            "",
            "| axis | A evidence | B evidence | similarity | difference | status |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    if len(specs) >= 2:
        for axis in ["资料覆盖", "过程/消息证据", "版本或系统差异", "待核验项"]:
            a = next((row for row in evidence if row.get("spec_id") == specs[0]), {})
            b = next((row for row in evidence if row.get("spec_id") == specs[1]), {})
            lines.append(
                f"| {axis} | {clean_md(a.get('snippet') or a.get('title'), 220)} | {clean_md(b.get('snippet') or b.get('title'), 220)} | 均需回到官方原文核验。 | 当前仅比较检索命中，不替代 clause 级差异分析。 | evidence-grounded |"
            )
    else:
        lines.append("| 单资料范围 | 当前主要是单规范/单主题证据定位 | 待补充第二组资料 | 不适用 | 如需对比，请补充 `--spec` 或 Release/CR 范围 | needs_verification |")

    lines.extend(
        [
            "",
            "## 7. 图示",
            "",
            "```mermaid",
            "flowchart TD",
            "  A[\"Research question\"] --> B[\"Infer task type and candidate specs\"]",
            "  B --> C[\"Fetch or reuse official materials\"]",
            "  C --> D[\"Parse and build SQLite FTS\"]",
            "  D --> E[\"Retrieve evidence snippets\"]",
            "  E --> F[\"Build evidence table\"]",
            "  F --> G[\"List verification gaps\"]",
            "```",
            "",
            "## 8. 常见误区和边界澄清",
            "",
            "- 不要把 FTS 命中的片段直接等同于完整 clause 结论。",
            "- 不要把 TS/TR 的最终文本、CR 的修改理由、TDoc 的会议贡献和 Meeting Report 的会议结论混为一类证据。",
            "- 如果 DOCX 来自 CR/TDoc，应保留 Word 修订模式中的新增/删除标记，避免把删除内容当作当前有效条文。",
            "- 第三方网页、专利背景或模型总结只能作为辅助入口，不能替代 3GPP 官方来源。",
            "",
            "## 9. 未确认点与后续核验建议",
            "",
            "| 未确认点 | 为什么未确认 | 后续应查 |",
            "| --- | --- | --- |",
            "| clause 级定位 | 当前自动报告使用 chunk_index，未保证抽取到完整 clause 边界 | 回到 processed 文本或官方 DOCX，补充 clause 编号和原文上下文 |",
            "| CR / TDoc / Meeting Report 溯源 | 本地检索未必覆盖相关会议资料 | 查询 3GPP Portal、FTP Docs 目录和 Meeting Report |",
            "| Release 差异 | 未自动完成版本间 diff | 下载目标版本 archive，进行 clause diff 和 CR trace |",
            "| 工程影响 | 标准文本不能直接代表具体实现行为 | 结合实现文档、日志、测试规范和专家复核 |",
            "",
            "## 10. 可复用总结",
            "",
            f"本次研究围绕“{question}”建立了可复核的本地证据链。当前最可靠的结论是：已定位到候选规范/资料和证据片段，但任何涉及设计动机、Release 演进、CR 原因、会议结论或公司立场的判断，都需要继续补充 CR、TDoc 和 Meeting Report 后才能从 `needs_verification` 升级为 `confirmed`。这份报告适合作为专业读者继续精读官方原文和补充证据的工作底稿。",
        ]
    )
    return "\n".join(lines) + "\n"


def run_deep_research(args: argparse.Namespace) -> dict[str, object]:
    input_dir = Path(args.input)
    metadata = Path(args.metadata)
    db_path = Path(args.db)
    task_type = classify_task(args.question)
    specs = infer_specs(args.question, args.spec)
    downloaded: list[str] = []
    if not args.no_fetch:
        for spec in specs:
            try:
                downloaded.append(str(download_spec_archive(spec, args.version, args.latest, input_dir)))
            except Exception as exc:
                downloaded.append(f"FAILED {spec}: {exc}")
    records = parse_tree(input_dir, metadata)
    build_db(metadata, db_path)
    evidence = collect_research_evidence(args.question, task_type, specs, db_path, args.limit)
    relation_data = relation_rows(db_path, limit=40)
    report = generate_research_report(args.question, task_type, specs, evidence, relation_data, downloaded)
    output = report_path_for(args.question, args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(report, encoding="utf-8")
    verification_exit = verify_evidence(output)
    return {
        "question": args.question,
        "task_type": task_type,
        "specs": specs,
        "downloaded": downloaded,
        "parsed_records": len(records),
        "evidence_count": len(evidence),
        "relations_count": len(relation_data),
        "report": str(output),
        "verification_exit": verification_exit,
    }


def load_tool_config(path: Path = TOOL_CONFIG) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def check_tools(path: Path = TOOL_CONFIG) -> list[dict[str, str]]:
    config = load_tool_config(path)
    results: list[dict[str, str]] = []
    for name, spec in config.items():
        command = spec.get("command", "")
        executable = command.split()[0] if command else ""
        found = shutil.which(executable) if executable else None
        results.append(
            {
                "tool": name,
                "type": spec.get("type", ""),
                "command": command,
                "status": "available" if found else "missing",
                "path": found or "",
            }
        )
    return results


def run_tool(name: str, args: list[str], path: Path = TOOL_CONFIG) -> int:
    import subprocess

    config = load_tool_config(path)
    if name not in config:
        print(f"Unknown tool {name!r}. Add it to {path}.", file=sys.stderr)
        return 2
    command = config[name].get("command", "")
    if not command:
        print(f"Tool {name!r} has no command.", file=sys.stderr)
        return 2
    full_command = command.split() + args
    print(f"Running external tool: {' '.join(full_command)}", file=sys.stderr)
    completed = subprocess.run(full_command, cwd=ROOT)
    return completed.returncode


def verify_evidence(path: Path) -> int:
    text = path.read_text(encoding="utf-8", errors="replace")
    issues = 0
    official_markers = ["3gpp.org", "portal.3gpp.org", "ftp", "TS ", "TR ", "CR", "TDoc", "Meeting Report", "Forge", "ETSI"]
    official_source_types = {"ts", "tr", "cr", "tdoc", "meeting report", "portal", "ftp", "forge", "etsi", "3gpp", "official"}
    table_header: list[str] = []
    for i, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("|") and "status" in stripped.lower() and "---" not in stripped:
            table_header = [cell.strip().lower().replace("`", "") for cell in stripped.strip("|").split("|")]
            continue
        if stripped.startswith("|") and "confirmed" in stripped.lower() and table_header:
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            row = {table_header[idx]: cells[idx] if idx < len(cells) else "" for idx in range(len(table_header))}
            source_type = row.get("source_type", "").lower()
            row_text = " ".join(cells)
            if source_type and source_type not in official_source_types:
                print(f"{path}:{i}: confirmed evidence row uses non-official source_type={source_type!r}")
                issues += 1
            if not any(marker in row_text for marker in official_markers):
                print(f"{path}:{i}: confirmed evidence row lacks obvious official source marker")
                issues += 1
            continue
        if re.search(r"\b(confirmed|已确认)\b", line, flags=re.I):
            if not any(marker in line for marker in official_markers):
                print(f"{path}:{i}: confirmed claim lacks obvious official marker")
                issues += 1
    if issues == 0:
        print("No obvious verification issues found.")
    return 1 if issues else 0


def cmd_fetch(args: argparse.Namespace) -> None:
    target = download_url(args.url, Path(args.out))
    print(target)


def cmd_fetch_list(args: argparse.Namespace) -> None:
    urls = [
        line.strip()
        for line in Path(args.file).read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    targets = []
    for url in urls:
        targets.append(str(download_url(url, Path(args.out))))
    print(json.dumps(targets, ensure_ascii=False, indent=2))


def cmd_fetch_spec(args: argparse.Namespace) -> None:
    target = download_spec_archive(args.spec, args.version, args.latest, Path(args.out))
    print(target)


def cmd_parse(args: argparse.Namespace) -> None:
    records = parse_tree(Path(args.input), Path(args.metadata))
    print(f"Parsed {len(records)} records -> {args.metadata}")


def cmd_build_db(args: argparse.Namespace) -> None:
    build_db(Path(args.metadata), Path(args.db))
    print(f"Built SQLite FTS database -> {args.db}")


def cmd_search(args: argparse.Namespace) -> None:
    rows = search_db(args.query, Path(args.db), args.limit)
    print(json.dumps(rows, ensure_ascii=False, indent=2))


def cmd_relations(args: argparse.Namespace) -> None:
    rows = relation_rows(Path(args.db), args.limit)
    print(json.dumps(rows, ensure_ascii=False, indent=2))


def cmd_check_tools(args: argparse.Namespace) -> None:
    rows = check_tools(Path(args.config))
    print(json.dumps(rows, ensure_ascii=False, indent=2))


def cmd_run_tool(args: argparse.Namespace) -> None:
    raise SystemExit(run_tool(args.name, args.args, Path(args.config)))


def cmd_verify(args: argparse.Namespace) -> None:
    raise SystemExit(verify_evidence(Path(args.file)))


def cmd_research(args: argparse.Namespace) -> None:
    result = run_deep_research(args)
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else f"Report written -> {result['report']}")
    if int(result["verification_exit"]) != 0:
        raise SystemExit(int(result["verification_exit"]))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download, parse, index, search, and verify 3GPP research evidence.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """
            Examples:
              python scripts/3gpp_research.py fetch-spec --spec 38.331 --latest
              python scripts/3gpp_research.py fetch --url https://www.3gpp.org/ftp/tsg_ran/WG2_RL2/TSGR2_104/Docs/R2-1817862.zip
              python scripts/3gpp_research.py fetch-list --file urls.txt
              python scripts/3gpp_research.py parse
              python scripts/3gpp_research.py build-db
              python scripts/3gpp_research.py search "RRCSetup fallback"
              python scripts/3gpp_research.py research "请分析 RRCSetup 在 RRC re-establishment fallback 场景中的作用" --spec 38.331
            """
        ),
    )
    sub = parser.add_subparsers(required=True)

    fetch = sub.add_parser("fetch", help="Download an official URL into TDoc/_incoming")
    fetch.add_argument("--url", required=True)
    fetch.add_argument("--out", default=str(TDOC_INCOMING))
    fetch.set_defaults(func=cmd_fetch)

    fetch_list = sub.add_parser("fetch-list", help="Download official URLs listed in a text file")
    fetch_list.add_argument("--file", required=True, help="Text file with one URL per line")
    fetch_list.add_argument("--out", default=str(TDOC_INCOMING))
    fetch_list.set_defaults(func=cmd_fetch_list)

    fetch_spec = sub.add_parser("fetch-spec", help="Download a ZIP from the official 3GPP Specs archive")
    fetch_spec.add_argument("--spec", required=True, help="Spec id, e.g. 38.331")
    fetch_spec.add_argument("--version", help="Optional archive version token, e.g. i20 or 18.2.0 if present in filename")
    fetch_spec.add_argument("--latest", action="store_true", help="Download the lexically latest archive ZIP")
    fetch_spec.add_argument("--out", default=str(TDOC_INCOMING))
    fetch_spec.set_defaults(func=cmd_fetch_spec)

    parse_cmd = sub.add_parser("parse", help="Parse incoming files and write metadata")
    parse_cmd.add_argument("--input", default=str(TDOC_INCOMING))
    parse_cmd.add_argument("--metadata", default=str(METADATA_CSV))
    parse_cmd.set_defaults(func=cmd_parse)

    db = sub.add_parser("build-db", help="Build SQLite FTS and relation tables")
    db.add_argument("--metadata", default=str(METADATA_CSV))
    db.add_argument("--db", default=str(DEFAULT_DB))
    db.set_defaults(func=cmd_build_db)

    search = sub.add_parser("search", help="Search the local SQLite FTS RAG database")
    search.add_argument("query")
    search.add_argument("--db", default=str(DEFAULT_DB))
    search.add_argument("--limit", type=int, default=10)
    search.set_defaults(func=cmd_search)

    relations = sub.add_parser("relations", help="Show the local GraphRAG-style relation table")
    relations.add_argument("--db", default=str(DEFAULT_DB))
    relations.add_argument("--limit", type=int, default=50)
    relations.set_defaults(func=cmd_relations)

    check_tools_cmd = sub.add_parser("check-tools", help="Check configured external tools")
    check_tools_cmd.add_argument("--config", default=str(TOOL_CONFIG))
    check_tools_cmd.set_defaults(func=cmd_check_tools)

    run_tool_cmd = sub.add_parser("run-tool", help="Run a configured external tool")
    run_tool_cmd.add_argument("name")
    run_tool_cmd.add_argument("args", nargs=argparse.REMAINDER)
    run_tool_cmd.add_argument("--config", default=str(TOOL_CONFIG))
    run_tool_cmd.set_defaults(func=cmd_run_tool)

    verify = sub.add_parser("verify", help="Check a report/evidence file for obvious ungrounded confirmed claims")
    verify.add_argument("file")
    verify.set_defaults(func=cmd_verify)

    research = sub.add_parser("research", help="Run one-click evidence-grounded deep research and write a report")
    research.add_argument("question", help="Research question or topic")
    research.add_argument("--spec", action="append", default=[], help="Candidate TS/TR spec id, e.g. 38.331. Can be repeated.")
    research.add_argument("--version", help="Optional archive version token when fetching specs")
    research.add_argument("--latest", action="store_true", help="Fetch the lexically latest archive for inferred/explicit specs")
    research.add_argument("--no-fetch", action="store_true", help="Reuse local incoming/index materials without downloading specs")
    research.add_argument("--input", default=str(TDOC_INCOMING), help="Incoming source directory")
    research.add_argument("--metadata", default=str(METADATA_CSV), help="Metadata CSV path")
    research.add_argument("--db", default=str(DEFAULT_DB), help="SQLite FTS database path")
    research.add_argument("--limit", type=int, default=8, help="Search limit per query/spec")
    research.add_argument("--output", help="Output report path. Defaults to research-runs/<timestamp>-<slug>.md")
    research.add_argument("--json", action="store_true", help="Print machine-readable run summary")
    research.set_defaults(func=cmd_research)

    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
