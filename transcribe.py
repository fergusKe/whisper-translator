import time
from pathlib import Path

import mlx_whisper

INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")
MODEL_SIZE = "mlx-community/whisper-large-v3-mlx"

SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".mp4", ".m4a", ".mov", ".webm", ".mkv"}


def transcribe_file(audio_path: Path) -> str:
    result = mlx_whisper.transcribe(str(audio_path), language="zh", path_or_hf_repo=MODEL_SIZE)

    lines = []
    for segment in result["segments"]:
        print(f"  [{segment['start']:.1f}s -> {segment['end']:.1f}s] {segment['text']}")
        lines.append(segment["text"])

    return "\n".join(lines)


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    media_files = [f for f in INPUT_DIR.iterdir() if f.suffix.lower() in SUPPORTED_EXTENSIONS]
    if not media_files:
        print(f"input/ 資料夾中沒有找到媒體檔案 {SUPPORTED_EXTENSIONS}")
        return

    pending = []
    for media_path in media_files:
        output_path = OUTPUT_DIR / f"{media_path.stem}_{MODEL_SIZE.split('/')[-1]}.txt"
        if output_path.exists():
            print(f"略過（已轉錄）: {media_path.name}")
        else:
            pending.append(media_path)

    if not pending:
        print("所有檔案都已轉錄完畢！")
        return

    for i, media_path in enumerate(pending, 1):
        print(f"\n[{i}/{len(pending)}] 正在轉錄: {media_path.name}")
        start = time.time()
        text = transcribe_file(media_path)
        elapsed = time.time() - start

        output_path = OUTPUT_DIR / f"{media_path.stem}_{MODEL_SIZE.split('/')[-1]}.txt"
        output_path.write_text(text, encoding="utf-8")
        print(f"已儲存: {output_path}")
        print(f"耗時: {elapsed:.1f} 秒")

    print("\n全部完成!")


if __name__ == "__main__":
    main()
