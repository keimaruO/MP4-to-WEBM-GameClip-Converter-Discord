# 🎮 MP4からWEBMへDiscord用10MBゲームクリップ変換

このツールは、Discord無料ユーザー向けにMP4動画をWEBMに変換し、10MB以下に圧縮します。

自動的に画質調整し9.5MB～9.9MBの最適なサイズに変換

これでNitro課金しなくても快適にゲームクリップを友達共有できる、はず(´･_･` )

## 📂 ざっとしたインストール方法

1. **FFmpegの実行ファイルをダウンロード** (下記手順参照)
2. 変換したい **MP4ファイル** を用意
3. `main.py` を実行し、ファイル選択
4. 変換後、**同じフォルダ**に `output.webm` が保存されます。



## 📂 インストール方法

python入れてない人は入れてねいれてるひとはそのまま次へ。

このプロジェクト(https://github.com/keimaruO/MP4-to-WEBM-GameClip-Converter-Discord)をダンロードして任意の場所に展開。

### 1. FFmpeg実行ファイルの準備

- [FFmpeg-Buildsの最新リリースページ](https://github.com/yt-dlp/FFmpeg-Builds/releases/tag/latest) から、使用しているOSに合ったFFmpegビルドをダウンロードしてください。
- **Windowsの場合**: `ffmpeg-master-latest-win64-gpl-shared.zip` を選んで解凍します。
- 解凍後、`ffmpeg.exe`、`ffplay.exe`、`ffprobe.exe` をツールと同じフォルダに配置します。

- 最終的なディレクトリ構成


<pre>
├── ffmpeg.exe       # FFmpeg実行ファイル
├── ffplay.exe       # FFplay実行ファイル
├── ffprobe.exe      # FFprobe実行ファイル
├── input.mp4        # 変換するMP4ファイル（任意）
├── main.bat         # バッチファイル（Windows用）
├── main.py          # Pythonスクリプト
└── output.webm      # 変換後のWEBMファイル（出力先）
</pre>








### 2. ツールの実行



- `start.bat` をダブルクリックで実行して、変換したいMP4ファイルを選択します。
- 変換が終わると、同じフォルダに `output.webm` が保存されます。

---

## 🚀 設定（オプション）

- **TARGET_SIZE**: 目標ファイルサイズ（デフォルト約9.5MB）
- **AUDIO_BITRATE**: 音声品質（デフォルト64kbps）
- **USE_GPU**: GPUによるデコード高速化

---

## 📜 ライセンス

MIT License（自由に使用・改変可能）
