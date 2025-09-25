import os
from pathlib import Path
import yaml

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

# Load .env if it exists
if load_dotenv and Path(".env").exists():
    load_dotenv()


def load_config(process: str = "video") -> dict:
    """
    Load configuration from config.yaml (if it exists) and .env.
    Environment variables take precedence.
    """
    base = {}
    if Path("config.yaml").exists():
        with open("config.yaml", "r", encoding="utf-8") as f:
            base = yaml.safe_load(f) or {}

    # Default values
    defaults = {
        "process_name": process,
        "output_dir": os.getenv("OUTPUT_DIR", "downloads"),
        "slides_output_dir": os.getenv("SLIDES_OUTPUT_DIR", "slides"),
        "videos_output_dir": os.getenv("VIDEOS_OUTPUT_DIR", "videos"),
        "log_dir": os.getenv("LOG_DIR", "logs"),
        "max_workers": int(os.getenv("MAX_WORKERS", "3")),
        "max_retries": int(os.getenv("MAX_RETRIES", "2")),
        "retry_backoff_sec": int(os.getenv("RETRY_BACKOFF_SEC", "4")),
        "concurrent_fragments": int(os.getenv("CONCURRENT_FRAGMENTS", "5")),
        "rate_limit": (int(os.getenv("RATE_LIMIT")) if os.getenv("RATE_LIMIT") else None),
        "cookies_file": os.getenv("COOKIES_FILE", "cookies.txt"),
    }

    # Merge config.yaml with defaults and .env (env has priority)
    merged = {**base.get(process, {}), **defaults}
    return merged
