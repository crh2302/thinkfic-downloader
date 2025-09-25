"""
CLI to download a sequence of slides and generate PDFs.
Saves all PDFs in a folder named slides_<timestamp>.
"""

import argparse
import yaml
from pathlib import Path
from datetime import datetime

from thinkfic_downloader.slides.core import download_all_slides
from thinkfic_downloader.config import load_config


def main() -> None:
    parser = argparse.ArgumentParser(description="Download slide presentations and generate PDFs")
    parser.add_argument("yaml_file", help="YAML file containing 'name' and 'last_url'")
    parser.add_argument("--outdir", type=Path, help="Base directory where the slides_<timestamp> folder will be created")
    args = parser.parse_args()

    data = yaml.safe_load(open(args.yaml_file, "r", encoding="utf-8"))

    cfg = load_config("slides")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if args.outdir:
        output_root = args.outdir / f"slides_{timestamp}"
    else:
        output_root = Path(cfg["slides_output_dir"]) / f"slides_{timestamp}"
    output_root.mkdir(parents=True, exist_ok=True)

    results = []
    for entry in data:
        name = entry["name"]
        last_url = entry["last_url"]
        ok = download_all_slides(name, last_url, output_root)
        results.append(ok)

    # Global summary
    ok_list = [n for n, ok in results if ok]
    fail_list = [n for n, ok in results if not ok]

    print("\n===== GLOBAL SUMMARY =====")
    print(f"✔ OK: {len(ok_list)} | ✘ FAIL: {len(fail_list)}")
    for n in ok_list:
        print(f"✔ {n}")
    for n in fail_list:
        print(f"✘ {n}")


if __name__ == "__main__":
    main()
