# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
import shlex

# ===== 設定パラメータ =====
TARGET_SIZE = 9961472         # ターゲットファイルサイズ（バイト）
AUDIO_BITRATE = 32000         # 音声ビットレート（bps）
USE_GPU = True                # GPU（NVENC）を使う場合 True

# AV1 エンコーダーの追加オプション
EXTRA_AV1_OPTS_GPU = ["-preset", "p4"]  # GPU（NVENC）用オプション（RTX 40系のみ有効）
EXTRA_AV1_OPTS_SW  = ["-cpu-used", "4"]  # CPU（libaom-av1）用オプション

# 出力解像度・その他映像設定
TARGET_RESOLUTION = (1632, 918)  # 出力解像度（None にすると元の解像度維持）
GRAYSCALE = False               # True にするとモノクロ変換
AUTO_RESOLUTION_ADJUST = True   # ビットレートが低い場合に解像度を自動調整するか
MIN_VIDEO_BITRATE_K = 0.5       # 最低映像ビットレート下限（kbit/s）
ENABLE_VFR = True              # 可変フレームレート（NVENC使用時は無効）

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

# ---- GPU モデル名取得（nvidia-smi を利用） ----
def get_gpu_model():
    try:
        result = subprocess.run(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], 
                                capture_output=True, text=True, check=True)
        gpu_model = result.stdout.strip()
        return gpu_model
    except Exception as e:
        return None

# ---- 入力ファイル選択ダイアログ ----
def select_input_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="入力動画ファイルを選択してください",
        filetypes=[("Video Files", "*.mp4;*.mkv;*.avi;*.mov;*.flv;*.wmv;*.webm"), ("All Files", "*.*")]
    )
    root.destroy()
    return file_path

# ---- 動画の再生時間取得 ----
def get_video_duration(input_file):
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
        return float(result.stdout.strip())
    except Exception as e:
        messagebox.showerror("エラー", f"ffprobe による動画情報の取得に失敗しました\n{e}")
        sys.exit(1)

