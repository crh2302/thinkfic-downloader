set shell := ["powershell.exe", "-c"]

# --- Virtual environment management ---
activate:
    .venv\Scripts\activate

recreate-venv:
    Remove-Item -Recurse -Force .venv -ErrorAction SilentlyContinue;
    python -m venv .venv --upgrade-deps

install:
    uv pip install -e ".[dev]"
    .\.venv\Scripts\python.exe -m pip install build twine

videos:
    .venv\Scripts\python -m src.thinkfic_downloader.video.cli videos.yaml

slides:
    .venv\Scripts\python -m thinkfic_downloader.slides.cli slides.yaml

format:
    .venv\Scripts\black .

lint:
    .venv\Scripts\flake8 .

all: install lint format videos slides

# --- Packaging & publishing ---
build:
    .\.venv\Scripts\python.exe -m build

publish-test:
    .\.venv\Scripts\twine upload --repository testpypi dist/*

publish:
    .\.venv\Scripts\twine upload dist/*
