# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
import shlex

# ===== 設定パラメータ =====
# ターゲットファイルサイズ（バイト）。例として約9.5MB (9961472 バイト)
TARGET_SIZE = 9961472

# 音声ビットレート（bps）
AUDIO_BITRATE = 64000

# GPU を使った高速デコード（ffmpeg の -hwaccel cuda）
USE_GPU = True

# エンコード時の追加オプション（エンコード速度と画質のトレードオフ）
EXTRA_VP8_OPTS = ["-cpu-used", "4"]

# ★ 解像度変更および自動調整の設定 ★
# 出力解像度（例：(640, 360)）。None にすれば元の解像度維持。
TARGET_RESOLUTION = (640, 360)

# GRAYSCALE が True ならモノクロ変換（今回はフルカラーなので通常 False）
GRAYSCALE = False

# ビットレートが低すぎるとき、自動的に TARGET_RESOLUTION を縮小するかどうか
AUTO_RESOLUTION_ADJUST = True
MIN_VIDEO_BITRATE_K = 50  # 最低映像ビットレート下限（kbit/s）

# ★ フレームレート可変の設定 ★
# 動きの少ないシーンは重複フレームを除去して実質的なフレームレートを下げる
ENABLE_VFR = True

# ===== ffmpeg/ffprobe のパス設定 =====
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
    root.withdraw()  # メインウィンドウ非表示
    file_path = filedialog.askopenfilename(
        title="入力動画ファイルを選択してください",
        filetypes=[("Video Files", "*.mp4;*.mkv;*.avi;*.mov;*.flv;*.wmv;*.webm"), ("All Files", "*.*")]
    )
    root.destroy()
    return file_path

def get_video_duration(input_file):
    """
    ffprobe を使用して動画の再生時間（秒）を取得する
    """
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
    """
    出力ファイル名を生成。
    既存の output.webm がある場合はタイムスタンプを付与
    """
    base_dir = os.path.dirname(input_file)
    base_name = "output"
    ext = ".webm"
    output_path = os.path.join(base_dir, base_name + ext)
    if os.path.exists(output_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(base_dir, f"{base_name}_{timestamp}{ext}")
    return output_path

def build_vf_filters():
    """
    出力時の映像フィルタを構築する。
    ・TARGET_RESOLUTION によるスケール変更
    ・GRAYSCALE (必要なら)
    ・ENABLE_VFR が True なら mpdecimate で重複フレームの除去（可変フレームレート）
    """
    filters = []
    if TARGET_RESOLUTION is not None:
        filters.append("scale={}:{}".format(TARGET_RESOLUTION[0], TARGET_RESOLUTION[1]))
    if GRAYSCALE:
        filters.append("format=gray")
    if ENABLE_VFR:
        filters.append("mpdecimate")
    return filters

def run_ffmpeg_pass(pass_num, input_file, video_bitrate_k, output_file=None):
    """
    1パス目（解析用）と2パス目（実際のエンコード）の ffmpeg コマンドを構築・実行
    """
    cmd = [FFMPEG]
    
    if USE_GPU:
        cmd += ["-hwaccel", "cuda"]
    
    cmd += ["-y", "-i", input_file]
    
    # フィルタチェーンの構築
    vf_filters = build_vf_filters()
    if vf_filters:
        cmd += ["-vf", ",".join(vf_filters)]
    
    # 2パスエンコード用の統計ファイルのパスを明示的に指定
    stats_file = os.path.join(os.getcwd(), "ffmpeg2pass")
    cmd += ["-passlogfile", stats_file]
    
    cmd += ["-c:v", "libvpx", "-b:v", f"{video_bitrate_k}k"]
    cmd += EXTRA_VP8_OPTS
    cmd += ["-pass", str(pass_num)]
    
    # 2パス目（最終エンコード）のみ、可変フレームレート出力のために -vsync vfr を指定
    if pass_num == 2 and ENABLE_VFR:
        cmd += ["-vsync", "vfr"]
    
    if pass_num == 1:
        cmd += ["-an", "-f", "webm", NULL_DEV]
    else:
        cmd += ["-c:a", "libvorbis", "-b:a", "64k", output_file]
    
    print("実行コマンド:")
    print(" ".join(shlex.quote(arg) for arg in cmd))
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("エラー", f"ffmpeg のパス {pass_num} エンコードでエラーが発生しました\n{e}")
        sys.exit(1)

def cleanup_logfiles():
    """
    ffmpeg の2パスエンコードで生成される一時ログファイルを削除する
    """
    for suffix in ["-0.log", "-0.log.mbtree"]:
        fpath = os.path.join(os.getcwd(), "ffmpeg2pass" + suffix)
        if os.path.exists(fpath):
            try:
                os.remove(fpath)
            except Exception:
                pass

def main():
    global TARGET_RESOLUTION  # 自動解像度調整のためにグローバルで変更可能にする
    # --- 入力ファイル選択 ---
    input_file = select_input_file()
    if not input_file:
        print("入力ファイルが選択されなかったため終了します。")
        sys.exit(0)
    print(f"入力ファイル: {input_file}")
    
    # --- 動画の再生時間取得 ---
    duration = get_video_duration(input_file)
    print(f"動画の長さ: {duration:.2f} 秒")
    
    # --- ターゲットファイルサイズから総ビット数計算 ---
    target_bits = TARGET_SIZE * 8
    audio_bits = AUDIO_BITRATE * duration
    video_bits = target_bits - audio_bits
    if video_bits <= 0:
        messagebox.showerror("エラー", "動画の長さに対してターゲットサイズが小さすぎます。")
        sys.exit(1)
    
    # --- 映像ビットレート算出 ---
    video_bitrate = video_bits / duration
    video_bitrate_k = int(video_bitrate / 1000)
    print(f"設定する映像ビットレート: {video_bitrate_k} kbit/s")
    print(f"音声ビットレート: {AUDIO_BITRATE // 1000} kbit/s")
    
    # --- ビットレートが低すぎる場合、自動解像度調整（できるだけ高品質を維持） ---
    if video_bitrate_k < MIN_VIDEO_BITRATE_K:
        if AUTO_RESOLUTION_ADJUST and TARGET_RESOLUTION is not None:
            factor = (video_bitrate_k / MIN_VIDEO_BITRATE_K) ** 0.5
            new_width = max(int(TARGET_RESOLUTION[0] * factor), 16)
            new_height = max(int(TARGET_RESOLUTION[1] * factor), 16)
            print(f"【自動調整】映像ビットレートが低いため、解像度を {TARGET_RESOLUTION} から ({new_width}, {new_height}) に調整します。")
            TARGET_RESOLUTION = (new_width, new_height)
        else:
            print("【注意】算出された映像ビットレートが非常に低いため、画質が著しく低下する可能性があります。")
    
    # --- 出力ファイル名生成 ---
    output_file = generate_output_filename(input_file)
    print(f"出力ファイル: {output_file}")
    
    # --- 2パスエンコード実行 ---
    print("=== 1パス目 (解析用) ===")
    run_ffmpeg_pass(1, input_file, video_bitrate_k)
    print("=== 2パス目 (エンコード) ===")
    run_ffmpeg_pass(2, input_file, video_bitrate_k, output_file=output_file)
    
    print("エンコードが完了しました。")
    messagebox.showinfo("完了", f"エンコードが完了しました。\n出力ファイル: {output_file}")
    
    # --- ログファイル削除 ---
    cleanup_logfiles()

if __name__ == "__main__":
    main()
