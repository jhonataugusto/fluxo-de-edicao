"""Gera o FCP7 XML da intro de teste para o FilmCraft (uma motion por clipe, trilhas separadas).

Uso: python -P gerar_xml.py [versao]   -> _CLAUDE/intro_teste_v<versao>.xml (padrão 01; nunca sobrescreve outra versão)
"""
import os, subprocess, sys
from xml.sax.saxutils import escape

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # _CLAUDE
FPS = 30
TOTAL = 1100
VERSAO = sys.argv[1] if len(sys.argv) > 1 else "01"

CENAS = {"c1": 0, "c2": 72, "c3": 159, "c4": 342, "c5": 609, "c6": 865, "c7": 978}
CLAROES = [71, 341, 608, 888, 977]


def quadros(caminho):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", caminho],
                         capture_output=True, text=True, check=True).stdout
    return round(float(out) * FPS)


def url(caminho):
    return "file:///" + caminho.replace("\\", "/")


RATE = f"<rate><timebase>{FPS}</timebase><ntsc>FALSE</ntsc></rate>"
_id = [0]


def clip(caminho, inicio, tipo):
    _id[0] += 1
    dur = quadros(caminho)
    nome = escape(os.path.basename(caminho))
    if tipo == "video":
        media = "<video><samplecharacteristics><width>1920</width><height>1080</height></samplecharacteristics></video>"
        extra = "<alphatype>straight</alphatype>" if not nome.startswith("fundo") else ""
        fonte = ""
    else:
        media = ("<audio><samplecharacteristics><depth>16</depth><samplerate>48000</samplerate></samplecharacteristics>"
                 "<channelcount>2</channelcount></audio>")
        extra = ""
        fonte = "<sourcetrack><mediatype>audio</mediatype><trackindex>1</trackindex></sourcetrack>"
    return (f'<clipitem id="clip-{_id[0]}"><name>{nome}</name><duration>{dur}</duration>{RATE}'
            f"<start>{inicio}</start><end>{inicio + dur}</end><in>0</in><out>{dur}</out>"
            f'<file id="file-{_id[0]}"><name>{nome}</name><pathurl>{escape(url(caminho))}</pathurl>'
            f"<duration>{dur}</duration>{RATE}<media>{media}</media></file>{fonte}{extra}</clipitem>")


p = lambda *a: os.path.join(BASE, *a)
v1 = clip(p("fundo.mov"), 0, "video")
v2 = "".join(clip(p("motion", f"{c}.mov"), q, "video") for c, q in CENAS.items())
v3 = "".join(clip(p("flashes", f"flash_{q:04d}.mov"), q, "video") for q in CLAROES)
a1 = clip(p("audio", "voz.wav"), 0, "audio")
a2 = clip(p("audio", "sfx_transicoes.wav"), 0, "audio")
a3 = clip(p("audio", "sfx_digitacao.wav"), 0, "audio")

xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xmeml>
<xmeml version="4"><sequence id="seq-1"><name>Intro teste v{VERSAO} - dossie animado</name>
<duration>{TOTAL}</duration>{RATE}
<media>
<video><format><samplecharacteristics>{RATE}<width>1920</width><height>1080</height>
<pixelaspectratio>square</pixelaspectratio></samplecharacteristics></format>
<track>{v1}</track>
<track>{v2}</track>
<track>{v3}</track>
</video>
<audio>
<track>{a1}</track>
<track>{a2}</track>
<track>{a3}</track>
</audio>
</media></sequence></xmeml>
"""
saida = p(f"intro_teste_v{VERSAO}.xml")
if os.path.exists(saida):
    sys.exit(f"{saida} já existe: use outra versão")
open(saida, "w", encoding="utf-8").write(xml)
print(saida)
