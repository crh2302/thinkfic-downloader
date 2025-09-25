"""
Main logic for downloading slides using ThreadPoolExecutor and tqdm.
"""

from pathlib import Path
from typing import List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import tempfile
import requests
from tqdm import tqdm
from PIL import Image


def expand_urls_from_last(last_url: str) -> List[str]:
    import re

    m = re.search(r"_page__([0-9]+)\.jpg$", last_url)
    if not m:
        raise ValueError(f"Could not extract page number from {last_url}")
    last_num = int(m.group(1))
    prefix = last_url[: m.start(1)]
    suffix = last_url[m.end(1) :]
    return [f"{prefix}{i}{suffix}" for i in range(0, last_num + 1)]


def download_slide(url: str, dest: Path) -> bool:
    try:
        r = requests.get(url, timeout=30, stream=True)
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(8192):
                if chunk:
                    f.write(chunk)
        return True
    except Exception:
        return False


def images_to_pdf(images: List[Path], pdf_path: Path) -> None:
    if not images:
        return
    pil_images = [Image.open(p).convert("RGB") for p in images]
    pil_images[0].save(pdf_path, save_all=True, append_images=pil_images[1:])


def download_all_slides(name: str, last_url: str, output_root: Path, max_workers: int = 4) -> Tuple[str, bool]:
    urls = expand_urls_from_last(last_url)
    pdf_path = output_root / f"{name}.pdf"

    ok_files: List[Path] = []

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        with tqdm(total=len(urls), desc=name, ncols=100) as pbar:
            with ThreadPoolExecutor(max_workers=max_workers) as pool:
                fut_map = {pool.submit(download_slide, url, tmp_path / f"slide_{i}.jpg"): i for i, url in enumerate(urls)}
                for fut in as_completed(fut_map):
                    i = fut_map[fut]
                    try:
                        ok = fut.result()
                    except Exception:
                        ok = False
                    if ok:
                        ok_files.append(tmp_path / f"slide_{i}.jpg")
                    pbar.update(1)

        if ok_files:
            images_to_pdf(sorted(ok_files), pdf_path)
            return name, True

    return name, False
