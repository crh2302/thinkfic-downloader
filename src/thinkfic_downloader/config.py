import os
from pathlib import Path
import yaml

# --- Intentar importar dotenv solo si está instalado ---
try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

# --- Cargar .env si existe ---
if load_dotenv and Path(".env").exists():
    load_dotenv()


def load_config(process: str = "video") -> dict:
    """
    Carga configuración desde config.yaml (si existe) y .env.
    Las variables de entorno tienen prioridad.
    """
    base = {}
    if Path("config.yaml").exists():
        with open("config.yaml", "r", encoding="utf-8") as f:
            base = yaml.safe_load(f) or {}

    # Valores por defecto
    defaults = {
        "process_name": process,
        "output_dir": os.getenv("OUTPUT_DIR", "downloads"),
        "log_dir": os.getenv("LOG_DIR", "logs"),
        "max_workers": int(os.getenv("MAX_WORKERS", "3")),
        "max_retries": int(os.getenv("MAX_RETRIES", "2")),
        "retry_backoff_sec": int(os.getenv("RETRY_BACKOFF_SEC", "4")),
        "concurrent_fragments": int(os.getenv("CONCURRENT_FRAGMENTS", "5")),
        # 🔑 Parsear RATE_LIMIT como int si existe, None si no
        "rate_limit": (int(os.getenv("RATE_LIMIT")) if os.getenv("RATE_LIMIT") else None),
        "cookies_file": os.getenv("COOKIES_FILE", "cookies.txt"),
    }

    # Combinar config.yaml con defaults y .env (env tiene prioridad)
    merged = {**base.get(process, {}), **defaults}
    return merged
