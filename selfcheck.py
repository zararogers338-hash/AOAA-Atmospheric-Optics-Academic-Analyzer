from pathlib import Path

REQUIRED = [
    "app.py",
    "README.md",
    "INSTALL.md",
    "LICENSE",
    "requirements.txt",
    "config.example.yaml",
    "utils/file_parser.py",
    "utils/nlp.py",
    "utils/graph.py",
    "utils/system_monitor.py",
    "pages/_phenomenon_base.py",
    "docs/ARCHITECTURE.md",
    "docs/MONITORING.md",
    "examples/sample_literature.txt",
]

missing = [p for p in REQUIRED if not Path(p).exists()]
if missing:
    raise SystemExit("Missing required files: " + ", ".join(missing))

bad = list(Path('.').rglob('__pycache__')) + list(Path('.').rglob('*.pyc'))
if bad:
    raise SystemExit("Python cache files should not be committed: " + ", ".join(map(str, bad[:10])))

print("AOAA selfcheck passed.")
