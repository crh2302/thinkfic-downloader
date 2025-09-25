"""
CLI para descargar secuencia de slides y generar PDF.
"""

import argparse
import shutil
from pathlib import Path
from datetime import datetime

from colorama import Fore, Style, init

from thinkfic_downloader.slides.slides import download_images, images_to_pdf
from thinkfic_downloader.logs import setup_logger

# Inicializar colorama para colores en consola
init(autoreset=True)

# Logger con archivo único por corrida
logger = setup_logger("slides-cli", kind="slides")


def main() -> None:
    parser = argparse.ArgumentParser(description="Descargar slides y generar un PDF")
    parser.add_argument("urls", help="Archivo de texto con URLs (una por línea)")
    parser.add_argument(
        "--out",
        help="Nombre del PDF final (si no se pasa, se genera con timestamp)",
    )
    args = parser.parse_args()

    # Timestamp único
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Carpeta temporal con timestamp
    out_dir = Path(f"slides_tmp_{timestamp}")

    # Nombre del PDF final
    pdf_out = Path(args.out) if args.out else Path(f"slides_{timestamp}.pdf")

    with open(args.urls, "r", encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip()]

    logger.info("Iniciando descarga de %d slides", len(urls))
    local_images = download_images(urls, out_dir)

    ok_count = len(local_images)
    fail_count = len(urls) - ok_count

    # Resumen con colores
    logger.info("===== RESUMEN SLIDES =====")
    logger.info(
        "%s✔ OK: %d%s | %s✘ FAIL: %d%s",
        Fore.GREEN,
        ok_count,
        Style.RESET_ALL,
        Fore.RED,
        fail_count,
        Style.RESET_ALL,
    )

    if ok_count > 0:
        images_to_pdf(local_images, pdf_out)
        logger.info("%sPDF generado:%s %s", Fore.CYAN, Style.RESET_ALL, pdf_out)
    else:
        logger.error(
            "%sNo se generó el PDF (ninguna imagen descargada).%s",
            Fore.RED,
            Style.RESET_ALL,
        )

    # 🔥 Limpiar directorio temporal
    if out_dir.exists():
        shutil.rmtree(out_dir)
        logger.info("Directorio temporal eliminado: %s", out_dir)


if __name__ == "__main__":
    main()
