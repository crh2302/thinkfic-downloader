"""
Lógica para descargar imágenes y generar un PDF.
"""

import requests
from pathlib import Path
from typing import List
from PIL import Image
from thinkfic_downloader.logs import setup_logger

logger = setup_logger("slides-downloader", kind="slides")


def download_images(urls: List[str], out_dir: Path) -> List[Path]:
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    local_paths = []

    for i, url in enumerate(urls, start=1):
        dest = out_dir / f"slide_{i}.jpg"
        try:
            logger.info("Descargando slide %d: %s", i, url)
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            dest.write_bytes(r.content)
            local_paths.append(dest)
            logger.info("OK: %s", dest)
        except Exception as e:
            logger.error("Fallo al descargar slide %d (%s): %s", i, url, e)

    return local_paths


def images_to_pdf(images: List[Path], pdf_path: Path) -> None:
    """Convierte imágenes a un único PDF."""
    if not images:
        logger.error("No hay imágenes válidas para generar PDF")
        return

    try:
        pil_images = [Image.open(p).convert("RGB") for p in images]
        pil_images[0].save(pdf_path, save_all=True, append_images=pil_images[1:])
        logger.info("PDF generado: %s", pdf_path)
    except Exception as e:
        logger.error("Error al generar PDF %s: %s", pdf_path, e)
