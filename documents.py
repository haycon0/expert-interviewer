"""Reading uploaded case documents and preparing them for the agents.

Supported: .txt, .md, .csv, .json, .pdf, .docx. Text is extracted once on upload;
the agents only ever see plain text.
"""

import csv
import io
import re
import zipfile
from pathlib import PurePath
from xml.etree import ElementTree

TEXT_TYPES = {".txt", ".md", ".csv", ".json"}
SUPPORTED = TEXT_TYPES | {".pdf", ".docx"}

MAX_STORED_CHARS = 2_000_000  # per document, to keep sessions a sane size
CONTEXT_LIMIT = 60_000        # characters (~15K tokens) of all kept documents given to the agents

_W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def extract_text(name: str, data: bytes) -> tuple[str, str]:
    """Return (kind, text). Text is empty when nothing readable was found."""
    ext = PurePath(name).suffix.lower()
    if ext not in SUPPORTED:
        return "unsupported", ""
    try:
        if ext in TEXT_TYPES:
            text = data.decode("utf-8-sig", errors="replace")
        elif ext == ".pdf":
            from pypdf import PdfReader

            reader = PdfReader(io.BytesIO(data))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        else:  # .docx
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                root = ElementTree.fromstring(z.read("word/document.xml"))
            text = "\n".join(
                "".join(t.text or "" for t in p.iter(f"{_W}t")) for p in root.iter(f"{_W}p")
            )
    except Exception:
        return ext.lstrip("."), ""
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return ext.lstrip("."), text[:MAX_STORED_CHARS]


def witness_excerpt(text: str, expert_name: str, limit: int) -> tuple[str, bool]:
    """Fit a document into `limit` characters, preferring the parts that mention the witness.

    CSV files (like an events log) are filtered row by row; other text line by line.
    Returns (excerpt, trimmed).
    """
    if len(text) <= limit:
        return text, False
    surname = expert_name.split()[-1].lower() if expert_name.split() else ""
    rows = list(csv.reader(io.StringIO(text)))
    if len(rows) > 1 and len(rows[0]) > 1:
        hits = [r for r in rows[1:] if surname and surname in " ".join(r).lower()]
        out = io.StringIO()
        csv.writer(out).writerows([rows[0], *hits])
        excerpt = out.getvalue() if hits else ""
    else:
        excerpt = "\n".join(l for l in text.splitlines() if surname and surname in l.lower())
    return (excerpt or text)[:limit], True


def build_context(docs: list[dict], expert_name: str) -> tuple[str, list[dict]]:
    """Combine kept documents into one block for the witness, criteria and grader agents.

    The character budget is shared evenly; a document that needs less frees room for
    the others. Returns (context, per-document notes on how much was included).
    """
    remaining = CONTEXT_LIMIT
    parts, notes = [], []
    ordered = sorted(docs, key=lambda d: len(d["text"]))  # small ones first so they fit whole
    for i, d in enumerate(ordered):
        share = remaining // (len(ordered) - i)
        excerpt, trimmed = witness_excerpt(d["text"], expert_name, share)
        remaining -= len(excerpt)
        parts.append((d, excerpt))
        notes.append({"id": d["id"], "included_chars": len(excerpt), "trimmed": trimmed})
    by_id = {d["id"]: e for d, e in parts}
    context = "\n\n".join(
        f"=== Document {n}: {d['name']} ===\n{by_id[d['id']]}" for n, d in enumerate(docs, 1)
    )
    return context, notes
