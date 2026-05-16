#!/usr/bin/env python3
"""Parse DOCX track changes into evidence-safe Markdown.

3GPP CRs and TDocs often keep Word Track Changes. A naive DOCX text extractor
can mix inserted and deleted text, which is dangerous for standards research.
This parser reads WordprocessingML directly and emits Git-diff-like Markdown:

  unchanged text
  + inserted text
  - deleted text

It intentionally uses only the Python standard library. `python-docx` is useful
for normal document editing, but it does not reliably expose deleted text.
"""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
TEXT_TAGS = {f"{{{W_NS}}}t", f"{{{W_NS}}}delText"}
PARA_TAG = f"{{{W_NS}}}p"
TABLE_TAG = f"{{{W_NS}}}tbl"
INS_TAG = f"{{{W_NS}}}ins"
DEL_TAG = f"{{{W_NS}}}del"
TAB_TAG = f"{{{W_NS}}}tab"
BR_TAG = f"{{{W_NS}}}br"


@dataclass
class TrackStats:
    inserted_segments: int = 0
    deleted_segments: int = 0
    paragraphs: int = 0


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def clean_text(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def merge_segments(segments: list[tuple[str, str]]) -> list[tuple[str, str]]:
    merged: list[tuple[str, str]] = []
    for status, text in segments:
        if not text:
            continue
        if merged and merged[-1][0] == status:
            merged[-1] = (status, merged[-1][1] + text)
        else:
            merged.append((status, text))
    return [(status, clean_text(text)) for status, text in merged if clean_text(text)]


def collect_segments(node: ElementTree.Element, status: str = "normal") -> list[tuple[str, str]]:
    current = status
    if node.tag == INS_TAG:
        current = "inserted"
    elif node.tag == DEL_TAG:
        current = "deleted"

    segments: list[tuple[str, str]] = []
    if node.tag in TEXT_TAGS and node.text:
        text_status = "deleted" if node.tag.endswith("}delText") else current
        segments.append((text_status, node.text))
    elif node.tag == TAB_TAG:
        segments.append((current, "\t"))
    elif node.tag == BR_TAG:
        segments.append((current, "\n"))

    for child in list(node):
        segments.extend(collect_segments(child, current))
        if child.tail:
            segments.append((current, child.tail))
    return merge_segments(segments)


def paragraph_to_markdown(paragraph: ElementTree.Element, stats: TrackStats) -> str:
    stats.paragraphs += 1
    lines: list[str] = []
    for status, text in collect_segments(paragraph):
        if status == "inserted":
            stats.inserted_segments += 1
            lines.append(f"+ {text}")
        elif status == "deleted":
            stats.deleted_segments += 1
            lines.append(f"- {text}")
        else:
            lines.append(text)
    return "\n".join(lines)


def iter_content_blocks(root: ElementTree.Element) -> list[ElementTree.Element]:
    blocks: list[ElementTree.Element] = []
    for node in root.iter():
        if node.tag == PARA_TAG:
            blocks.append(node)
        elif node.tag == TABLE_TAG:
            # Table paragraphs are also yielded by root.iter(); this marker keeps
            # table boundaries visible without duplicating cell extraction logic.
            pass
    return blocks


def parse_docx_track_changes(path: Path) -> tuple[str, TrackStats]:
    stats = TrackStats()
    parts: list[str] = []
    with zipfile.ZipFile(path) as zf:
        names = [n for n in zf.namelist() if n.startswith("word/") and n.endswith(".xml")]
        xml_names = ["word/document.xml"] + [n for n in names if n != "word/document.xml"]
        for name in xml_names:
            if name not in zf.namelist():
                continue
            try:
                root = ElementTree.fromstring(zf.read(name))
            except ElementTree.ParseError:
                continue
            blocks: list[str] = []
            for paragraph in iter_content_blocks(root):
                rendered = paragraph_to_markdown(paragraph, stats)
                if rendered:
                    blocks.append(rendered)
            if blocks:
                parts.append(f"<!-- DOCX part: {name} -->\n\n" + "\n\n".join(blocks))
    return "\n\n".join(parts).strip(), stats


def docx_to_markdown(path: Path) -> str:
    text, stats = parse_docx_track_changes(path)
    header = [
        "<!-- 3GPP DOCX track-changes aware extraction -->",
        f"<!-- inserted_segments={stats.inserted_segments}; deleted_segments={stats.deleted_segments}; paragraphs={stats.paragraphs} -->",
        "<!-- Lines beginning with '+' are Word insertions; '-' are Word deletions. Do not treat deleted text as current standard text. -->",
        "",
    ]
    return "\n".join(header) + text


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert DOCX track changes to Git-diff-like Markdown.")
    parser.add_argument("docx")
    parser.add_argument("--out", help="Output Markdown path. Defaults to stdout.")
    args = parser.parse_args()

    markdown = docx_to_markdown(Path(args.docx))
    if args.out:
        Path(args.out).write_text(markdown, encoding="utf-8")
    else:
        sys.stdout.buffer.write(markdown.encode("utf-8"))
        sys.stdout.buffer.write(b"\n")


if __name__ == "__main__":
    main()