# ---- 出力ファイル名生成 ----
def generate_output_filename(input_file):
    base_dir = os.path.dirname(input_file)
    base_name = "output"
    ext = ".webm"  # WebM は AV1 と Opus/Vorbis に対応
    output_path = os.path.join(base_dir, base_name + ext)
    if os.path.exists(output_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(base_dir, f"{base_name}_{timestamp}{ext}")
    return output_path

# ---- 映像フィルタの構築 ----
def build_vf_filters():
    filters = []
    if TARGET_RESOLUTION is not None:
        filters.append(f"scale={TARGET_RESOLUTION[0]}:{TARGET_RESOLUTION[1]}")
    if GRAYSCALE:
        filters.append("format=gray")
    # GPU 使用時（NVENC）には、mpdecimate 等のフィルタは使用しない
    if ENABLE_VFR and not USE_GPU:
        filters.append("mpdecimate")
    return filters

# ---- ffmpeg の実行 ----
def run_ffmpeg(pass_num, input_file, video_bitrate_k, output_file=None):
    cmd = [FFMPEG]
    if USE_GPU:
        cmd += ["-hwaccel", "cuda"]
    cmd += ["-y", "-i", input_file]
    
    vf_filters = build_vf_filters()
    if vf_filters:
        cmd += ["-vf", ",".join(vf_filters)]
    
    if not USE_GPU:
        stats_file = os.path.join(os.getcwd(), "ffmpeg2pass")
        cmd += ["-passlogfile", stats_file]
    
    encoder = "av1_nvenc" if USE_GPU else "libaom-av1"
    cmd += ["-c:v", encoder, "-b:v", f"{video_bitrate_k}k"]
    
    if USE_GPU:
        cmd += EXTRA_AV1_OPTS_GPU
        # NVENC使用時は -vsync は指定しない
    else:
        cmd += EXTRA_AV1_OPTS_SW
        if pass_num:
            cmd += ["-pass", str(pass_num)]
        if pass_num == 2 and ENABLE_VFR:
            cmd += ["-vsync", "vfr"]
    
    # 音声設定
    if not USE_GPU:
        if pass_num == 1:
            cmd += ["-an", "-f", "webm", NULL_DEV]
        else:
            cmd += ["-c:a", "libopus", "-b:a", "64k", output_file]
    else:
        cmd += ["-c:a", "libopus", "-b:a", "64k", output_file]
    
    print("実行コマンド:")
    print(" ".join(shlex.quote(arg) for arg in cmd))
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("エラー", f"ffmpeg のエンコードでエラーが発生しました\n{e}")
        sys.exit(1)

# ---- ログファイルのクリーンアップ ----
def cleanup_logfiles():
    for suffix in ["-0.log", "-0.log.mbtree"]:
        path = os.path.join(os.getcwd(), "ffmpeg2pass" + suffix)
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception:
                pass

# ---- メイン処理 ----
def main():
    global TARGET_RESOLUTION, USE_GPU
    input_file = select_input_file()
    if not input_file:
        print("入力ファイルが選択されなかったため終了します。")
        sys.exit(0)
    print(f"入力ファイル: {input_file}")
    
    duration = get_video_duration(input_file)
    print(f"動画の長さ: {duration:.2f} 秒")
    
    target_bits = TARGET_SIZE * 8
    audio_bits = AUDIO_BITRATE * duration
    video_bits = target_bits - audio_bits
    if video_bits <= 0:
        messagebox.showerror("エラー", "動画の長さに対してターゲットサイズが小さすぎます。")
        sys.exit(1)
    
    video_bitrate = video_bits / duration
    video_bitrate_k = int(video_bitrate / 1000)
    print(f"設定する映像ビットレート: {video_bitrate_k} kbit/s")
    print(f"音声ビットレート: {AUDIO_BITRATE // 1000} kbit/s")
    
    if video_bitrate_k < MIN_VIDEO_BITRATE_K:
        if AUTO_RESOLUTION_ADJUST and TARGET_RESOLUTION is not None:
            factor = (video_bitrate_k / MIN_VIDEO_BITRATE_K) ** 0.5
            new_width = max(int(TARGET_RESOLUTION[0] * factor), 16)
            new_height = max(int(TARGET_RESOLUTION[1] * factor), 16)
            print(f"【自動調整】解像度を {TARGET_RESOLUTION} から ({new_width}, {new_height}) に調整します。")
            TARGET_RESOLUTION = (new_width, new_height)
        else:
            print("【注意】映像ビットレートが非常に低いため、画質が著しく低下する可能性があります。")
    
    output_file = generate_output_filename(input_file)
    print(f"出力ファイル: {output_file}")
    
    # GPU 使用時は、nvidia-smi により GPU モデルを取得し、
    # RTX 40 系（Ada Lovelace）以外、すなわち RTX 3080 などの場合は AV1 NVENC が未対応の可能性が高いのでフォールバック
    if USE_GPU:
        gpu_model = get_gpu_model()
        if gpu_model is None:
            messagebox.showwarning("警告", "GPU情報が取得できなかったため、CPU エンコードにフォールバックします。")
            USE_GPU = False
        else:
            # ここでは RTX 40 系のキーワード（例："RTX 4090", "Ada" など）がある場合のみ NVENC 使用とする
            if not (("RTX 40" in gpu_model) or ("Ada" in gpu_model)):
                warn_msg = (f"現在の GPU は '{gpu_model}' です。\n"
                            "このGPUは AV1 NVENC エンコードに対応していない可能性があるため、\n"
                            "CPU エンコード（libaom-av1）にフォールバックします。")
                print(warn_msg)
                messagebox.showwarning("警告", warn_msg)
                USE_GPU = False
    
    if USE_GPU:
        print("=== 単一パス (NVENC ハードウェアエンコード) ===")
        run_ffmpeg(None, input_file, video_bitrate_k, output_file=output_file)
    else:
        print("=== 1パス目 (解析用) ===")
        run_ffmpeg(1, input_file, video_bitrate_k)
        print("=== 2パス目 (エンコード) ===")
        run_ffmpeg(2, input_file, video_bitrate_k, output_file=output_file)
    
    print("エンコードが完了しました。")
    messagebox.showinfo("完了", f"エンコードが完了しました。\n出力ファイル: {output_file}")
    cleanup_logfiles()

if __name__ == "__main__":
    main()
