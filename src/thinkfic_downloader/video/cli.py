import argparse
from pathlib import Path
from datetime import datetime

from thinkfic_downloader.video.core import download_all


def main() -> None:
    """Punto de entrada CLI para descargar videos."""
    parser = argparse.ArgumentParser(description="Descargar videos definidos en un archivo YAML con yt-dlp.")
    parser.add_argument(
        "yaml_file",
        type=Path,
        help="Ruta al archivo YAML con la lista de videos",
    )
    parser.add_argument(
        "--outdir",
        type=Path,
        help="Directorio donde guardar los videos " "(si no se pasa, se genera con timestamp)",
    )

    args = parser.parse_args()

    # Definir carpeta de salida con timestamp si no se pasa
    if args.outdir:
        output_dir = args.outdir
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(f"videos_{timestamp}")

    download_all(args.yaml_file, output_dir)
