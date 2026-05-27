# -*- coding: utf-8 -*-
"""Smoke tests for file parser."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class FakeFile:
    def __init__(self, name, data):
        self.name = name
        self._data = data
    def read(self):
        return self._data
    def seek(self, n):
        pass


def test_empty_file():
    from utils.file_parser import parse_file
    f = FakeFile("empty.txt", b"")
    result = parse_file(f)
    assert result["format"] == "txt"
    assert result["text"] == ""
    print("PASS: empty file")


def test_garbled_file():
    from utils.file_parser import parse_file
    f = FakeFile("garbled.txt", bytes(range(256)) * 10)
    result = parse_file(f)
    assert isinstance(result["text"], str)
    print("PASS: garbled file")


def test_large_text():
    from utils.file_parser import parse_file
    big = b"hello world " * 1000000  # ~12MB
    f = FakeFile("big.txt", big)
    result = parse_file(f)
    assert result["text"]
    assert len(result["text"]) > 0
    print("PASS: large text file")


def test_json():
    from utils.file_parser import parse_file
    f = FakeFile("test.json", b'{"key": "value"}')
    result = parse_file(f)
    assert result["success"]
    assert "key" in result["text"]
    print("PASS: JSON")


def test_jsonl():
    from utils.file_parser import parse_file
    data = b'{"a":1}\n{"b":2}\n{"c":3}\n'
    f = FakeFile("test.jsonl", data)
    result = parse_file(f)
    assert result["success"]
    print("PASS: JSONL")


if __name__ == "__main__":
    test_empty_file()
    test_garbled_file()
    test_large_text()
    test_json()
    test_jsonl()
    print("\nAll parser smoke tests passed!")
