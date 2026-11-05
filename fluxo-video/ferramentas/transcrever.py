"""Transcreve um áudio/vídeo com tempo por palavra (faster-whisper, GPU se houver).

Uso: python -P transcrever.py <midia> --saida <pasta> [--modelo large-v3-turbo] [--idioma pt]
Saída: transcricao.json ({idioma, duracao_s, palavras[{texto,inicio,fim,prob}], frases[{texto,inicio,fim}]})
       e transcricao.txt (uma frase por linha, com o tempo).
"""
import argparse, json, os, subprocess
import numpy as np
from faster_whisper import WhisperModel

ap = argparse.ArgumentParser()
ap.add_argument("midia")
ap.add_argument("--saida", required=True)
ap.add_argument("--modelo", default="large-v3-turbo")
ap.add_argument("--idioma", default="pt")
a = ap.parse_args()
os.makedirs(a.saida, exist_ok=True)

# Decodifica pelo FFmpeg (16 kHz mono float32): evita depender da versão do PyAV.
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", a.midia, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"],
                     capture_output=True, check=True).stdout
audio = np.frombuffer(pcm, np.float32)

def rodar(device, tipo):
    m = WhisperModel(a.modelo, device=device, compute_type=tipo)
    s, i = m.transcribe(audio, language=a.idioma, word_timestamps=True, vad_filter=True)
    return list(s), i

try:
    segs, info = rodar("cuda", "float16")
except RuntimeError as e:  # sem CUDA utilizável: CPU (mais lento, mesmo resultado)
    print("GPU indisponível, usando CPU:", e)
    segs, info = rodar("cpu", "int8")

palavras = [{"texto": w.word.strip(), "inicio": round(w.start, 3), "fim": round(w.end, 3), "prob": round(w.probability, 3)}
            for s in segs for w in (s.words or [])]
frases = [{"texto": s.text.strip(), "inicio": round(s.start, 3), "fim": round(s.end, 3)} for s in segs]
json.dump({"idioma": info.language, "duracao_s": round(info.duration, 3), "palavras": palavras, "frases": frases},
          open(os.path.join(a.saida, "transcricao.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
with open(os.path.join(a.saida, "transcricao.txt"), "w", encoding="utf-8") as f:
    for s in frases:
        f.write(f"[{s['inicio']:6.2f}–{s['fim']:6.2f}] {s['texto']}\n")
print(open(os.path.join(a.saida, "transcricao.txt"), encoding="utf-8").read())
