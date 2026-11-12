"""Temporário: transcreve reels públicos do perfil (para estudar o padrão dos roteiros). Não grava nada no repositório."""
import subprocess, sys, glob, os
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "yt-dlp", "faster-whisper"], check=False)
IDS = sys.argv[1:] or os.environ.get("PADROES", "").split()
os.makedirs("/tmp/r", exist_ok=True)
for c in IDS:
    t, i = c.split(":")
    subprocess.run(["yt-dlp", "-q", "--no-warnings", "-f", "ba/b", "-x", "--audio-format", "mp3", "-o", f"/tmp/r/{t}_{i}.%(ext)s",
                    "--print", "after_move:INFO " + t + " " + i + " | %(duration)s s | curtidas %(like_count)s | comentários %(comment_count)s",
                    f"https://www.instagram.com/reel/{i}/"])
from faster_whisper import WhisperModel
m = WhisperModel("small", device="cpu", compute_type="int8")
for f in sorted(glob.glob("/tmp/r/*.mp3")):
    segs, info = m.transcribe(f, language="pt", vad_filter=True)
    print("#####", os.path.basename(f), round(info.duration), "s")
    print(" ".join(s.text.strip() for s in segs), flush=True)
