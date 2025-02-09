# 🎮 MP4からWEBMへDiscord用10MBゲームクリップ変換

このツールは、Discord無料ユーザー向けにMP4動画をWEBMに変換し、10MB以下に圧縮します。

自動的に画質調整し9.5MB～9.9MBの最適なサイズに変換

これでNitro課金しなくても快適にゲームクリップを友達共有できる、はず(´･_･` )

## 📂 ざっとした使い方

1. 変換したい **MP4ファイル** を用意
2. `start.bat` を実行し、任意のMP4ファイルを選択
3. 変換後、**同じフォルダ**に `output.webm` が保存される。

完成。


## 📂 インストール方法

### 1. 必要なファイルの準備

1. **FFmpegのダウンロード**  
   - [FFmpeg-Buildsの最新リリースページ](https://github.com/yt-dlp/FFmpeg-Builds/releases/tag/latest)から、使用中のOSに合ったFFmpegビルドをダウンロードしてください。  
   - **Windowsの場合：**  
     `ffmpeg-master-latest-win64-gpl-shared.zip` を選び、解凍します。

2. **Pythonのインストール**  
   - まだPythonをインストールしていない場合は、公式サイトからインストールしてください。

3. **プロジェクトのダウンロード**  
   - [GitHubリポジトリ](https://github.com/keimaruO/MP4-to-WEBM-GameClip-Converter-Discord)からプロジェクトをダウンロードし、任意の場所に展開してください。

### 2. ファイルの配置

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


### 3. ツールの実行

1. **実行方法**  
   - `start.bat` を実行して、変換したいMP4ファイルを選択してください。

2. **変換完了**  
   - 変換が終了すると、同じフォルダに `output.webm` が生成されます。

---

## オプション設定

ツールには以下の設定項目があります。必要に応じて値を変更してください。

- **TARGET_SIZE**  
  目標ファイルサイズ（デフォルト：約9.5MB）

- **AUDIO_BITRATE**  
  音声のビットレート（デフォルト：64kbps）

- **USE_GPU**  
  GPUを利用してデコード処理を高速化するオプション

---

## ライセンス

このツールは **MIT License** の下で公開されています。  
自由に使用および改変することができます。

---
