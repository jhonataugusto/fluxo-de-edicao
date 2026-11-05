"""Corta os silêncios de uma fala usando os tempos por palavra da transcrição.

Uso: python -P cortar_silencios.py <audio> --transcricao transcricao.json --saida <pasta> [--versao 01]
     [--respiro 0.10] [--antes 0.04] [--depois 0.08]
Saída (nunca sobrescreve): voz_cortada_v<versao>.wav, cortes_v<versao>.json ({trechos[{de,ate}], duracao_antes_s,
duracao_depois_s}) e transcricao_cortada_v<versao>.json (mesmo formato da transcrição, com os tempos novos).
Silêncio entre palavras maior que o respiro vira respiro; emendas com micro-fade de 8 ms para não estalar.
"""
import argparse, json, os, subprocess, sys
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("audio")
ap.add_argument("--transcricao", required=True)
ap.add_argument("--saida", required=True)
ap.add_argument("--versao", default="01")
ap.add_argument("--respiro", type=float, default=0.10, help="silêncio máximo mantido entre palavras (s)")
ap.add_argument("--antes", type=float, default=0.04, help="folga antes de cada palavra (s)")
ap.add_argument("--depois", type=float, default=0.08, help="folga depois de cada palavra (s)")
a = ap.parse_args()

SR = 48000
saidas = [os.path.join(a.saida, f"{n}_v{a.versao}.{e}") for n, e in
          (("voz_cortada", "wav"), ("cortes", "json"), ("transcricao_cortada", "json"))]
if any(os.path.exists(s) for s in saidas):
    sys.exit(f"versão {a.versao} já existe em {a.saida}: use outra --versao")

trans = json.load(open(a.transcricao, encoding="utf-8"))
palavras = trans["palavras"]
pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", a.audio, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                     capture_output=True, check=True).stdout
x = np.frombuffer(pcm, np.float32).reshape(-1, 2)
dur = len(x) / SR

# Trechos a manter: cada palavra com folga; une palavras cujo vão (já com folgas) cabe no respiro
trechos = []
for w in palavras:
    de, ate = max(0.0, w["inicio"] - a.antes), min(dur, w["fim"] + a.depois)
    if trechos and de - trechos[-1][1] <= a.respiro:
        trechos[-1][1] = max(trechos[-1][1], ate)
    else:
        trechos.append([de, ate])

# Segunda passada pela energia: o Whisper estica palavras por cima das pausas; silêncio real dentro de um trecho
# (abaixo do limiar por mais que o respiro + folgas) também vira respiro.
JAN = int(0.01 * SR)
rms = np.sqrt((x.mean(1)[: len(x) // JAN * JAN].reshape(-1, JAN) ** 2).mean(1) + 1e-12)
db = 20 * np.log10(rms)
limiar = max(np.percentile(db, 20) + 6, db.max() - 45)  # chão de ruído + 6 dB, nunca acima de pico − 45 dB
silencio = db < limiar
minimo = a.respiro + a.antes + a.depois
refinados = []
for de, ate in trechos:
    i0, i1 = int(de / 0.01), int(ate / 0.01)
    atual, k = de, i0
    while k < i1:
        if silencio[k]:
            j = k
            while j < i1 and silencio[j]:
                j += 1
            if (j - k) * 0.01 >= minimo:
                refinados.append([atual, k * 0.01 + a.depois])
                atual = j * 0.01 - a.antes
            k = j
        else:
            k += 1
    refinados.append([atual, ate])
trechos = [t for t in refinados if t[1] - t[0] > 0.05]

# Monta o áudio: trecho + respiro (silêncio) entre trechos, micro-fade nas emendas
fade = int(0.008 * SR)
rampa = np.linspace(0, 1, fade, dtype=np.float32)[:, None]
pedacos, mapa, t_novo = [], [], 0.0
for k, (de, ate) in enumerate(trechos):
    p = x[int(de * SR):int(ate * SR)].copy()
    if len(p) > 2 * fade:
        p[:fade] *= rampa
        p[-fade:] *= rampa[::-1]
    mapa.append((de, ate, t_novo))
    pedacos.append(p)
    t_novo += len(p) / SR
    if k < len(trechos) - 1:
        pedacos.append(np.zeros((int(a.respiro * SR), 2), np.float32))
        t_novo += a.respiro
y = np.concatenate(pedacos)


def novo_tempo(t):
    for de, ate, t0 in mapa:
        if de <= t <= ate:
            return round(t0 + (t - de), 3)
    # caiu num silêncio removido: prende na borda do trecho seguinte (ou no fim do anterior)
    for de, ate, t0 in mapa:
        if t < de:
            return round(t0, 3)
    de, ate, t0 = mapa[-1]
    return round(t0 + (ate - de), 3)


novas = [{**w, "inicio": novo_tempo(w["inicio"]), "fim": novo_tempo(w["fim"])} for w in palavras]
frases = []
for s in trans["frases"]:
    ws = [n for n, w in zip(novas, palavras) if s["inicio"] - 0.05 <= w["inicio"] <= s["fim"] + 0.05]
    if ws:
        frases.append({"texto": s["texto"], "inicio": ws[0]["inicio"], "fim": ws[-1]["fim"]})

subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-c:a",
                "pcm_s16le", saidas[0]], input=np.clip(y, -1, 1).astype(np.float32).tobytes(), check=True)
json.dump({"trechos": [{"de": round(d, 3), "ate": round(t, 3)} for d, t in trechos], "respiro_s": a.respiro,
           "duracao_antes_s": round(dur, 3), "duracao_depois_s": round(len(y) / SR, 3)},
          open(saidas[1], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump({**trans, "duracao_s": round(len(y) / SR, 3), "palavras": novas, "frases": frases},
          open(saidas[2], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"{dur:.2f} s -> {len(y) / SR:.2f} s ({len(trechos)} trechos, {len(trechos) - 1} emendas)")
