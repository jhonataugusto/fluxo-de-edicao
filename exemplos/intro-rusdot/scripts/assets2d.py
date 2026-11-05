"""Gera as imagens 2D (PNG com transparência) que viram camadas 3D no EffectCraft.

Uso: python -P assets2d.py   -> _CLAUDE/assets2d/*.png
Paleta do vídeo: laranja Rust (acento), azul Godot ("antes"), grafite, osso. Fontes do perfil jonato.
"""
import math, os, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS, OUT = os.path.join(BASE, "assets"), os.path.join(BASE, "assets2d")
FONTES = r"C:\Users\jhonata\Documents\fluxo-video\perfis\jonato\fontes"
os.makedirs(OUT, exist_ok=True)
LAR, AZUL, OSSO, GRAF, GRAF2, CINZA = (232, 68, 28), (71, 140, 191), (237, 230, 218), (24, 24, 29), (33, 32, 41), (138, 133, 151)
TIT, MONO, MONOB = "BigShouldersDisplay-Black.ttf", "IBMPlexMono-Regular.ttf", "IBMPlexMono-Bold.ttf"


def F(nome, tam):
    return ImageFont.truetype(os.path.join(FONTES, nome), tam)


def salvar(im, nome):
    im.save(os.path.join(OUT, nome + ".png"))


def com_brilho(im, cor, raio=18, forca=1.6):
    """Glow: cópia borrada da silhueta, na cor do acento, por trás."""
    a = im.split()[3].filter(ImageFilter.GaussianBlur(raio)).point(lambda v: min(255, int(v * forca)))
    g = Image.new("RGBA", im.size, cor + (0,))
    g.putalpha(a)
    return Image.alpha_composite(g, im)


def texto(s, fonte, tam, cor, brilho=None, pad=60):
    f = F(fonte, tam)
    x0, y0, x1, y1 = f.getbbox(s)
    im = Image.new("RGBA", (x1 - x0 + 2 * pad, y1 - y0 + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((pad - x0, pad - y0), s, font=f, fill=cor + (255,))
    return com_brilho(im, brilho) if brilho else im


def card(w, h, raio=28, borda=None, fundo=GRAF):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((4, 4, w - 5, h - 5), raio, fill=fundo + (255,),
                                         outline=(borda or (60, 58, 70)) + (255,), width=4 if borda else 2)
    return im


# textos
salvar(texto("RUST", TIT, 330, LAR, brilho=LAR), "txt_rust")
salvar(texto("C++", TIT, 300, AZUL, brilho=AZUL), "txt_cpp")
salvar(texto("ENGINE DE JOGOS", TIT, 150, OSSO), "txt_engine")
salvar(texto("MOTORES", TIT, 170, OSSO), "txt_motores")
salvar(texto("EU RECRIEI A GODOT", TIT, 140, OSSO), "txt_recriei")
for ch in "7DIAS":
    salvar(texto(ch, MONOB, 300, LAR if ch == "7" else OSSO, brilho=LAR if ch == "7" else None), f"ch_{ch}")
for ch in "RUSDOT":
    salvar(texto(ch, TIT, 230, OSSO), f"rd_{ch}")
salvar(texto("GAME ENGINE // escrita em Rust", MONO, 46, CINZA, pad=20), "txt_sub")

# painéis de código
CPP = ["class Node : public Object {", "    GDCLASS(Node, Object);", "public:", "    void _process(double dt);",
       "    Vector2 position;", "};"]
RUST = ["pub struct Node {", "    pub position: Vec2,", "}", "impl Node {", "    pub fn process(&mut self,",
        "                   dt: f64) {}"]
for nome, linhas, cor, tag in (("codigo_cpp", CPP, AZUL, "node.cpp"), ("codigo_rust", RUST, LAR, "node.rs")):
    im = card(1100, 640, borda=cor)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((4, 4, 1095, 70), 28, fill=GRAF2 + (255,))
    for k, c in enumerate((cor, CINZA, CINZA)):
        d.ellipse((30 + k * 34, 27, 50 + k * 34, 47), fill=c + (255,))
    d.text((150, 22), tag, font=F(MONO, 30), fill=CINZA + (255,))
    for k, l in enumerate(linhas):
        d.text((50, 110 + k * 80), l, font=F(MONOB, 44), fill=(cor if k in (0, 3) else OSSO) + (255,))
    salvar(com_brilho(im, cor, 30, 0.6), nome)

# módulos (apagado e aceso)
for rot in ["RENDER", "FÍSICA", "ÁUDIO", "INTERFACES", "MOTORES", "SCRIPTS", "ESTRUTURA", "LINGUAGEM", "LÓGICAS",
            "NÚCLEO"]:
    for estado, cor in (("off", AZUL), ("on", LAR)):
        im = card(820, 520, borda=cor if estado == "on" else None)
        d = ImageDraw.Draw(im)
        d.text((410, 220), rot, font=F(MONOB, 70), fill=OSSO + (255,), anchor="mm")
        d.rounded_rectangle((90, 400, 730, 430), 12, fill=cor + ((255,) if estado == "on" else (110,)))
        if estado == "on":
            im = com_brilho(im, cor, 26, 0.8)
        salvar(im, f"mod_{rot}_{estado}")

# engrenagens
for estado in ("off", "on"):
    S = 900
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c, r, dentes = S / 2, 330, 14
    pts = []
    for k in range(dentes * 4):
        a = 2 * math.pi * k / (dentes * 4)
        rr = r * (1.14 if k % 4 in (1, 2) else 0.97)
        pts.append((c + rr * math.cos(a), c + rr * math.sin(a)))
    d.polygon(pts, fill=GRAF + (255,), outline=(60, 58, 70, 255))
    d.ellipse((c - 70, c - 70, c + 70, c + 70), fill=(8, 8, 10, 255))
    d.ellipse((c - 205, c - 205, c + 205, c + 205), outline=LAR + ((255,) if estado == "on" else (70,)), width=22)
    if estado == "on":
        im = com_brilho(im, LAR, 22, 1.0)
    salvar(im, f"engrenagem_{estado}")

# personagem em card
p = Image.open(os.path.join(ASSETS, "narrador_a.png")).convert("RGBA").resize((900, 900))
im = card(980, 1080, borda=LAR)
im.alpha_composite(p, (40, 40))
ImageDraw.Draw(im).text((490, 1010), "@jonaltos", font=F(MONOB, 48), fill=(201, 163, 230, 255), anchor="mm")
salvar(com_brilho(im, LAR, 24, 0.7), "card_narrador")

# ícones com brilho de borda
for arq, cor, nome in (("godot_azul.png", AZUL, "icone_godot"), ("rusdot.png", LAR, "icone_rusdot")):
    ic = Image.open(os.path.join(ASSETS, arq)).convert("RGBA")
    ic = ic.resize((900, int(900 * ic.height / ic.width)))
    pad = Image.new("RGBA", (ic.width + 160, ic.height + 160), (0, 0, 0, 0))
    pad.alpha_composite(ic, (80, 80))
    salvar(com_brilho(pad, cor, 30, 0.9), nome)

# fundos (brilho difuso) e poeira
for nome, cor in (("fundo_laranja", LAR), ("fundo_azul", AZUL)):
    W, H = 2400, 1350
    im = Image.new("RGBA", (W, H), (5, 5, 8, 255))
    g = Image.new("L", (W, H), 0)
    ImageDraw.Draw(g).ellipse((W * .25, H * .2, W * .75, H * .85), fill=150)
    cam = Image.new("RGBA", (W, H), cor + (0,))
    cam.putalpha(g.filter(ImageFilter.GaussianBlur(260)))
    salvar(Image.alpha_composite(im, cam), nome)
rnd = random.Random(5)
for k in range(3):
    im = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for _ in range(70):
        x, y, r = rnd.uniform(0, 1920), rnd.uniform(0, 1080), rnd.uniform(1.5, 4.5)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 190, 150, rnd.randint(60, 160)))
    salvar(im.filter(ImageFilter.GaussianBlur(1.2)), f"poeira_{k}")
