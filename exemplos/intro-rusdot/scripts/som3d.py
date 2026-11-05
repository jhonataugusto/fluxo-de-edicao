"""Som da intro 3D: voz cortada com pausa antes da revelação, base de batida 120 BPM e efeitos nos cortes.

Uso: python -P som3d.py
Lê audio/voz_cortada_v02.wav. Grava em audio/: voz3d_v01.wav (normalizada), musica3d_v01.wav, sfx3d_v01.wav e
mix3d_v01.wav (conferência, masterizado em -14 LUFS). Nunca sobrescreve: falha se a v01 já existir.
"""
import os, subprocess, sys
import numpy as np

AUD = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "audio")
SR, DUR, BPM = 48000, 32.3, 120
BAT = 60 / BPM
PAUSA_EM, PAUSA = 24.9, 1.0  # inserida no vão entre "Rust." (24,79) e "E eu vou" (25,01)
CORTES = [1.5, 3.0, 4.5, 6.0, 9.0, 10.4, 13.9, 17.9, 21.9, 29.5]
MOSTRAR = 26.5  # revelação Godot -> Rusdot
ENCAIXES = [13.3, 14.8, 15.76, 16.42]  # módulos chegando (R2)
rng = np.random.default_rng(11)
N = int(DUR * SR)

saidas = {k: os.path.join(AUD, f"{k}_v01.wav") for k in ("voz3d", "musica3d", "sfx3d", "mix3d")}
if any(os.path.exists(s) for s in saidas.values()):
    sys.exit("v01 já existe: mude a versão")


def ler(arq):
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", arq, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(pcm, np.float32).reshape(-1, 2).copy()


def gravar(x, arq):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a",
                    "pcm_s16le", arq], input=np.clip(x, -1, 1).astype(np.float32).tobytes(), check=True)


def normalizar(entrada, saida, lufs):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", entrada, "-af", f"loudnorm=I={lufs}:TP=-1.5:LRA=11",
                    "-ar", str(SR), "-c:a", "pcm_s16le", saida], check=True)


def poe(pista, som, t0, ganho_db=0.0, pan=0.0):
    i = int(t0 * SR)
    if i >= len(pista) or i + len(som) <= 0:
        return
    s = som[max(0, -i): len(pista) - max(i, 0)] * 10 ** (ganho_db / 20)
    i = max(i, 0)
    if s.ndim == 1:
        s = np.stack([s * (1 - max(pan, 0)), s * (1 + min(pan, 0))], 1)
    pista[i:i + len(s)] += s


def env(n, ataque, queda):
    e = np.exp(-np.arange(n) / SR / queda)
    a = min(n, max(1, int(ataque * SR)))
    e[:a] *= np.linspace(0, 1, a)
    return e


def passa_baixa(x, corte):
    a = np.exp(-2 * np.pi * np.asarray(corte, dtype=float) / SR) * np.ones(len(x))
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = (1 - a[i]) * x[i] + a[i] * acc
        y[i] = acc
    return y


# ---------- instrumentos ----------
def bumbo():
    n = int(0.45 * SR)
    tt = np.arange(n) / SR
    f = 45 + 110 * np.exp(-tt * 35)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.16)


def chimbal(aberto=False):
    n = int((0.18 if aberto else 0.05) * SR)
    r = np.diff(np.concatenate([[0], rng.normal(0, 1, n)]))
    return r / 3 * env(n, 0.001, 0.06 if aberto else 0.015)


def nota(freq, dur, queda=0.25, brilho=2500):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    return passa_baixa(2 * ((tt * freq) % 1) - 1, brilho) * env(n, 0.004, queda)


def pad(freqs, dur):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * tt + rng.uniform(0, 6)) + 0.4 * np.sin(2 * np.pi * f * 2.003 * tt) for f in freqs)
    return s / len(freqs) * np.minimum(1, tt / 0.6) * np.minimum(1, (dur - tt) / 0.6)


def whoosh(dur=0.45):
    n = int(dur * SR)
    u = np.linspace(0, 1, n)
    r = rng.normal(0, 1, n)
    corte = 400 + 6000 * np.sin(np.pi * u) ** 2
    s = (passa_baixa(r, corte) - passa_baixa(r, corte * 0.2)) * np.sin(np.pi * u) ** 3
    return s / np.abs(s).max()


