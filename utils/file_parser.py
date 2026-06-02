# -*- coding: utf-8 -*-
"""Robust multi-format file parser for AOAA.
Supports: txt, md, pdf, doc, docx, json, jsonl, csv, tsv, xlsx, xls,
          html, xml, yaml, wos.txt, ris, bib
Output: {"text": str, "success": bool, "format": str, "error": str|None, "metadata": dict}
"""

import os
import re
import io
import json
import traceback
from typing import Dict, Any, List

from utils.logger import log_info, log_warn, log_error

CHUNK_SIZE = 10 * 1024 * 1024  # 10MB


def _detect_encoding(raw_bytes: bytes) -> str:
    """Detect encoding with chardet/charset-normalizer fallback."""
    try:
        import chardet
        result = chardet.detect(raw_bytes[:50000])
        if result and result.get("encoding"):
            return result["encoding"]
    except ImportError:
        pass
    try:
        from charset_normalizer import from_bytes
        result = from_bytes(raw_bytes[:50000]).best()
        if result:
            return str(result.encoding)
    except ImportError:
        pass
    return "utf-8"


def _safe_decode(raw_bytes: bytes) -> str:
    """Decode bytes with encoding detection and fallbacks."""
    for enc in ["utf-8", "utf-8-sig"]:
        try:
            return raw_bytes.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    detected = _detect_encoding(raw_bytes)
    try:
        return raw_bytes.decode(detected)
    except (UnicodeDecodeError, LookupError):
        return raw_bytes.decode("utf-8", errors="replace")


def _make_result(text="", success=True, fmt="", error=None, metadata=None) -> Dict[str, Any]:
    return {
        "text": text,
        "success": success,
        "format": fmt,
        "error": error,
        "metadata": metadata or {}
    }


def parse_txt(data: bytes, filename: str) -> Dict[str, Any]:
    """Parse plain text / markdown."""
    text = _safe_decode(data)
    fmt = "md" if filename.lower().endswith(".md") else "txt"
    return _make_result(text=text, fmt=fmt)


def parse_pdf(data: bytes, filename: str) -> Dict[str, Any]:
    """Parse PDF with triple fallback: fitz -> pdfplumber -> PyPDF2."""
    text = ""
    # Try PyMuPDF/fitz
    try:
        import fitz
        doc = fitz.open(stream=data, filetype="pdf")
        pages = []
        for page in doc:
            pages.append(page.get_text())
        text = "\n".join(pages)
        doc.close()
        if text.strip():
            return _make_result(text=text, fmt="pdf")
    except Exception as e:
        log_warn(f"fitz failed for {filename}: {e}")

    # Try pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            pages = []
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    pages.append(t)
            text = "\n".join(pages)
        if text.strip():
            return _make_result(text=text, fmt="pdf")
    except Exception as e:
        log_warn(f"pdfplumber failed for {filename}: {e}")

    # Try PyPDF2
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(io.BytesIO(data))
        pages = []
        for page in reader.pages:
            t = page.extract_text()
            if t:
                pages.append(t)
        text = "\n".join(pages)
        if text.strip():
            return _make_result(text=text, fmt="pdf")
    except Exception as e:
        log_warn(f"PyPDF2 failed for {filename}: {e}")

    if text.strip():
        return _make_result(text=text, fmt="pdf")
    return _make_result(text="", success=False, fmt="pdf", error="All PDF parsers failed")


def parse_docx(data: bytes, filename: str) -> Dict[str, Any]:
    """Parse docx with python-docx."""
    try:
        from docx import Document
        doc = Document(io.BytesIO(data))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        text = "\n".join(paragraphs)
        return _make_result(text=text, fmt="docx")
    except Exception as e:
        log_warn(f"python-docx failed for {filename}: {e}")
        return _make_result(text="", success=False, fmt="docx", error=str(e))


