set shell := ["powershell.exe", "-c"]

activate:
    .venv\Scripts\activate

install:
    uv pip install -e ".[dev]"

videos:
    .venv\Scripts\python -m src.thinkfic_downloader.video.cli videos.yaml

slides:
    .venv\Scripts\python -m thinkfic_downloader.slides.cli slides.yaml

format:
    .venv\Scripts\black .

lint:
    .venv\Scripts\flake8 .

all: install lint format videos slides
