import argparse
from pathlib import Path
from datetime import datetime

from thinkfic_downloader.video.core import download_all, VIDEOS_OUTPUT_DIR
from thinkfic_downloader.logs import setup_logger

logger = setup_logger("video-cli", kind="video")


def main() -> None:
    parser = argparse.ArgumentParser(description="Download videos defined in a YAML file using yt-dlp.")
    parser.add_argument(
        "yaml_file",
        type=Path,
        help="Path to the YAML file with the list of videos",
    )
    parser.add_argument(
        "--outdir",
        type=Path,
        help="Base directory where the videos_<timestamp> folder will be created",
    )

    args = parser.parse_args()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if args.outdir:
        output_dir = args.outdir / f"videos_{timestamp}"
    else:
        output_dir = VIDEOS_OUTPUT_DIR / f"videos_{timestamp}"

    output_dir.mkdir(parents=True, exist_ok=True)

    ok_list, fail_list = download_all(args.yaml_file, output_dir)

    print("\n===== GLOBAL SUMMARY =====")
    print(f"✔ OK: {len(ok_list)} | ✘ FAIL: {len(fail_list)}")
    for n in ok_list:
        print(f"✔ {n}")
    for n in fail_list:
        print(f"✘ {n}")

    logger.info("Download finished. Files stored in: %s", output_dir)


if __name__ == "__main__":
    main()