def parse_doc(data: bytes, filename: str) -> Dict[str, Any]:
    """Parse .doc - try textract if available, else fail gracefully."""
    try:
        import textract
        text = textract.process(io.BytesIO(data)).decode("utf-8", errors="replace")
        return _make_result(text=text, fmt="doc")
    except ImportError:
        return _make_result(
            text=_safe_decode(data),
            success=False,
            fmt="doc",
            error="textract not installed; extracted raw text as fallback"
        )
    except Exception as e:
        return _make_result(text="", success=False, fmt="doc", error=str(e))


def parse_excel(data: bytes, filename: str) -> Dict[str, Any]:
    """Parse xlsx/xls with pandas."""
    try:
        import pandas as pd
        ext = os.path.splitext(filename)[1].lower()
        engine = "openpyxl" if ext == ".xlsx" else None
        df = pd.read_excel(io.BytesIO(data), engine=engine)
        text = df.to_string(index=False)
        metadata = {"columns": list(df.columns), "rows": len(df)}
        return _make_result(text=text, fmt="xlsx", metadata=metadata)
    except Exception as e:
        return _make_result(text="", success=False, fmt="xlsx", error=str(e))


def parse_csv_tsv(data: bytes, filename: str) -> Dict[str, Any]:
    """Parse CSV/TSV."""
    try:
        import pandas as pd
        text_str = _safe_decode(data)
        sep = "\t" if filename.lower().endswith(".tsv") else ","
        df = pd.read_csv(io.StringIO(text_str), sep=sep, on_bad_lines="skip")
        text = df.to_string(index=False)
        metadata = {"columns": list(df.columns), "rows": len(df)}
        fmt = "tsv" if sep == "\t" else "csv"
        return _make_result(text=text, fmt=fmt, metadata=metadata)
    except Exception as e:
        text_str = _safe_decode(data)
        return _make_result(text=text_str, success=False, fmt="csv", error=str(e))


def parse_json(data: bytes, filename: str) -> Dict[str, Any]:
    """Parse JSON or JSONL."""
    text_str = _safe_decode(data)
    # Try orjson first
    try:
        import orjson
        obj = orjson.loads(text_str)
        return _make_result(text=json.dumps(obj, ensure_ascii=False, indent=2), fmt="json")
    except ImportError:
        pass
    except Exception:
        pass

    # Standard json
    try:
        obj = json.loads(text_str)
        return _make_result(text=json.dumps(obj, ensure_ascii=False, indent=2), fmt="json")
    except json.JSONDecodeError:
        pass

    # Try JSONL
    lines = text_str.strip().split("\n")
    objects = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            objects.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    if objects:
        text = json.dumps(objects, ensure_ascii=False, indent=2)
        return _make_result(text=text, fmt="jsonl", metadata={"records": len(objects)})

    return _make_result(text=text_str, success=False, fmt="json", error="Invalid JSON/JSONL")


