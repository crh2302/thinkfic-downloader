# Thinkific Downloader

Command-line tools to download **videos** and **slides** from Thinkific-based course platforms.

## Features

- Download videos with [`yt-dlp`](https://github.com/yt-dlp/yt-dlp).
- Download slides as images and convert them into PDFs.
- Configurable via `config.yaml` or environment variables (`.env`).
- Colored logging to console and file.
- Parallel downloads with `ThreadPoolExecutor` and progress bars with `tqdm`.
- Ready for reproducible installs with [`uv`](https://github.com/astral-sh/uv) and `pyproject.toml`.

## Requirements

- Python 3.9 or later.
- Dependencies listed in `pyproject.toml`.

## Installation

Clone the repository and set up a virtual environment:

```bash
git clone https://github.com/yourusername/thinkific-downloader.git
cd thinkific-downloader
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows
```

### With uv (recommended)

```bash
uv pip install -e ".[dev]"
```

This reads directly from `pyproject.toml` and installs all dependencies (including dev tools if requested).

### With pip (fallback)

```bash
pip install -r requirements.txt
```

The `requirements.txt` file is auto-generated from `pyproject.toml` for compatibility.

## Usage

### Download videos

Define a `videos.yaml` file:

```yaml
- name: "Video_1"
  url: "https://example.com/video1.m3u8"
- name: "Video_2"
  url: "https://example.com/video2.m3u8"
```

Run:

```bash
thinkfic-video videos.yaml
```

Videos will be saved in a `videos_<timestamp>` folder.

### Download slides

Define a `slides.yaml` file:

```yaml
- name: "Module_I_II"
  last_url: "https://example.com/page_7.jpg"
```

Run:

```bash
thinkfic-slides slides.yaml
```

Slides will be combined into a PDF and stored in `slides_<timestamp>`.

## Configuration

Customizable via `.env` or `config.yaml`:

- `OUTPUT_DIR`, `VIDEOS_OUTPUT_DIR`, `SLIDES_OUTPUT_DIR`
- `MAX_WORKERS`, `MAX_RETRIES`, `RETRY_BACKOFF_SEC`
- `CONCURRENT_FRAGMENTS`, `RATE_LIMIT`
- `COOKIES_FILE`

Example `.env`:

```env
MAX_WORKERS=4
RATE_LIMIT=500K
COOKIES_FILE=cookies.txt
```

## Authentication / Cookies

At the moment, **cookies are not required**. Videos and slides can be downloaded directly if the URLs are public.

The `COOKIES_FILE` option is only provided for compatibility. If in the future Thinkific (or another platform) requires you to be logged in, you can export your browser session cookies (e.g. with a Chrome/Firefox extension like _Get cookies.txt_) and save them as `cookies.txt`.

- **Today** → You don’t need any cookies file.
- **Future** → If access becomes restricted, place `cookies.txt` in the project root and the tool will use it automatically.

## Development

Install development dependencies:

```bash
uv pip install -e ".[dev]"
```

Run lint and format:

```bash
just lint
just format
```

Run downloads:

```bash
just videos
just slides
```

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/new-feature`.
3. Open a pull request.

## License

MIT License. See the [LICENSE](LICENSE) file.

```

