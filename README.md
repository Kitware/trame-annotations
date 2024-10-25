# trame-annotations

This trame package aims to gather widgets that help make image/video annotations easier with your trame application.

## Installing

Install it from pypi:

```bash
pip install trame-annotations
```

## Contribute to trame-annotations

```bash
git clone https://github.com/Kitware/trame-annotations.git
cd trame-annotations
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e '.[dev]'
pip install pre-commit
pre-commit install
pytest .
```