def parse_html_xml(data: bytes, filename: str) -> Dict[str, Any]:
    """Parse HTML/XML with BeautifulSoup."""
    try:
        from bs4 import BeautifulSoup
        text_str = _safe_decode(data)
        fmt = "xml" if filename.lower().endswith(".xml") else "html"
        parser = "lxml-xml" if fmt == "xml" else "html.parser"
        try:
            soup = BeautifulSoup(text_str, parser)
        except Exception:
            soup = BeautifulSoup(text_str, "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        title = soup.find("title")
        metadata = {}
        if title:
            metadata["title"] = title.get_text(strip=True)
        return _make_result(text=text, fmt=fmt, metadata=metadata)
    except Exception as e:
        return _make_result(text=_safe_decode(data), success=False, fmt="html", error=str(e))


def parse_yaml(data: bytes, filename: str) -> Dict[str, Any]:
    """Parse YAML."""
    try:
        import yaml
        text_str = _safe_decode(data)
        obj = yaml.safe_load(text_str)
        return _make_result(text=str(obj), fmt="yaml")
    except Exception as e:
        return _make_result(text=_safe_decode(data), success=False, fmt="yaml", error=str(e))


def parse_wos(data: bytes, filename: str) -> Dict[str, Any]:
    """Parse Web of Science exported TXT format.
    Fields: TI, AU, PY, TC, DI, CR, AB, DE, etc.
    """
    text_str = _safe_decode(data)
    records = []
    current = {}
    current_field = None

    for line in text_str.split("\n"):
        # Match WOS tagged format: two-letter tag + space, or "ER" (end-of-record, 2 chars)
        is_tagged = (len(line) >= 3 and line[2] == " " and line[:2].strip().isalpha())
        is_er = (line.strip() == "ER" and len(line.strip()) == 2)
        if is_tagged or is_er:
            if is_er:
                if current:
                    records.append(current)
                current = {}
                current_field = None
            else:
                current_field = line[:2].strip()
                value = line[3:].strip()
                if current_field in current:
                    current[current_field] += "; " + value
                else:
                    current[current_field] = value
        elif line.startswith("   ") and current_field:
            current[current_field] = current.get(current_field, "") + " " + line.strip()

    if current:
        records.append(current)

    # Build combined text and metadata
    all_text_parts = []
    metadata = {"wos_records": len(records), "records_detail": []}
    for rec in records:
        parts = []
        m = {}
        for field in ["TI", "AB", "DE", "AU"]:
            if field in rec:
                parts.append(rec[field])
        if "TI" in rec:
            m["title"] = rec["TI"]
        if "AU" in rec:
            m["authors"] = rec["AU"]
        if "PY" in rec:
            m["year"] = rec["PY"]
        if "TC" in rec:
            m["citations"] = rec["TC"]
        if "DI" in rec:
            m["doi"] = rec["DI"]
        if "DE" in rec:
            m["keywords"] = rec["DE"]
        if "CR" in rec:
            m["references"] = rec["CR"]
        metadata["records_detail"].append(m)
        all_text_parts.append(" ".join(parts))

    text = "\n\n".join(all_text_parts)
    return _make_result(text=text, fmt="wos", metadata=metadata)


def parse_ris(data: bytes, filename: str) -> Dict[str, Any]:
    """Parse RIS format."""
    text_str = _safe_decode(data)
    records = []
    current = {}
    for line in text_str.split("\n"):
        line = line.strip()
        if not line:
            continue
        match = re.match(r"^([A-Z][A-Z0-9])\s+-\s+(.*)$", line)
        if match:
            tag, value = match.group(1), match.group(2)
            if tag == "ER":
                if current:
                    records.append(current)
                current = {}
            else:
                if tag in current:
                    current[tag] += "; " + value
                else:
                    current[tag] = value
    if current:
        records.append(current)

    all_text = []
    metadata = {"ris_records": len(records)}
    for rec in records:
        parts = [rec.get("TI", ""), rec.get("AB", ""), rec.get("KW", "")]
        all_text.append(" ".join(p for p in parts if p))

    return _make_result(text="\n\n".join(all_text), fmt="ris", metadata=metadata)


def parse_bib(data: bytes, filename: str) -> Dict[str, Any]:
    """Parse BibTeX format (basic)."""
    text_str = _safe_decode(data)
    entries = re.findall(r"@\w+\{[^@]+\}", text_str, re.DOTALL)
    all_text = []
    metadata = {"bib_entries": len(entries)}
    for entry in entries:
        fields = {}
        for m in re.finditer(r"(\w+)\s*=\s*[{\"](.*?)[}\"]", entry, re.DOTALL):
            fields[m.group(1).lower()] = m.group(2).strip()
        parts = [fields.get("title", ""), fields.get("abstract", ""), fields.get("keywords", "")]
        all_text.append(" ".join(p for p in parts if p))
    return _make_result(text="\n\n".join(all_text), fmt="bib", metadata=metadata)


# Extension to parser mapping
_PARSERS = {
    ".txt": parse_txt,
    ".md": parse_txt,
    ".pdf": parse_pdf,
    ".docx": parse_docx,
    ".doc": parse_doc,
    ".xlsx": parse_excel,
    ".xls": parse_excel,
    ".csv": parse_csv_tsv,
    ".tsv": parse_csv_tsv,
    ".json": parse_json,
    ".jsonl": parse_json,
    ".html": parse_html_xml,
    ".htm": parse_html_xml,
    ".xml": parse_html_xml,
    ".yaml": parse_yaml,
    ".yml": parse_yaml,
    ".ris": parse_ris,
    ".bib": parse_bib,
}


def parse_file(uploaded_file) -> Dict[str, Any]:
    """Parse a single uploaded file. Returns unified structure.
    uploaded_file: Streamlit UploadedFile or similar with .name and .read()
    """
    filename = getattr(uploaded_file, "name", "unknown")
    log_info(f"Parsing file: {filename}")

    try:
        data = uploaded_file.read()
        if hasattr(uploaded_file, "seek"):
            uploaded_file.seek(0)
    except Exception as e:
        log_error(f"Failed to read {filename}", e)
        return _make_result(text="", success=False, fmt="unknown", error=f"Read error: {e}")

    # Check for WOS format
    if filename.lower().endswith(".txt"):
        text_preview = _safe_decode(data[:2000])
        if re.search(r"^(FN|VR|PT|AU|TI)\s", text_preview, re.MULTILINE):
            log_info(f"Detected WOS format for {filename}")
            try:
                result = parse_wos(data, filename)
                result["metadata"]["filename"] = filename
                return result
            except Exception as e:
                log_error(f"WOS parse failed for {filename}", e)

    ext = os.path.splitext(filename)[1].lower()
    parser = _PARSERS.get(ext)

    if parser:
        try:
            # Chunked read for large files
            if len(data) > CHUNK_SIZE and ext in [".txt", ".md", ".csv", ".tsv"]:
                log_info(f"Large file {filename} ({len(data)} bytes), reading in chunks")
                text = _safe_decode(data[:CHUNK_SIZE])
                result = _make_result(text=text, fmt=ext.strip("."))
                result["metadata"]["truncated"] = True
                result["metadata"]["original_size"] = len(data)
            else:
                result = parser(data, filename)
            result["metadata"]["filename"] = filename
            result["metadata"]["size_bytes"] = len(data)
            return result
        except Exception as e:
            log_error(f"Parser failed for {filename}", e)
            # Fallback: try raw text extraction
            fallback_text = _safe_decode(data) if len(data) < CHUNK_SIZE else _safe_decode(data[:CHUNK_SIZE])
            return _make_result(
                text=fallback_text,
                success=False,
                fmt=ext.strip("."),
                error=f"Parser error: {e}",
                metadata={"filename": filename, "fallback": True}
            )
    else:
        # Unknown format - try as text
        try:
            text = _safe_decode(data[:CHUNK_SIZE])
            return _make_result(text=text, success=False, fmt="unknown",
                                error=f"Unsupported format: {ext}",
                                metadata={"filename": filename})
        except Exception as e:
            return _make_result(text="", success=False, fmt="unknown",
                                error=f"Cannot read: {e}",
                                metadata={"filename": filename})


def parse_files(uploaded_files, progress_callback=None) -> List[Dict[str, Any]]:
    """Parse multiple files with progress tracking."""
    results = []
    total = len(uploaded_files)
    for i, f in enumerate(uploaded_files):
        try:
            result = parse_file(f)
            results.append(result)
            status = "OK" if result["success"] else f"PARTIAL ({result['error']})"
            log_info(f"[{i+1}/{total}] {f.name}: {status}")
        except Exception as e:
            log_error(f"[{i+1}/{total}] {f.name}: FAILED", e)
            results.append(_make_result(
                text="", success=False, fmt="unknown",
                error=str(e), metadata={"filename": getattr(f, "name", "unknown")}
            ))
        if progress_callback:
            progress_callback((i + 1) / total)
    return results
