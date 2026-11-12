"""Temporário: transcreve reels públicos do perfil (para estudar o padrão dos roteiros). Não grava nada no repositório."""
import subprocess, sys, glob, os
subprocess.run("sudo apt-get install -y -qq ffmpeg >/dev/null 2>&1", shell=True)
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "yt-dlp", "faster-whisper"], check=False)
import numpy as np
IDS = sys.argv[1:] or os.environ.get("PADROES", "").split()
os.makedirs("/tmp/r", exist_ok=True)
for c in IDS:
    t, i = c.split(":")
    subprocess.run([sys.executable, "-m", "yt_dlp", "-q", "--no-warnings", "--no-simulate", "-f", "ba/b", "-o", f"/tmp/r/{t}_{i}.%(ext)s",
                    "--print", "INFO " + t + " " + i + " | curtidas %(like_count)s | comentários %(comment_count)s", f"https://www.instagram.com/reel/{i}/"])
from faster_whisper import WhisperModel
m = WhisperModel("small", device="cpu", compute_type="int8")
for f in sorted(glob.glob("/tmp/r/*")):
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout
    audio = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
    segs, info = m.transcribe(audio, language="pt", vad_filter=True)
    print("#####", os.path.basename(f), round(len(audio) / 16000), "s")
    print(" ".join(s.text.strip() for s in segs), flush=True)
