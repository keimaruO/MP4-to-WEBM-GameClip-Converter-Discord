# 🎮 MP4からWEBMへDiscord用10MBゲームクリップ変換

このツールは、Discord無料ユーザー向けにMP4動画をWEBMに変換し、10MB以下に圧縮します。これでゲームクリップがDiscordにアップロード可能になります！

## 📂 使い方

1. **FFmpegの実行ファイルをダウンロード** (下記手順参照)
2. 変換したい **MP4ファイル** を用意
3. `main.py` を実行し、ファイル選択
4. 変換後、**同じフォルダ**に `output.webm` が保存されます。

## 🛠 必要なファイル

- **FFmpegの実行ファイル**（`ffmpeg.exe`, `ffplay.exe`, `ffprobe.exe`）
- **MP4ファイル**（変換対象）

## 🚀 設定（オプション）

- **TARGET_SIZE**: 目標ファイルサイズ（デフォルト約9.5MB）
- **AUDIO_BITRATE**: 音声品質（デフォルト64kbps）
- **USE_GPU**: GPUによるデコード高速化

---

## 📂 詳細手順

### 1. FFmpeg実行ファイルの準備

- [FFmpeg-Buildsの最新リリースページ](https://github.com/yt-dlp/FFmpeg-Builds/releases/tag/latest) から、使用しているOSに合ったFFmpegビルドをダウンロードしてください。
- **Windowsの場合**: `ffmpeg-master-latest-win64-gpl-shared.zip` を選んで解凍します。
- 解凍後、`ffmpeg.exe`、`ffplay.exe`、`ffprobe.exe` をツールと同じフォルダに配置します。

### 2. ツールの実行

- `main.py` を実行して、変換したいMP4ファイルを選択します。
- 変換が終わると、同じフォルダに `output.webm` が保存されます。

---

## 📜 ライセンス

MIT License（自由に使用・改変可能）
