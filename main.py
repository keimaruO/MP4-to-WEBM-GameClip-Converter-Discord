# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
import shlex

# ===== 設定パラメータ =====
# ターゲットサイズ（バイト）。
# ここでは安全マージンを見て約9.5MB (9961472 バイト) を採用
TARGET_SIZE = 9961472
# もしくは 9.9MB 程度にしたい場合は（例）：
# TARGET_SIZE = 10380902

# 音声ビットレート（bps）
AUDIO_BITRATE = 64000

# GPU を使ってデコード高速化を試みる（ffmpeg の -hwaccel cuda を使用）。
# ※ libvpx のエンコード自体は GPU 対応していないため、
#    GPU が使える場合は入力のデコードが多少速くなる可能性があります。
USE_GPU = True

# エンコード時の追加オプション（エンコード速度と画質のトレードオフ）
# ※ 2パスエンコードの場合、-deadline realtime は使用できないため削除。
EXTRA_VP8_OPTS = ["-cpu-used", "4"]

# ===== ffmpeg/ffprobe のパス設定 =====
# 本スクリプトと同じフォルダに ffmpeg.exe, ffprobe.exe がある前提（Windows）
script_dir = os.path.dirname(os.path.abspath(__file__))
if os.name == "nt":
    FFMPEG = os.path.join(script_dir, "ffmpeg.exe")
    FFPROBE = os.path.join(script_dir, "ffprobe.exe")
    NULL_DEV = "NUL"
else:
    FFMPEG = "ffmpeg"
    FFPROBE = "ffprobe"
    NULL_DEV = "/dev/null"

# ===== 入力ファイル選択ダイアログ =====
def select_input_file():
    root = tk.Tk()
    root.withdraw()  # メインウィンドウを表示しない
    file_path = filedialog.askopenfilename(
        title="入力動画ファイルを選択してください",
        filetypes=[("Video Files", "*.mp4;*.mkv;*.avi;*.mov;*.flv;*.wmv;*.webm"), ("All Files", "*.*")]
    )
    root.destroy()
    return file_path

def get_video_duration(input_file):
    """ffprobe を使用して動画の再生時間（秒）を取得する"""
    cmd = [
        FFPROBE,
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        input_file
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        duration_str = result.stdout.strip()
        return float(duration_str)
    except Exception as e:
        messagebox.showerror("エラー", f"ffprobe による動画情報の取得に失敗しました\n{e}")
        sys.exit(1)

def generate_output_filename(input_file):
    """出力ファイル名を決定。
       output.webm が存在する場合は日時を付与したファイル名とする"""
    base_dir = os.path.dirname(input_file)
    base_name = "output"
    ext = ".webm"
    output_path = os.path.join(base_dir, base_name + ext)
    if os.path.exists(output_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(base_dir, f"{base_name}_{timestamp}{ext}")
    return output_path

def run_ffmpeg_pass(pass_num, input_file, video_bitrate_k, output_file=None):
    """1パス目、2パス目の ffmpeg コマンドを構築して実行する"""
    cmd = [FFMPEG]
    
    if USE_GPU:
        cmd += ["-hwaccel", "cuda"]
    
    cmd += ["-y", "-i", input_file]
    
    # 統計ファイルのパスを明示的に指定
    stats_file = os.path.join(os.getcwd(), "ffmpeg2pass")
    cmd += ["-passlogfile", stats_file]
    
    cmd += ["-c:v", "libvpx", "-b:v", f"{video_bitrate_k}k"]
    cmd += EXTRA_VP8_OPTS
    cmd += ["-pass", str(pass_num)]
    
    if pass_num == 1:
        cmd += ["-an", "-f", "webm", NULL_DEV]
    else:
        cmd += ["-c:a", "libvorbis", "-b:a", "64k", output_file]
    
    print("実行コマンド:")
    print(" ".join(shlex.quote(x) for x in cmd))
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("エラー", f"ffmpeg のパス {pass_num} エンコードでエラーが発生しました\n{e}")
        sys.exit(1)

def main():
    # 入力ファイル選択
    input_file = select_input_file()
    if not input_file:
        print("入力ファイルが選択されなかったため終了します。")
        sys.exit(0)
    print(f"入力ファイル: {input_file}")
    
    # ffprobe により動画の長さを取得
    duration = get_video_duration(input_file)
    print(f"動画の長さ: {duration:.2f} 秒")
    
    # ターゲットファイルサイズ（バイト）から総ビット数（1バイト=8ビット）を計算
    target_bits = TARGET_SIZE * 8
    # 音声分に必要なビット数 = AUDIO_BITRATE * duration
    audio_bits = AUDIO_BITRATE * duration
    # 映像に割り当て可能なビット数
    video_bits = target_bits - audio_bits
    if video_bits <= 0:
        messagebox.showerror("エラー", "動画の長さに対してターゲットサイズが小さすぎます。")
        sys.exit(1)
    
    # 映像の平均ビットレート (bps)
    video_bitrate = video_bits / duration
    # ffmpeg には kbit/s 単位で指定（整数）
    video_bitrate_k = int(video_bitrate / 1000)
    
    print(f"設定する映像ビットレート: {video_bitrate_k} kbit/s")
    print(f"音声ビットレート: {AUDIO_BITRATE//1000} kbit/s")
    
    # 出力ファイル名を生成（既存ファイルがある場合は日時を付与）
    output_file = generate_output_filename(input_file)
    print(f"出力ファイル: {output_file}")
    
    # ffmpeg の 2パスエンコードを実行
    print("=== 1パス目 (解析用) ===")
    run_ffmpeg_pass(1, input_file, video_bitrate_k)
    print("=== 2パス目 (実際のエンコード) ===")
    run_ffmpeg_pass(2, input_file, video_bitrate_k, output_file=output_file)
    
    print("エンコードが完了しました。")
    messagebox.showinfo("完了", f"エンコードが完了しました。\n出力ファイル: {output_file}")

    # クリーンアップ処理
    # ffmpeg によって生成される 2-pass のログファイルを削除
    for suffix in ["-0.log", "-0.log.mbtree"]:
        fpath = os.path.join(os.getcwd(), "ffmpeg2pass" + suffix)
        if os.path.exists(fpath):
            try:
                os.remove(fpath)
            except Exception:
                pass

if __name__ == "__main__":
    main()
