"""Desenha guias de composição sobre quadros renderizados e aponta conteúdo forte em zonas proibidas.

Uso: python -P guias_quadro.py quadro.png [outro.png ...]
Grava <quadro>_guias.png ao lado e imprime alertas por quadro.

Guias (proporcionais a 1920x1080, valem para qualquer tamanho 16:9):
- terços (branco) e centro (cruz);
- área segura de gráficos, 5 % por lado (verde) — EBU R95;
- faixa de baixo, 15 % (vermelho): barra de progresso, controles e legendas do YouTube;
- faixa de cima, 10 % (laranja): título e botões ao pausar.
Alerta = parte relevante da zona com brilho alto e borda forte (provável texto ou objeto importante).
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ZONAS = {  # nome: (x0, y0, x1, y1) em fração do quadro, limiar de alerta
    # limiares calibrados na intro do Rusdot: a base do logo Godot invadindo a faixa de baixo deu 0,4 %,
    # "MOTORES" 1,2 %, "ENGINE DE JOGOS" na faixa de cima 0,9 %. Texto fino e escuro pode escapar: olhe o _guias.png.
    "faixa de baixo (UI do YouTube)": ((0.0, 0.85, 1.0, 1.0), 0.003),
    "faixa de cima (título ao pausar)": ((0.0, 0.0, 1.0, 0.10), 0.004),
    "borda esquerda fora da área segura": ((0.0, 0.0, 0.05, 1.0), 0.020),
    "borda direita fora da área segura": ((0.95, 0.0, 1.0, 1.0), 0.020),
}


def mapa_forte(img):
    """Pixels claros com borda forte: aproxima onde há texto ou contorno nítido."""
    g = np.asarray(img.convert("L"), dtype=np.float32) / 255.0
    gx = np.abs(np.diff(g, axis=1, prepend=g[:, :1]))
    gy = np.abs(np.diff(g, axis=0, prepend=g[:1, :]))
    return (g > 0.62) & ((gx + gy) > 0.18), g


def analisar(caminho):
    img = Image.open(caminho).convert("RGB")
    w, h = img.size
    forte, lum = mapa_forte(img)
    alertas = []
    for nome, ((x0, y0, x1, y1), limiar) in ZONAS.items():
        z = forte[int(y0 * h):int(y1 * h), int(x0 * w):int(x1 * w)]
        frac = float(z.mean()) if z.size else 0.0
        if frac > limiar:
            alertas.append(f"{nome}: {frac * 100:.1f}% de conteúdo forte")
    # onde está o "peso" visual (centro de massa do conteúdo forte) em relação aos terços
    ys, xs = np.nonzero(forte)
    foco = None
    if len(xs) > 50:
        foco = (xs.mean() / w, ys.mean() / h)
    # quanto do quadro está estourado (flash) ou vazio
    estouro = float((lum > 0.92).mean())
    vazio = float((lum < 0.04).mean())
    if estouro > 0.25:
        alertas.append(f"{estouro * 100:.0f}% do quadro quase branco (flash forte: contar flashes/s)")
    if vazio > 0.6:
        alertas.append(f"{vazio * 100:.0f}% do quadro quase preto (fundo aparecendo?)")

    over = img.copy()
    d = ImageDraw.Draw(over, "RGBA")
    d.rectangle([0, int(0.85 * h), w, h], fill=(255, 40, 40, 70))
    d.rectangle([0, 0, w, int(0.10 * h)], fill=(255, 150, 0, 50))
    d.rectangle([int(0.05 * w), int(0.05 * h), int(0.95 * w), int(0.95 * h)], outline=(60, 255, 120, 200), width=2)
    for k in (1, 2):
        d.line([(w * k / 3, 0), (w * k / 3, h)], fill=(255, 255, 255, 120), width=1)
        d.line([(0, h * k / 3), (w, h * k / 3)], fill=(255, 255, 255, 120), width=1)
    d.line([(w / 2 - 12, h / 2), (w / 2 + 12, h / 2)], fill=(255, 255, 255, 160), width=1)
    d.line([(w / 2, h / 2 - 12), (w / 2, h / 2 + 12)], fill=(255, 255, 255, 160), width=1)
    if foco:
        fx, fy = foco[0] * w, foco[1] * h
        d.ellipse([fx - 9, fy - 9, fx + 9, fy + 9], outline=(46, 230, 240, 255), width=3)
    saida = Path(caminho).with_name(Path(caminho).stem + "_guias.png")
    over.save(saida)

    foco_txt = f"peso visual em x={foco[0]:.2f}, y={foco[1]:.2f}" if foco else "sem conteúdo forte"
    print(f"{Path(caminho).name}: {foco_txt} -> {saida.name}")
    for a in alertas:
        print(f"  ALERTA {a}")
    if not alertas:
        print("  ok")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for arq in sys.argv[1:]:
        analisar(arq)
