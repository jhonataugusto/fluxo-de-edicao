"""SFX da intro 3D v02 com os sons do pack (fluxo-de-edicao/assets/Sfx) + música com silêncio antes da revelação.

Gera audio/sfx3d_v02.wav e audio/musica3d_v02.wav (48 kHz estéreo, 32,3 s). Não altera os v01.
Cada evento: (tempo, arquivo, ganho dB, modo). modo "pico" alinha o ponto mais forte do som ao tempo
(whooshes: o "vuuush" cai no corte); "inicio" alinha o começo (impactos); "fim" termina no tempo (build-up).
"""
import subprocess
from pathlib import Path

import numpy as np

SR, DUR = 48000, 32.3
PACK = Path(r"C:\Users\jhonata\Documents\fluxo-de-edicao\assets\Sfx")
AUDIO = Path(__file__).resolve().parent.parent / "audio"


def ler(caminho):
    bruto = subprocess.run(["ffmpeg", "-v", "error", "-i", str(caminho), "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                           capture_output=True, check=True).stdout
    return np.frombuffer(bruto, dtype=np.float32).reshape(-1, 2).copy()


def pico(x):
    env = np.convolve(np.abs(x).mean(axis=1), np.ones(960) / 960, mode="same")  # janela de 20 ms
    return int(env.argmax())


GRAMPOS = ["hit grapple #1.wav", "hit grapple #2.wav", "hit grapple #3.wav", "hit grapple #4.wav"]
EVENTOS = [
    (0.0, "Lit dark whoosh.mp3", -16, "inicio"),       # ar escuro de abertura
    (1.5, "Quick whoosh.mp3", -10, "pico"),            # S1 -> S2
    (2.19, "Lit whoosh impact.mp3", -6, "pico"),       # RUST assenta
    (3.0, "woosh #3.mp3", -10, "pico"),                # -> S3
    (3.35, "Lit cloth roll 1.mp3", -15, "inicio"),     # OC cai no quadro
    (4.5, "woosh #6.mp3", -12, "pico"),                # -> S4
    (6.0, "bass woosh #1.mp3", -9, "pico"),            # -> S5 travelling
    (9.0, "My fav whoosh.mp3", -9, "pico"),            # chicote -> S6
    (9.35, "Lit cloth roll 2 .mp3", -16, "inicio"),    # OC irritado sobe
    (9.55, "Lit shock.mp3", -9, "inicio"),             # "C++" aparece
    (10.4, "Dark whoosh2.mp3", -8, "pico"),            # entra no corredor
    (13.9, "Quick whoosh2.mp3", -10, "pico"),          # -> R2
    (17.28, "Lit whoosh impact.mp3", -7, "pico"),      # "RUST"
    (17.9, "woosh #2.mp3", -11, "pico"),               # -> R3
    (20.6, "Lit energy release .mp3", -10, "inicio"),  # INTERFACES acende
    (21.9, "woosh #4.mp3", -11, "pico"),               # -> R4
    (22.84, "Lit hit 2.mp3", -9, "inicio"),            # engrenagens acendem
    (23.0, "Lit cloth roll 3.mp3", -16, "inicio"),     # OC empolgado chega
    (26.5, "Bass buildup #1.mp3", -8, "fim"),          # sobe até a revelação (música já calou)
    (26.5, "Thunder #1.mp3", -6, "inicio"),            # Godot vira Rusdot
    (26.5, "Bass Explosion.mp3", -9, "inicio"),
    (29.5, "woosh #6.mp3", -12, "pico"),               # -> FIN
    (30.2, "dodge whoosh #1.mp3", -9, "pico"),         # OC voa para dentro
    (30.4, "Lit Dual impact.mp3", -9, "inicio"),       # OC assenta
]
# cartões encaixando: "7 DIAS" (cada letra assenta em t+0,33), módulos (chega+0,2) e letras RUSDOT (t+0,33)
for k in range(5):
    EVENTOS.append((3.08 + k * 0.1 + 0.33, GRAMPOS[k % 4], -15, "inicio"))
for k, t in enumerate([14.1, 14.8, 15.76, 16.42]):
    EVENTOS.append((t + 0.2, GRAMPOS[k], -8, "inicio"))
for k in range(6):
    EVENTOS.append((27.0 + k * 0.13 + 0.33, GRAMPOS[k % 4], -14, "inicio"))
# painéis do corredor virando de C++ para Rust: tique baixinho em cada virada
for k in range(9):
    EVENTOS.append((10.4 + 3.5 * (k * 800 + 1500) / 8000, GRAMPOS[k % 4], -22, "inicio"))


def main():
    n = int(SR * DUR)
    sfx = np.zeros((n, 2), dtype=np.float32)
    cache = {}
    for t, arq, db, modo in EVENTOS:
        if arq not in cache:
            cache[arq] = ler(PACK / arq)
        x = cache[arq] * (10 ** (db / 20))
        ref = {"pico": pico(x), "inicio": 0, "fim": len(x)}[modo]
        i0 = int(t * SR) - ref
        a, b = max(i0, 0), min(i0 + len(x), n)
        if b > a:
            sfx[a:b] += x[a - i0:b - i0]
    sfx *= 10 ** (-3 / 20) / max(1e-6, np.abs(sfx).max())  # pico em -3 dBFS
    escrever(AUDIO / "sfx3d_v02.wav", sfx)

    # música: some de 24,8 a 26,5 s (silêncio antes da revelação) e volta no impacto
    m = ler(AUDIO / "musica3d_v01.wav")[:n]
    tt = np.arange(len(m)) / SR
    g = np.interp(tt, [0, 24.5, 24.8, 26.45, 26.6, DUR], [1, 1, 0, 0, 1, 1]).astype(np.float32)
    escrever(AUDIO / "musica3d_v02.wav", m * g[:, None])
    print(f"{len(EVENTOS)} eventos de SFX -> sfx3d_v02.wav; musica3d_v02.wav com silêncio 24,8–26,5 s")


def escrever(caminho, x):
    if caminho.exists():
        raise SystemExit(f"{caminho.name} já existe: não sobrescrevo (versione)")
    subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ac", "2", "-ar", str(SR), "-i", "-", "-c:a", "pcm_s24le",
                    str(caminho)], input=x.astype(np.float32).tobytes(), check=True)


if __name__ == "__main__":
    main()
