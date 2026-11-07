import argparse
from pathlib import Path

from opencc import OpenCC

OUTPUT_DIR = Path("output")

CONVERTERS = {
    "traditional": "s2twp",
    "simplified": "t2s",
}


def convert_file(path: Path, converter: OpenCC) -> bool:
    original = path.read_text(encoding="utf-8")
    converted = converter.convert(original)
    if converted == original:
        return False

    path.write_text(converted, encoding="utf-8")
    return True


def main():
    parser = argparse.ArgumentParser(description="批次轉換 output/ 內的 txt 簡繁中文。")
    parser.add_argument(
        "--to",
        choices=CONVERTERS.keys(),
        default="traditional",
        help="轉換方向，預設 traditional（簡體轉台灣繁體）。",
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=OUTPUT_DIR,
        help="要轉換的檔案或資料夾，預設 output/。",
    )
    args = parser.parse_args()

    converter = OpenCC(CONVERTERS[args.to])
    paths = [args.path] if args.path.is_file() else sorted(args.path.rglob("*.txt"))

    changed = 0
    for path in paths:
        if convert_file(path, converter):
            changed += 1
            print(f"已轉換: {path}")
        else:
            print(f"略過（無變更）: {path}")

    print(f"\n完成，共處理 {len(paths)} 個 txt，轉換 {changed} 個。")


if __name__ == "__main__":
    main()
