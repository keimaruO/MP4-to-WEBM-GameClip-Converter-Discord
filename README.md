[English](#english)
# Discord Nitroなくてもちょうどいい具合に10MB以内に動画を圧縮して遅れるようにするやつ



---

## 日本語

### 🎮 概要

Nitro非会員様こんにちは。

このツールは、MP4をWEBMに変換して、10MB以下に圧縮します。  Discord無料ユーザー向け

どんな長さ、どんな解像度、フレームレートであっても9.5MB～9.9MB以内に圧縮するやつ。GPU使うから早いゾ

無課金だと最大ファイルアップロードが10MBくそだるくて何回もクリップ再出力してる人向けのツール


### 📂 ざっとした使い方

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

## English

### 🎮 Overview

This tool converts MP4 videos into WEBM format and compresses them to under 10MB for free Discord users.  

### 📂 Quick Usage

1. Prepare the **MP4 file** you want to convert.
2. Run `start.bat` and select your desired MP4 file.
3. After conversion, `output.webm` will be saved in the **same folder**.

That's it.

## 📂 Installation Guide

### 1. Prepare the Required Files

1. **Download FFmpeg**  
   - Visit the [FFmpeg-Builds latest release page](https://github.com/yt-dlp/FFmpeg-Builds/releases/tag/latest) and download the FFmpeg build that matches your operating system.  
   - **For Windows:**  
     Choose `ffmpeg-master-latest-win64-gpl-shared.zip` and extract it.

2. **Install Python**  
   - If you haven't installed Python yet, download it from the official website.

3. **Download the Project**  
   - Download the project from the [This GitHub repository](https://github.com/keimaruO/MP4-to-WEBM-GameClip-Converter-Discord) and extract it to a location of your choice.

### 2. Organize Your Files

Your final directory structure should look like this:

<pre>
├── ffmpeg.exe       # FFmpeg executable
├── ffplay.exe       # FFplay executable
├── ffprobe.exe      # FFprobe executable
├── input.mp4        # MP4 file to be converted (optional)
├── main.bat         # Batch file (for Windows)
├── main.py          # Python script
└── output.webm      # Converted WEBM file (output)
</pre>

### 3. Run the Tool

1. **How to Run**  
   - Execute `start.bat` and select the MP4 file you want to convert.

2. **Conversion Completion**  
   - Once the conversion is finished, `output.webm` will appear in the same folder.

---

## Optional Settings

The tool offers the following configuration options. Adjust the values as needed:

- **TARGET_SIZE**  
  Target file size (default: ~9.5MB)

- **AUDIO_BITRATE**  
  Audio bitrate (default: 64kbps)

- **USE_GPU**  
  Option to use the GPU to speed up the decoding process

---

## License

This tool is released under the **MIT License**.  
Feel free to use and modify it as you like.

---
