"""
Lógica principal para descarga de videos con yt-dlp.
"""

from tqdm import tqdm
from pathlib import Path
from typing import Dict, Any, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

import yaml
from yt_dlp import YoutubeDL
from colorama import init

from thinkfic_downloader.config import load_config
from thinkfic_downloader.logs import setup_logger

# --- Inicialización global ---
init(autoreset=True)

# --- Configuración ---
cfg = load_config("video")
OUTPUT_DIR = Path(cfg["output_dir"])
MAX_WORKERS = cfg["max_workers"]
MAX_RETRIES = cfg["max_retries"]
RETRY_BACKOFF_SEC = cfg["retry_backoff_sec"]
CONCURRENT_FRAGMENTS = cfg["concurrent_fragments"]
RATE_LIMIT = cfg["rate_limit"]  # int o None
COOKIES_FILE = Path(cfg["cookies_file"])

logger = setup_logger("video-downloader", kind="video")


# -----------------------------
# Helpers de nombres y tqdm
# -----------------------------
def _short_name(name: str, max_len: int = 25) -> str:
    """Acorta nombre si excede max_len, agrega '…' al final."""
    return name if len(name) <= max_len else name[: max_len - 1] + "…"


def make_pbar(name: str) -> tqdm:
    """Crea una barra de progreso con ancho fijo y formato alineado."""
    return tqdm(
        total=0,
        unit="B",
        unit_scale=True,
        desc=_short_name(name, 25),
        leave=True,
        ncols=120,  # ancho fijo global
        bar_format=("{desc:<27} {percentage:3.0f}%|{bar:40}| " "{n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"),
    )


# -----------------------------
# Lógica principal
# -----------------------------
def _progress_hook_tqdm(d: Dict[str, Any], pbar: tqdm):
    if d["status"] == "downloading":
        downloaded = d.get("downloaded_bytes", 0)
        total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
        if total:
            pbar.total = total
            pbar.n = downloaded
            pbar.refresh()
    elif d["status"] == "finished":
        pbar.n = pbar.total
        pbar.refresh()


def load_videos(yaml_file: Path) -> List[Tuple[str, str]]:
    """Carga lista de (name, url) desde YAML."""
    yaml_file = yaml_file.resolve()
    with open(yaml_file, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return [(item["name"], item["url"]) for item in raw]


def download_video(name: str, url: str, output_dir: Path) -> Tuple[str, bool]:
    """Descarga un video individual con progreso en tqdm."""
    out_path = output_dir / f"{name}.mp4"
    pbar = make_pbar(name)

    ydl_opts = {
        "outtmpl": str(out_path),
        "progress_hooks": [lambda d: _progress_hook_tqdm(d, pbar)],
        "quiet": True,  # silencio general
        "no_warnings": True,  # sin warnings
        "noprogress": True,  # desactiva barra interna
        "logger": None,  # sin logs de yt-dlp
        "concurrent_fragment_downloads": CONCURRENT_FRAGMENTS,
    }

    if RATE_LIMIT:
        ydl_opts["ratelimit"] = RATE_LIMIT
    if COOKIES_FILE.exists():
        ydl_opts["cookiefile"] = str(COOKIES_FILE)

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        pbar.close()
        return name, True
    except Exception as e:
        pbar.write(f"{name} ❌ Error: {e}")
        pbar.close()
        return name, False


def download_all(yaml_file: Path, output_dir: Path = OUTPUT_DIR) -> None:
    """Descarga múltiples videos desde YAML con barras alineadas."""
    items = load_videos(yaml_file)
    output_dir.mkdir(parents=True, exist_ok=True)
    results: List[Tuple[str, bool]] = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        fut_map = {pool.submit(download_video, n, u, output_dir): n for n, u in items}
        try:
            for fut in as_completed(fut_map):
                name = fut_map[fut]
                try:
                    _, ok = fut.result()
                except Exception as e:
                    logger.error("Excepción en %s: %s", name, e)
                    results.append((name, False))
                else:
                    results.append((name, ok))
        except KeyboardInterrupt:
            logger.warning("⏹ Descarga interrumpida por el usuario")
            for fut in fut_map:
                fut.cancel()

    ok_list = [n for n, ok in results if ok]
    fail_list = [n for n, ok in results if not ok]

    logger.info("===== RESUMEN =====")
    logger.info("✔ OK: %d | ✘ FAIL: %d", len(ok_list), len(fail_list))
    for n in ok_list:
        logger.info("✔ %s", n)
    for n in fail_list:
        logger.info("✘ %s", n)
