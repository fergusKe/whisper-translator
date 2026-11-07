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

1. 將影片或音檔放入 `input/` 資料夾，可直接放檔案，也可以放多層資料夾
2. 執行轉錄

```bash
uv run transcribe.py
```

3. 結果輸出至 `output/`，格式為 `{檔名}_whisper-large-v3-mlx.txt`

每段文字都會附上起訖時間軸，方便回到影片或音檔定位內容：

```text
[00:01:23 → 00:01:28] 這是該段轉錄文字。
```

輸出會保留 `input/` 裡的資料夾結構。例如：

```text
input/課程名稱/01-章節/1-1 單元.mp4
output/課程名稱/01-章節/1-1 單元_whisper-large-v3-mlx.txt
```

已轉錄過的檔案下次會自動跳過。判斷方式是對應的輸出 `.txt` 是否已存在。
若要讓既有輸出也加上時間軸，請刪除該 `.txt` 後重新執行轉錄。

## 中文簡繁轉換

轉錄時會自動將 Whisper 輸出的中文轉成台灣繁體，再寫入 `.txt`。

如果已經有轉好的 `.txt`，可以事後批次轉換：

```bash
uv run convert_text.py --to traditional
```

也可以轉成簡體：

```bash
uv run convert_text.py --to simplified
```

預設會處理 `output/` 裡所有 `.txt`，並直接改寫原檔。也可以指定單一檔案或資料夾：

```bash
uv run convert_text.py --to traditional --path "output/課程名稱"
```

簡繁轉換使用本機 OpenCC 規則，不會呼叫 LLM，也不會消耗 token。

## 進度與耗時

程式會先掃描所有媒體檔，顯示已轉錄與待轉錄數量。轉錄時會同時顯示全部進度與待轉錄進度，例如：

```text
[29/70｜待轉錄 1/42] 正在轉錄: ...
```

前面的 `29/70` 是全部媒體檔進度，後面的 `待轉錄 1/42` 是這次實際需要轉錄的進度。單支影片需要等 Whisper 完整轉錄後才會寫入 `.txt`。

一小時影片大致可能需要 5-30 分鐘，實際時間會依 Mac 晶片、影片長度、音訊複雜度和模型載入狀況而變動。第一次執行時也可能需要下載模型。

## 支援格式

`.mp4` `.mov` `.mkv` `.webm` `.mp3` `.wav` `.m4a`

## 模型

使用 `mlx-community/whisper-large-v3-mlx`，首次執行時會自動從 Hugging Face 下載（約 3GB），快取於 `~/.cache/huggingface/hub/`。