# OC do jonato (emoções, PNG com transparência) com brilho de contorno suave
BRANDING = r"C:\Users\jhonata\Desktop\jonato branding"
for arq, nome in (("Normal.png", "oc_normal"), ("Aceno.png", "oc_aceno"), ("Empolgado.png", "oc_empolgado"),
                  ("Irritado.png", "oc_irritado"), ("Triste .png", "oc_triste")):
    oc = Image.open(os.path.join(BRANDING, arq)).convert("RGBA").resize((1400, 1400), Image.LANCZOS)
    salvar(com_brilho(oc, (201, 163, 230), 20, 0.5), nome)

# logo da Godot nova (icon_color_outline) com brilho azul
ic = Image.open(os.path.join(BRANDING, "icon_color_outline.png")).convert("RGBA").resize((1000, 1000), Image.LANCZOS)
pad = Image.new("RGBA", (1160, 1160), (0, 0, 0, 0))
pad.alpha_composite(ic, (80, 80))
salvar(com_brilho(pad, AZUL, 30, 0.9), "icone_godot_v2")

# light leak para as transições (luz entrando pela direita, núcleo quase branco)
W, H = 1920, 1080
g = Image.new("L", (W, H), 0)
ImageDraw.Draw(g).ellipse((W * 0.45, -H * 0.3, W * 1.35, H * 1.1), fill=255)
g = g.filter(ImageFilter.GaussianBlur(220))
for nome, cor in (("leak_laranja", (255, 120, 50)), ("leak_azul", (120, 190, 255))):
    im = Image.new("RGBA", (W, H), cor + (0,))
    im.putalpha(g)
    nucleo = Image.new("RGBA", (W, H), (255, 240, 225, 0))
    nucleo.putalpha(g.point(lambda v: max(0, v - 150) * 2))
    salvar(Image.alpha_composite(im, nucleo), nome)
print("ok:", len(os.listdir(OUT)), "imagens em", OUT)