def impacto(dur=1.6):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    grave = np.sin(2 * np.pi * np.cumsum(32 + 40 * np.exp(-tt * 5)) / SR) * np.exp(-tt * 2.2)
    s = grave + 0.7 * passa_baixa(rng.normal(0, 1, n), 3000) * np.exp(-tt * 22)
    return s / np.abs(s).max()


def subida(dur=1.0):
    n = int(dur * SR)
    u = np.linspace(0, 1, n)
    s = passa_baixa(rng.normal(0, 1, n), 300 + 7000 * u ** 2) * u ** 2
    return s / np.abs(s).max()


def clack():
    n = int(0.12 * SR)
    tt = np.arange(n) / SR
    s = (np.sin(2 * np.pi * 180 * tt) * 0.6 + passa_baixa(rng.normal(0, 1, n), 4000)) * np.exp(-tt * 45)
    return s / np.abs(s).max()


# ---------- voz: pausa antes da revelação, normalizada ----------
voz = ler(os.path.join(AUD, "voz_cortada_v02.wav"))
i = int(PAUSA_EM * SR)
voz = np.concatenate([voz[:i], np.zeros((int(PAUSA * SR), 2), np.float32), voz[i:]])[:N]
voz = np.pad(voz, ((0, max(0, N - len(voz))), (0, 0)))
tmp = os.path.join(AUD, "_voz3d_tmp.wav")
gravar(voz, tmp)
normalizar(tmp, saidas["voz3d"], -16)
os.remove(tmp)

# ---------- música (lá menor) ----------
mus = np.zeros((N, 2))
A1, C2, E2, A2 = 55.0, 65.41, 82.41, 110.0
k = 0
while k * BAT < DUR:
    tb = k * BAT
    secao = "gancho" if tb < 10.4 else "respiro" if tb < 24.8 else "pausa" if tb < MOSTRAR else "final"
    if secao != "pausa":
        if secao in ("gancho", "final") or k % 2 == 0:
            poe(mus, bumbo(), tb, -4 if secao != "respiro" else -7)
        poe(mus, chimbal(), tb + BAT / 2, -18 if secao != "respiro" else -24, pan=0.3)
        if k % 4 == 3 and secao != "respiro":
            poe(mus, chimbal(True), tb + BAT * 0.75, -22, pan=-0.3)
        if secao in ("respiro", "final"):  # arpejo em semicolcheias
            for j, f in enumerate((A2 * 2, C2 * 4, E2 * 4, C2 * 4)):
                poe(mus, nota(f, 0.22, 0.12, 1800), tb + j * BAT / 4, -27, pan=0.4 * (-1) ** j)
    k += 1
for de, ate in ((0, 10.4), (10.4, 24.8), (MOSTRAR, DUR)):  # pad por seção
    poe(mus, pad((A1, E2, A2), ate - de), de, -16)
poe(mus, subida(1.0), 24.8 - 1.0, -14)
fim = np.linspace(1, 0, int(0.6 * SR))
mus[-len(fim):] *= fim[:, None]

# ---------- efeitos ----------
sfx = np.zeros((N, 2))
w = whoosh()
for c in CORTES:
    poe(sfx, w, c - 0.22, -16, pan=rng.uniform(-0.4, 0.4))
for s in ENCAIXES:
    poe(sfx, clack(), s + 0.18, -12, pan=rng.uniform(-0.3, 0.3))
poe(sfx, impacto(), MOSTRAR, -6)
poe(sfx, whoosh(0.8), 2.19 - 0.5, -12)  # "RUST" chegando do fundo

gravar(mus * 0.9, saidas["musica3d"])
gravar(sfx * 0.9, saidas["sfx3d"])

# ---------- mix de conferência: voz -16, música bem abaixo, master -14 LUFS ----------
mix = ler(saidas["voz3d"])[:N] + ler(saidas["musica3d"])[:N] * 10 ** (-8 / 20) + ler(saidas["sfx3d"])[:N] * 10 ** (-3 / 20)
tmp = os.path.join(AUD, "_mix_tmp.wav")
gravar(mix * 0.8, tmp)
normalizar(tmp, saidas["mix3d"], -14)
os.remove(tmp)
print("ok:", ", ".join(os.path.basename(s) for s in saidas.values()))
