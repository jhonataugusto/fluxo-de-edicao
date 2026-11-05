"""Extrai os contornos dos ícones (Godot azul e Rusdot) em camadas para virar geometria 3D no Blender.

Uso: python -P contornos.py
Saída: assets/icone_godot.json e assets/icone_rusdot.json
       {aspecto, camadas[{papel: corpo|claro|escuro, polys[[[x,y],...]]}]} — altura 1, centro em 0, y para cima.
"""
import json, os
import cv2
import numpy as np

ASSETS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")


def ler(nome):
    return cv2.imdecode(np.fromfile(os.path.join(ASSETS, nome), np.uint8), cv2.IMREAD_UNCHANGED)


def polys(mask, h, w, area_min=0.0004):
    mask = cv2.morphologyEx(mask.astype(np.uint8) * 255, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    cont, _ = cv2.findContours(mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    out = []
    for c in cont:
        if cv2.contourArea(c) < area_min * h * h:
            continue
        c = cv2.approxPolyDP(c, 1.2, True)[:, 0, :].astype(float)
        if len(c) < 3:
            continue
        out.append([[round((x - w / 2) / h, 4), round((h / 2 - y) / h, 4)] for x, y in c])
    return out


for arq, nome in (("godot_azul.png", "godot"), ("rusdot.png", "rusdot")):
    im = ler(arq)
    h, w = im.shape[:2]
    a = im[:, :, 3] > 128
    hsv = cv2.cvtColor(im[:, :, :3], cv2.COLOR_BGR2HSV)
    claro = a & (hsv[:, :, 2] > 200) & (hsv[:, :, 1] < 50)
    escuro = a & (hsv[:, :, 2] < 70)
    dados = {"aspecto": round(w / h, 4), "camadas": [
        {"papel": "corpo", "polys": polys(a, h, w)},
        {"papel": "claro", "polys": polys(claro, h, w)},
        {"papel": "escuro", "polys": polys(escuro, h, w)}]}
    json.dump(dados, open(os.path.join(ASSETS, f"icone_{nome}.json"), "w"))
    print(nome, {c["papel"]: (len(c["polys"]), sum(len(p) for p in c["polys"])) for c in dados["camadas"]})
