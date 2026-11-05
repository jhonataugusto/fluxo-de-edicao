"""Mede uma referência de edição: cortes, câmera, movimento de elementos, flashes e folhas de quadros.

Uso: python -P analisar_ref.py <video.mp4> [--saida <pasta>] [--passo-folha 6]
Saída: <nome>_medidas.json, <nome>_folha_NN.jpg (quadros a cada N frames) e <nome>_resumo.jpg.
"""
import argparse, json, math, os, subprocess
import cv2
import numpy as np
from scenedetect import detect, ContentDetector

ap = argparse.ArgumentParser()
ap.add_argument("video")
ap.add_argument("--saida")
ap.add_argument("--passo-folha", type=int, default=0, help="frames entre quadros da folha (0 = ~5 por segundo)")
a = ap.parse_args()

nome = os.path.splitext(os.path.basename(a.video))[0]
saida = a.saida or os.path.dirname(os.path.abspath(a.video))
os.makedirs(saida, exist_ok=True)

cap = cv2.VideoCapture(a.video)
fps = cap.get(cv2.CAP_PROP_FPS)
passo = a.passo_folha or max(1, round(fps / 5))

# 1. Cortes
cenas = [(s.get_seconds(), e.get_seconds()) for s, e in detect(a.video, ContentDetector(threshold=27))]
cortes = [s for s, _ in cenas[1:]]

# 2. Câmera (afim global por fluxo óptico + RANSAC), elementos (resíduo) e diferença de brilho
W = 480
camera, residuo, diff, brilho, quadros = [], [], [], [], []
prev = None
i = 0
while True:
    ok, f = cap.read()
    if not ok:
        break
    t = i / fps
    h = int(f.shape[0] * W / f.shape[1])
    g = cv2.cvtColor(cv2.resize(f, (W, h)), cv2.COLOR_BGR2GRAY)
    brilho.append(float(g.mean()))
    if i % passo == 0:
        quadros.append((t, cv2.resize(f, (320, int(320 * f.shape[0] / f.shape[1])))))
    if prev is not None:
        diff.append(float(cv2.absdiff(g, prev).mean()))
        pts = cv2.goodFeaturesToTrack(prev, 300, 0.01, 8)
        reg = {"t": round(t, 3), "escala": 1.0, "dx": 0.0, "dy": 0.0, "rot": 0.0, "ok": False}
        res = 0.0
        if pts is not None and len(pts) >= 12:
            nxt, st, _ = cv2.calcOpticalFlowPyrLK(prev, g, pts, None)
            p0, p1 = pts[st == 1], nxt[st == 1]
            if len(p0) >= 12:
                M, inl = cv2.estimateAffinePartial2D(p0, p1, method=cv2.RANSAC, ransacReprojThreshold=2.0)
                if M is not None:
                    s = math.hypot(M[0, 0], M[1, 0])
                    reg.update(escala=round(s, 5), dx=round(M[0, 2] / W, 5), dy=round(M[1, 2] / W, 5),
                               rot=round(math.degrees(math.atan2(M[1, 0], M[0, 0])), 3),
                               ok=bool(inl.mean() > 0.5))
                    pred = (M[:, :2] @ p0.T).T + M[:, 2]
                    res = float(np.median(np.linalg.norm(p1 - pred, axis=1)))
        camera.append(reg)
        residuo.append(res)
    prev = g
    i += 1
cap.release()

# 3. Resumo
dur = i / fps
validos = [c for c in camera if c["ok"]]
zoom = [abs(c["escala"] - 1) for c in validos]
desl = [math.hypot(c["dx"], c["dy"]) for c in validos]
mov = [z > 0.0008 or d > 0.0015 for z, d in zip(zoom, desl)]
# punch-in: zoom acumulado > 6% em até 4 frames
punches = []
for k in range(len(camera) - 4):
    acc = np.prod([camera[k + j]["escala"] for j in range(4)])
    if acc > 1.06 and (not punches or camera[k]["t"] - punches[-1] > 0.3):
        punches.append(camera[k]["t"])
d = np.array(diff)
flashes = [round(k / fps, 2) for k in range(1, len(brilho) - 1)
           if brilho[k] - brilho[k - 1] > 25 and brilho[k] - brilho[k + 1] > 15]
durs = [e - s for s, e in cenas] or [dur]

lufs = None
try:
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", a.video, "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True, errors="ignore")
    linhas = [l for l in r.stderr.splitlines() if l.strip().startswith("I:")]
    lufs = float(linhas[-1].split()[1]) if linhas else None
except Exception:
    pass

resumo = {
    "duracao_s": round(dur, 2), "fps": round(fps, 3),
    "cortes": len(cortes), "cortes_por_10s": round(len(cortes) / dur * 10, 2),
    "duracao_media_plano_s": round(float(np.mean(durs)), 2),
    "duracao_mediana_plano_s": round(float(np.median(durs)), 2),
    "camera_em_movimento_pct": round(100 * sum(mov) / max(1, len(mov)), 1),
    "zoom_medio_por_s_pct": round(100 * float(np.mean(zoom)) * fps, 2) if zoom else 0,
    "punch_ins": [round(p, 2) for p in punches],
    "movimento_elementos_mediano_px480": round(float(np.median(residuo)), 3) if residuo else 0,
    "diff_media": round(float(d.mean()), 2) if len(d) else 0,
    "picos_diff_s": [round((k + 1) / fps, 2) for k in np.where(d > d.mean() + 3 * d.std())[0]] if len(d) else [],
    "flashes_s": flashes,
    "lufs_integrado": lufs,
}
json.dump({"video": a.video, "resumo": resumo, "cenas": [{"inicio": round(s, 3), "fim": round(e, 3)} for s, e in cenas],
           "camera": camera, "diff": [round(x, 2) for x in diff], "brilho": [round(x, 1) for x in brilho]},
          open(os.path.join(saida, f"{nome}_medidas.json"), "w", encoding="utf-8"), ensure_ascii=False)

# 4. Folhas de quadros (6 colunas x 5 linhas por folha, corte marcado em vermelho) e resumo (8 quadros)
def marca(img, t, corte):
    img = img.copy()
    cv2.rectangle(img, (0, 0), (92, 22), (0, 0, 0), -1)
    cv2.putText(img, f"{t:6.2f}s", (4, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    if corte:
        cv2.rectangle(img, (0, 0), (img.shape[1] - 1, img.shape[0] - 1), (0, 0, 255), 3)
    return img

def grade(itens, cols):
    hq, wq = itens[0][1].shape[:2]
    linhas = math.ceil(len(itens) / cols)
    tela = np.zeros((linhas * hq, cols * wq, 3), np.uint8)
    for k, (t, q) in enumerate(itens):
        corte = any(0 <= t - c < passo / fps for c in cortes)
        tela[(k // cols) * hq:(k // cols + 1) * hq, (k % cols) * wq:(k % cols + 1) * wq] = marca(q, t, corte)
    return tela

por_folha = 30
for k in range(0, len(quadros), por_folha):
    cv2.imwrite(os.path.join(saida, f"{nome}_folha_{k // por_folha + 1:02d}.jpg"), grade(quadros[k:k + por_folha], 6),
                [cv2.IMWRITE_JPEG_QUALITY, 85])
idx = np.linspace(0, len(quadros) - 1, 8).astype(int)
cv2.imwrite(os.path.join(saida, f"{nome}_resumo.jpg"), grade([quadros[j] for j in idx], 4), [cv2.IMWRITE_JPEG_QUALITY, 85])

print(json.dumps(resumo, ensure_ascii=False, indent=1))
