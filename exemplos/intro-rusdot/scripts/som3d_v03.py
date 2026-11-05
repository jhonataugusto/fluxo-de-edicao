"""SFX da intro 3D v03 com o "Ultimate Sfx Pack" (fluxo-de-edicao/assets/Sfx/Ultimate sfx pack).

Gera audio/sfx3d_v03.wav (48 kHz estéreo, 32,3 s). A música continua a musica3d_v02.wav (silêncio antes da revelação).
Mesma lógica do som3d_v02.py: (tempo, arquivo, ganho dB, modo); "pico" alinha o ponto mais forte do som ao tempo,
"inicio" alinha o começo, "fim" termina no tempo. Sons escolhidos pelo clima "documento/tech": whooshes curtos,
impactos secos, faísca elétrica no código, dados digitais; nada de luta, sangue ou vozes de anime.
"""
import subprocess
from pathlib import Path

import numpy as np

SR, DUR = 48000, 32.3
PACK = Path(r"C:\Users\jhonata\Documents\fluxo-de-edicao\assets\Sfx\Ultimate sfx pack\Ultimate Sfx Pack Collection")
AUDIO = Path(__file__).resolve().parent.parent / "audio"
W, I, S, G = "WHOOSHES N BUILDUPS/", "IMPACTS/", "SPECIAL/", "Sfx (110+)/"


def ler(caminho):
    bruto = subprocess.run(["ffmpeg", "-v", "error", "-i", str(caminho), "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                           capture_output=True, check=True).stdout
    return np.frombuffer(bruto, dtype=np.float32).reshape(-1, 2).copy()


def pico(x):
    env = np.convolve(np.abs(x).mean(axis=1), np.ones(960) / 960, mode="same")  # janela de 20 ms
    return int(env.argmax())


GRAMPOS = [G + f"sfx_hit_grapple0{k}.wav" for k in (1, 2, 3, 4)]
EVENTOS = [
    (0.0, G + "digital_data_13.wav", -22, "inicio"),   # cama digital de abertura (tema: código)
    (1.5, W + "Swoosh.wav", -10, "pico"),              # S1 -> S2
    (2.19, I + "Another impact.wav", -7, "inicio"),    # RUST assenta
    (3.0, W + "Zoom.wav", -9, "pico"),                 # -> S3 (dutch)
    (3.35, W + "Cloth.wav", -14, "inicio"),            # OC cai no quadro
    (4.5, G + "Fast Swish.wav", -11, "pico"),          # -> S4
    (6.0, G + "Power_Wooshes_01.wav", -9, "pico"),     # -> S5 travelling
    (9.0, W + "SPEED WHOOSH.wav", -8, "pico"),         # chicote -> S6
    (9.35, W + "Cloth 2.wav", -15, "inicio"),          # OC irritado sobe
    (9.55, G + "Electrical Spark.mp3", -10, "inicio"), # "C++" aparece
    (10.4, G + "spacial whoosh.wav", -8, "pico"),      # entra no corredor
    (13.9, G + "Power_Wooshes_03.wav", -10, "pico"),   # -> R2
    (17.28, G + "Epic_Hit_-_9.wav", -8, "inicio"),     # "RUST"
    (17.9, G + "Epic_Swishes_01.wav", -11, "pico"),    # -> R3
    (20.6, G + "Anime Shine Sound Effect.mp3", -13, "inicio"),  # INTERFACES acende
    (21.9, G + "woosh 12.wav", -10, "pico"),           # -> R4
    (22.84, I + "Small impact.wav", -8, "inicio"),     # engrenagens acendem
    (22.84, S + "Rotating metal.wav", -18, "inicio"),  # giro das engrenagens
    (23.0, W + "Cloth.wav", -15, "inicio"),            # OC empolgado chega
    (26.5, W + "Electric buildup.wav", -10, "fim"),    # sobe até a revelação (música já calou)
    (26.5, G + "spacial warp impact 2.mp3", -6, "inicio"),  # Godot vira Rusdot
    (26.5, I + "Thunder slam.wav", -10, "inicio"),
    (29.5, W + "Swoosh.wav", -11, "pico"),             # -> FIN
    (30.2, G + "Sonic Whoosh.wav", -10, "pico"),       # OC voa para dentro
    (30.4, I + "Landing.wav", -8, "inicio"),           # OC assenta
]
# cartões encaixando: "7 DIAS" (cada letra assenta em t+0,33), módulos (chega+0,2) e letras RUSDOT (t+0,33)
for k in range(5):
    EVENTOS.append((3.08 + k * 0.1 + 0.33, GRAMPOS[k % 4], -15, "inicio"))
for k, t in enumerate([14.1, 14.8, 15.76, 16.42]):
    EVENTOS.append((t + 0.2, G + ("default impact.wav" if k % 2 == 0 else "deep impact.wav"), -9, "inicio"))
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
    escrever(AUDIO / "sfx3d_v03.wav", sfx)
    print(f"{len(EVENTOS)} eventos de SFX -> sfx3d_v03.wav")


def escrever(caminho, x):
    if caminho.exists():
        raise SystemExit(f"{caminho.name} já existe: não sobrescrevo (versione)")
    subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ac", "2", "-ar", str(SR), "-i", "-", "-c:a", "pcm_s24le",
                    str(caminho)], input=x.astype(np.float32).tobytes(), check=True)


if __name__ == "__main__":
    main()
