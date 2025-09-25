from pathlib import Path
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

import yaml
from yt_dlp import YoutubeDL
from tqdm import tqdm

from thinkfic_downloader.config import load_config
from thinkfic_downloader.logs import setup_logger


cfg = load_config("video")
MAX_WORKERS = cfg["max_workers"]
CONCURRENT_FRAGMENTS = cfg["concurrent_fragments"]
RATE_LIMIT = cfg["rate_limit"]
COOKIES_FILE = Path(cfg["cookies_file"])
VIDEOS_OUTPUT_DIR = Path(cfg["videos_output_dir"])

logger = setup_logger("video-downloader", kind="video")


def load_videos(yaml_file: Path) -> List[Tuple[str, str]]:
    with open(yaml_file, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    return [(item["name"], item["url"]) for item in raw]


def download_video(name: str, url: str, output_dir: Path) -> Tuple[str, bool]:
    out_path = output_dir / f"{name}.mp4"

    ydl_opts = {
        "outtmpl": str(out_path),
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
        "logger": None,
        "concurrent_fragment_downloads": CONCURRENT_FRAGMENTS,
        "http_headers": {"User-Agent": "Mozilla/5.0"},
        "prefer_ffmpeg": True,
        "hls_use_mpegts": True,
    }

    if RATE_LIMIT:
        ydl_opts["ratelimit"] = RATE_LIMIT
    if COOKIES_FILE.exists():
        ydl_opts["cookiefile"] = str(COOKIES_FILE)

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return name, True
    except Exception as e:
        logger.error("❌ Error downloading %s: %s", name, e)
        return name, False


def download_all(yaml_file: Path, output_dir: Path) -> Tuple[List[str], List[str]]:
    items = load_videos(yaml_file)
    if not items:
        return [], []

    ok_list, fail_list = [], []

    with (
        ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool,
        tqdm(
            total=len(items),
            desc="Downloading videos",
            position=0,
            leave=True,
            ncols=100,
            dynamic_ncols=True,
        ) as pbar,
    ):
        fut_map = {pool.submit(download_video, n, u, output_dir): n for n, u in items}

        for fut in as_completed(fut_map):
            name = fut_map[fut]
            ok = False
            try:
                _, ok = fut.result()
            except Exception as e:
                logger.error("Exception in %s: %s", name, e)
            if ok:
                ok_list.append(name)
                tqdm.write(f"✔ {name}", nolock=True)
            else:
                fail_list.append(name)
                tqdm.write(f"✘ {name}", nolock=True)
            pbar.update(1)

    return ok_list, fail_list
