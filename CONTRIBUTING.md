# Contributing / 贡献指南

Thank you for your interest in AOAA.

欢迎参与 AOAA。

## Good contributions / 适合贡献的内容

- Better document parsers
- More robust multilingual keyword extraction
- More atmospheric-optics analysis pages
- Visualization improvements
- Documentation fixes
- Bug reports with reproducible steps
- New example datasets without private or copyrighted data

## Development check / 开发检查

```bash
python -m compileall .
python selfcheck.py
python smoke_test.py
```

Please avoid committing caches, local model files, API keys, private documents, or exported results.
