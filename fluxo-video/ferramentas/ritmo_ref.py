"""Ritmo de uma referência: BPM da trilha, quanto os cortes caem na batida e como os intervalos aceleram/respiram.

Uso: python -P ritmo_ref.py <video.mp4> --medidas <ref>_medidas.json
Saída: <ref>_ritmo.json ({bpm, cortes_na_batida_pct, cortes_em_ataque_pct, intervalos_s[], onsets_s[]}) ao lado das medidas.
Cortes vêm do analisar_ref.py. "Na batida" = até 2 quadros de uma batida da grade de BPM; "em ataque" = até 2 quadros
de um ataque forte do som (onset), seja música, efeito ou fala.
"""
import argparse, json, subprocess
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("video")
ap.add_argument("--medidas", required=True)
a = ap.parse_args()

SR, HOP = 22050, 512
med = json.load(open(a.medidas, encoding="utf-8"))
fps = med["resumo"]["fps"]
tol = 2 / fps
cortes = [c["inicio"] for c in med["cenas"][1:]]

pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", a.video, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                     capture_output=True, check=True).stdout
x = np.frombuffer(pcm, np.float32)

# Força de ataque: fluxo espectral positivo (log), por janela
win = np.hanning(2048)
quadros = np.lib.stride_tricks.sliding_window_view(np.pad(x, 1024), 2048)[::HOP] * win
mag = np.log1p(np.abs(np.fft.rfft(quadros, axis=1)))
fluxo = np.maximum(np.diff(mag, axis=0), 0).sum(1)
fluxo = (fluxo - fluxo.mean()) / (fluxo.std() + 1e-9)
t_env = (np.arange(len(fluxo)) + 1) * HOP / SR

# Ataques: picos locais acima de 1,5 desvio, separados por >= 0,1 s
onsets = []
for i in range(1, len(fluxo) - 1):
    if fluxo[i] > 1.5 and fluxo[i] >= fluxo[i - 1] and fluxo[i] >= fluxo[i + 1]:
        if not onsets or t_env[i] - onsets[-1] >= 0.1:
            onsets.append(float(t_env[i]))

# BPM por autocorrelação da força de ataque (60–180 BPM) e fase da grade pelo melhor alinhamento
env = np.maximum(fluxo, 0)
ac = np.correlate(env, env, "full")[len(env) - 1:]
lags = np.arange(len(ac)) * HOP / SR
faixa = (lags >= 60 / 180) & (lags <= 60 / 60)
periodo = lags[faixa][np.argmax(ac[faixa])]
bpm = 60 / periodo
fases = np.linspace(0, periodo, 64, endpoint=False)


def grade(f):
    return np.arange(f, t_env[-1], periodo)


pont = [np.interp(grade(f), t_env, env).sum() for f in fases]
batidas = grade(fases[int(np.argmax(pont))])


def perto(ts, alvos):
    if not len(alvos) or not ts:
        return 0.0
    return 100 * np.mean([np.min(np.abs(np.asarray(alvos) - t)) <= tol for t in ts])


intervalos = np.diff([0] + cortes + [med["resumo"]["duracao_s"]]).round(2).tolist()
saida = {"bpm": round(float(bpm), 1), "cortes": len(cortes),
         "cortes_na_batida_pct": round(perto(cortes, batidas), 1),
         "acaso_pct": round(min(100.0, 100 * 2 * tol / periodo), 1),  # o que cairia na batida por sorte
         "cortes_em_ataque_pct": round(perto(cortes, onsets), 1),
         "ataques_por_s": round(len(onsets) / max(t_env[-1], 1e-9), 2),
         "intervalos_s": intervalos, "onsets_s": [round(o, 3) for o in onsets]}
dest = a.medidas.replace("_medidas.json", "_ritmo.json")
json.dump(saida, open(dest, "w", encoding="utf-8"), ensure_ascii=False)
print(json.dumps({k: v for k, v in saida.items() if k != "onsets_s"}, ensure_ascii=False))
