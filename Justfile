# Justfile para gestionar entorno y correr thinkfic-downloader
set shell := ["powershell.exe", "-c"]

# Activar el venv
activate:
    .venv\Scripts\activate

# Instalar dependencias (prod + dev)
install:
    uv pip install -e ".[dev]"

# Descargar videos desde videos.yaml
download:
    .venv\Scripts\thinkfic-video videos.yaml

# Descargar slides (ejemplo con urls.txt)
slides:
    .venv\Scripts\thinkfic-slides urls.txt --out slides.pdf

# Formatear código con black
format:
    .venv\Scripts\black src

# Lint con flake8
lint:
    .venv\Scripts\flake8 src

# Run todo: install + lint + format + download + slides
all: install lint format download slides

pip-upgrade: 
    uv pip install --upgrade pip

# Dev rápido: limpia logs, reinstala, corre todo
dev:
    python -c "import shutil; shutil.rmtree('logs', ignore_errors=True)"
    just pip-upgrade install lint format
