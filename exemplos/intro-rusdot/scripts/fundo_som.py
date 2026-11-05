"""Fundo (cor por trecho + vinheta + grão), clarões de transição e efeitos sonoros da intro de teste.

Uso: python -P fundo_som.py   (depois do render das cenas: lê motion/c*/digitacao_c*.json)
Saída em _CLAUDE/: fundo.mov, flashes/flash_<quadro>.mov, audio/voz.wav, audio/sfx_transicoes.wav,
audio/sfx_digitacao.wav.
"""
import glob, json, os, subprocess
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # _CLAUDE
VIDEO = os.path.dirname(BASE)
FPS, W, H, SR = 30, 1920, 1080, 48000
TOTAL = 1100  # quadros (36,67 s)
rng = np.random.default_rng(7)


def hexrgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32)


# ---------- fundo ----------
TRECHOS = [(0, "#0D1520"), (72, "#1A0B07"), (159, "#0D1520"), (342, "#0E0D12"), (609, "#1A0B07"),
           (837, "#000000"), (865, "#0A1018"), (889, "#1A0B07")]


def cor_fundo(f):
    rgb = hexrgb([cor for q, cor in TRECHOS if q <= f][-1])
    if f >= TOTAL - 10:  # some junto com a última cena
        rgb = rgb * (TOTAL - 1 - f) / 9
    return rgb


yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
r2 = ((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2
vinheta = (1 - 0.55 * np.clip(r2 / 2, 0, 1))[..., None]
ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r",
                       str(FPS), "-i", "-", "-c:v", "prores_ks", "-profile:v", "2", "-pix_fmt", "yuv422p10le",
                       os.path.join(BASE, "fundo.mov")], stdin=subprocess.PIPE)
for f in range(TOTAL):
    img = cor_fundo(f)[None, None, :] * vinheta
    if f < 837 or f >= 865:  # a pausa fica preta pura
        img = img + rng.normal(0, 4.0, (H // 2, W // 2, 1)).repeat(2, 0).repeat(2, 1)
    ff.stdin.write(np.clip(img, 0, 255).astype(np.uint8).tobytes())
ff.stdin.close()
ff.wait()

# ---------- clarões (light leak) ----------
CLAROES = [(71, "#FF5A1F"), (341, "#FF5A1F"), (608, "#FF5A1F"), (888, "#FFE3C8"), (977, "#FF5A1F")]
PERFIL = [0.45, 1.0, 0.8, 0.4, 0.12]
os.makedirs(os.path.join(BASE, "flashes"), exist_ok=True)
d = np.sqrt(((xx - W * 0.85) / (W * 0.6)) ** 2 + ((yy - H * 0.4) / (H * 0.9)) ** 2)
forma = np.clip(1.1 - d, 0, 1) ** 1.5  # luz entrando pela direita
for q, cor in CLAROES:
    rgb = hexrgb(cor) * (1 - forma[..., None] * 0.5) + 255 * forma[..., None] * 0.5  # núcleo quase branco
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r",
                           str(FPS), "-i", "-", "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le",
                           os.path.join(BASE, "flashes", f"flash_{q:04d}.mov")], stdin=subprocess.PIPE)
    for a in PERFIL:
        alpha = np.clip(forma * a * 1.6, 0, 1) * 255
        ff.stdin.write(np.dstack([np.clip(rgb, 0, 255), alpha]).astype(np.uint8).tobytes())
    ff.stdin.close()
    ff.wait()

# ---------- som ----------
os.makedirs(os.path.join(BASE, "audio"), exist_ok=True)
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", os.path.join(VIDEO, "audio_teste.m4a"), "-ar", str(SR), "-ac", "2",
                "-c:a", "pcm_s16le", os.path.join(BASE, "audio", "voz.wav")], check=True)
N = int(TOTAL / FPS * SR)


def passa_baixa(x, corte):
    """Filtro de 1 polo com corte variável (array em Hz)."""
    a = np.exp(-2 * np.pi * np.asarray(corte) / SR) * np.ones_like(x)
    y = np.zeros_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = (1 - a[i]) * x[i] + a[i] * acc
        y[i] = acc
    return y


def whoosh(dur=0.5):
    n = int(dur * SR)
    t = np.linspace(0, 1, n)
    ruido = rng.normal(0, 1, n)
    corte = 300 + 5000 * np.sin(np.pi * t) ** 2
    s = (passa_baixa(ruido, corte) - passa_baixa(ruido, corte * 0.15)) * np.sin(np.pi * t) ** 3
    return s / np.abs(s).max()


def impacto(dur=1.2):
    n = int(dur * SR)
    t = np.arange(n) / SR
    freq = 38 + 30 * np.exp(-t * 6)
    grave = np.sin(2 * np.pi * np.cumsum(freq) / SR) * np.exp(-t * 3.2)
    trans = passa_baixa(rng.normal(0, 1, n), 2500) * np.exp(-t * 28)
    s = grave + 0.8 * trans
    return s / np.abs(s).max()


def tec():
    n = int(0.018 * SR)
    t = np.arange(n) / SR
    s = np.diff(np.concatenate([[0], rng.normal(0, 1, n)])) * np.exp(-t * 380)
    return s / np.abs(s).max()


def poe(pista, som, t, ganho_db, pan=0.0):
    i = int(t * SR)
    if i >= N:
        return
    s = som[: N - i] * 10 ** (ganho_db / 20)
    pista[i:i + len(s), 0] += s * (1 - max(pan, 0))
    pista[i:i + len(s), 1] += s * (1 + min(pan, 0))


trans = np.zeros((N, 2))
w = whoosh()
for q, _ in CLAROES:  # pico do whoosh no corte
    poe(trans, w, (q + 1) / FPS - 0.25, -14, pan=rng.uniform(-0.3, 0.3))
poe(trans, impacto(), 889 / FPS, -8)

dig = np.zeros((N, 2))
for arq in sorted(glob.glob(os.path.join(BASE, "motion", "c*", "digitacao_c*.json"))):
    for d in json.load(open(arq)):
        for k in range(d["chars"]):
            poe(dig, tec(), d["t"] + k / d["cps"] + rng.uniform(-0.006, 0.006), -24 + rng.uniform(-3, 2),
                pan=rng.uniform(-0.15, 0.15))


def grava(pista, nome):
    pico = np.abs(pista).max()
    if pico > 0.98:
        pista = pista * 0.98 / pico
    pcm = (np.clip(pista, -1, 1) * 32767).astype("<i2").tobytes()
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "s16le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    os.path.join(BASE, "audio", nome)], input=pcm, check=True)


grava(trans, "sfx_transicoes.wav")
grava(dig, "sfx_digitacao.wav")
print("fundo, clarões e som prontos")
