# -*- coding: utf-8 -*-
"""Comprehensive tests for file_parser.py."""

import pytest
from tests.conftest import FakeUploadedFile


# ── TXT ──

def test_txt_simple():
    from utils.file_parser import parse_file
    f = FakeUploadedFile("test.txt", b"Hello world. This is a test.")
    r = parse_file(f)
    assert r["success"]
    assert r["format"] == "txt"
    assert "Hello world" in r["text"]


def test_txt_empty():
    from utils.file_parser import parse_file
    f = FakeUploadedFile("empty.txt", b"")
    r = parse_file(f)
    assert r["format"] == "txt"
    assert r["text"] == ""


def test_txt_garbled():
    from utils.file_parser import parse_file
    r = parse_file(FakeUploadedFile("garbled.txt", bytes(range(256)) * 10))
    assert isinstance(r["text"], str)


def test_txt_large():
    from utils.file_parser import parse_file
    big = b"hello world " * 1000000
    r = parse_file(FakeUploadedFile("big.txt", big))
    assert len(r["text"]) > 0


def test_txt_chinese():
    from utils.file_parser import parse_file
    data = "大气光学是研究光在大气中传播、散射和折射的科学。".encode("utf-8")
    r = parse_file(FakeUploadedFile("chinese.txt", data))
    assert r["success"]
    assert "大气光学" in r["text"]


def test_txt_chinese_gbk():
    from utils.file_parser import parse_file
    data = "大气光学学术分析器".encode("gbk")
    r = parse_file(FakeUploadedFile("cn_gbk.txt", data))
    assert isinstance(r["text"], str)
    assert len(r["text"]) > 0


# ── JSON ──

def test_json_simple():
    from utils.file_parser import parse_file
    r = parse_file(FakeUploadedFile("test.json", b'{"key": "value"}'))
    assert r["success"]
    assert "key" in r["text"]


def test_json_invalid():
    from utils.file_parser import parse_file
    r = parse_file(FakeUploadedFile("bad.json", b'{not json}'))
    assert not r["success"]


# ── JSONL ──

def test_jsonl():
    from utils.file_parser import parse_file
    r = parse_file(FakeUploadedFile("test.jsonl", b'{"a":1}\n{"b":2}\n{"c":3}\n'))
    assert r["success"]
    assert r["format"] == "jsonl"


def test_jsonl_empty():
    from utils.file_parser import parse_file
    r = parse_file(FakeUploadedFile("empty.jsonl", b""))
    assert not r["success"]


# ── CSV ──

def test_csv_simple():
    from utils.file_parser import parse_file
    r = parse_file(FakeUploadedFile("test.csv", b"col1,col2\nval1,val2\nval3,val4"))
    assert r["success"]
    assert r["format"] in ("csv", "xlsx")


# ── WOS ──

def test_wos_detection():
    from utils.file_parser import parse_file
    data = b"""FN ISI Export
VR 1.0
PT J
AU Smith, J
TI A Study of Atmospheric Optics
PY 2020
TC 5
ER

PT J
AU Jones, K
TI Light Scattering in Clouds
PY 2019
TC 12
ER
"""
    r = parse_file(FakeUploadedFile("wos_test.txt", data))
    assert r["format"] == "wos"
    assert r["success"]
    assert r["metadata"]["wos_records"] == 2


# ── RIS ──

def test_ris():
    from utils.file_parser import parse_file
    data = b"""TY  - JOUR
TI  - Atmospheric Light Scattering
AU  - Zhang, W
PY  - 2021
KW  - optics; atmosphere
ER  -
"""
    r = parse_file(FakeUploadedFile("test.ris", data))
    assert r["format"] == "ris"
    assert r["success"]
    assert r["metadata"]["ris_records"] == 1


# ── BibTeX ──

def test_bibtex():
    from utils.file_parser import parse_file
    data = b"""@article{smith2020,
    title={Atmospheric Optics},
    author={Smith, J},
    year={2020},
    abstract={A study of light in the atmosphere},
    keywords={optics, atmosphere}
}
"""
    r = parse_file(FakeUploadedFile("test.bib", data))
    assert r["format"] == "bib"
    assert r["success"]
    assert r["metadata"]["bib_entries"] == 1


# ── YAML ──

def test_yaml():
    from utils.file_parser import parse_file
    r = parse_file(FakeUploadedFile("test.yaml", b"key: value\nlist:\n  - a\n  - b"))
    assert r["success"]
    assert r["format"] == "yaml"


# ── HTML ──

def test_html():
    from utils.file_parser import parse_file
    r = parse_file(FakeUploadedFile("test.html", b"<html><body><p>Hello</p></body></html>"))
    assert r["success"]
    assert "Hello" in r["text"]


# ── Unsupported format ──

def test_unsupported():
    from utils.file_parser import parse_file
    r = parse_file(FakeUploadedFile("test.xyz", b"some data"))
    assert not r["success"]
    assert r["format"] == "unknown"


# ── parse_files bulk ──

def test_parse_files_bulk():
    from utils.file_parser import parse_files
    files = [
        FakeUploadedFile("a.txt", b"hello"),
        FakeUploadedFile("b.txt", b"world"),
    ]
    results = parse_files(files)
    assert len(results) == 2
    assert all(r["success"] for r in results)
