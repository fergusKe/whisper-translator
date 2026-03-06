# Whisper Translator

將影片或音檔自動轉錄為中文文字。

使用 [mlx-whisper](https://github.com/ml-explore/mlx-examples/tree/main/whisper)（Apple Silicon 優化版），在 M 系列晶片上速度遠快於原版 Whisper。

## 環境需求

- macOS（Apple Silicon，M1 以上）
- [uv](https://docs.astral.sh/uv/)
- [ffmpeg](https://ffmpeg.org/)

## 安裝

```bash
brew install ffmpeg
uv sync
```

## 使用方式

1. 將影片或音檔放入 `input/` 資料夾
2. 執行轉錄

```bash
uv run transcribe.py
```

3. 結果輸出至 `output/`，格式為 `{檔名}_whisper-large-v3-mlx.txt`

已轉錄過的檔案下次會自動跳過。

## 支援格式

`.mp4` `.mov` `.mkv` `.webm` `.mp3` `.wav` `.m4a`

## 模型

使用 `mlx-community/whisper-large-v3-mlx`，首次執行時會自動從 Hugging Face 下載（約 3GB），快取於 `~/.cache/huggingface/hub/`。
