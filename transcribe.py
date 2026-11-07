import subprocess
import time
from pathlib import Path

INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")
MODEL_SIZE = "mlx-community/whisper-large-v3-mlx"
TEXT_CONVERTER = "s2twp"

SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".mp4", ".m4a", ".mov", ".webm", ".mkv"}
HALLUCINATION_PHRASES = (
    "明鏡與點點欄目",
    "明镜与点点栏目",
    "請不吝點贊",
    "请不吝点赞",
)


def find_media_files() -> list[Path]:
    return sorted(
        f for f in INPUT_DIR.rglob("*") if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def get_output_path(media_path: Path) -> Path:
    relative_path = media_path.relative_to(INPUT_DIR)
    return OUTPUT_DIR / relative_path.with_name(
        f"{media_path.stem}_{MODEL_SIZE.split('/')[-1]}.txt"
    )


def get_text_converter():
    from opencc import OpenCC

    return OpenCC(TEXT_CONVERTER)


def is_hallucinated_text(text: str) -> bool:
    normalized = " ".join(text.split())
    if not normalized:
        return True

    return any(phrase in normalized for phrase in HALLUCINATION_PHRASES)


def format_timestamp(seconds: float) -> str:
    """將 Whisper 回傳的秒數格式化為易讀的時間軸。"""
    total_seconds = max(0, int(seconds))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def validate_media_file(media_path: Path) -> None:
    probe = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a:0",
            "-show_entries",
            "stream=codec_type",
            "-of",
            "default=nw=1:nk=1",
            str(media_path),
        ],
        capture_output=True,
        text=True,
    )
    if probe.returncode != 0:
        detail = probe.stderr.strip() or "未知的媒體格式錯誤"
        raise RuntimeError(detail)
    if not probe.stdout.strip():
        raise RuntimeError("找不到可讀取的音訊串流，檔案可能尚未完整下載或已損壞")


def transcribe_file(audio_path: Path) -> str:
    import mlx_whisper

    converter = get_text_converter()
    print("  載入模型並開始轉錄，第一支或長影片可能會停留一段時間...", flush=True)
    result = mlx_whisper.transcribe(
        str(audio_path),
        language="zh",
        path_or_hf_repo=MODEL_SIZE,
        condition_on_previous_text=False,
        hallucination_silence_threshold=2.0,
    )

    lines = []
    for segment in result["segments"]:
        text = converter.convert(segment["text"])
        if is_hallucinated_text(text):
            print(
                f"  [{segment['start']:.1f}s -> {segment['end']:.1f}s] 略過疑似幻覺: {text}",
                flush=True,
            )
            continue

        print(f"  [{segment['start']:.1f}s -> {segment['end']:.1f}s] {text}", flush=True)
        start_time = format_timestamp(segment["start"])
        end_time = format_timestamp(segment["end"])
        lines.append(f"[{start_time} → {end_time}] {text}")

    return "\n".join(lines)


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    media_files = find_media_files()
    if not media_files:
        print(f"input/ 資料夾中沒有找到媒體檔案 {SUPPORTED_EXTENSIONS}")
        return

    pending = []
    skipped_count = 0
    total_count = len(media_files)
    for overall_index, media_path in enumerate(media_files, 1):
        output_path = get_output_path(media_path)
        if output_path.exists():
            skipped_count += 1
            print(f"[{overall_index}/{total_count}] 略過（已轉錄）: {media_path.relative_to(INPUT_DIR)}")
        else:
            pending.append((overall_index, media_path))

    print(f"\n掃描完成：共 {total_count} 個媒體檔，已轉錄 {skipped_count} 個，待轉錄 {len(pending)} 個。")

    if not pending:
        print("所有檔案都已轉錄完畢！")
        return

    for pending_index, (overall_index, media_path) in enumerate(pending, 1):
        output_path = get_output_path(media_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        print(
            f"\n[{overall_index}/{total_count}｜待轉錄 {pending_index}/{len(pending)}] "
            f"正在轉錄: {media_path.relative_to(INPUT_DIR)}",
            flush=True,
        )
        print(f"輸出位置: {output_path}", flush=True)
        try:
            validate_media_file(media_path)
        except RuntimeError as error:
            print(f"略過：無法讀取媒體檔 {media_path}", flush=True)
            print(f"原因：{error}", flush=True)
            continue

        start = time.time()
        text = transcribe_file(media_path)
        elapsed = time.time() - start

        output_path.write_text(text, encoding="utf-8")
        print(f"已儲存: {output_path}", flush=True)
        print(f"耗時: {elapsed:.1f} 秒", flush=True)

    print("\n全部完成!")


if __name__ == "__main__":
    main()
