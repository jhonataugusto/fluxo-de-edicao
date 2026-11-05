# Cenas da intro de teste "eu recriei a godot em rust" — perfil jonato ("dossiê animado").
# Uso: blender -b -P cenas.py -- <cena> <pasta_saida>
# Cada cena vira PNGs RGBA (fundo transparente) e um digitacao_<cena>.json para o som de digitação.
import bpy, sys, os, math, json, random

CENA, SAIDA = sys.argv[sys.argv.index("--") + 1:][:2]
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # _CLAUDE
ASSETS = os.path.join(BASE, "assets")
FONTES = r"C:\Users\jhonata\Documents\fluxo-video\perfis\jonato\fontes"
FPS = 30

# Paleta deste vídeo (perfil: fundo escuro, 1 acento por tela, texto claro)
COR = {"osso": "#EDE6DA", "laranja": "#DB310B", "azul": "#478CBF", "painel": "#17161F",
       "painel2": "#1F1D29", "escuro": "#0F0E14", "lilas": "#C9A3E6", "cinza": "#8A8597"}

# Cena: (quadro global de início, duração em quadros)
CENAS = {"c1": (0, 72), "c2": (72, 87), "c3": (159, 183), "c4": (342, 267),
         "c5": (609, 228), "c6": (865, 113), "c7": (978, 122)}
G0, N = CENAS[CENA]
DIGITACAO = []


def lin(hexcor):
    c = [int(hexcor[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return [((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c] + [1]


# Curvas (t de 0 a 1)
EASE = {"lin": lambda t: t,
        "out2": lambda t: 1 - (1 - t) ** 2,
        "out3": lambda t: 1 - (1 - t) ** 3,
        "expo": lambda t: 1 if t >= 1 else 1 - 2 ** (-10 * t),
        "in2": lambda t: t * t,
        "inout3": lambda t: 4 * t ** 3 if t < .5 else 1 - (-2 * t + 2) ** 3 / 2}


def anim(alvo, caminho, idx, f0, f1, v0, v1, curva="out3"):
    """Keyframe em todo quadro com a curva escolhida (independe da interpolação do Blender)."""
    for f in range(f0, f1 + 1):
        t = 0 if f1 == f0 else (f - f0) / (f1 - f0)
        v = v0 + (v1 - v0) * EASE[curva](min(max(t, 0), 1))
        if idx is None:
            setattr(alvo, caminho, v)
            alvo.keyframe_insert(caminho, frame=f)
        else:
            getattr(alvo, caminho)[idx] = v
            alvo.keyframe_insert(caminho, index=idx, frame=f)


# ---------- cena base ----------
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.preferences.edit.keyframe_new_interpolation_type = "LINEAR"
scn = bpy.context.scene
scn.render.resolution_x, scn.render.resolution_y, scn.render.fps = 1920, 1080, FPS
scn.frame_start, scn.frame_end = 0, N - 1
scn.render.film_transparent = True
scn.render.image_settings.file_format, scn.render.image_settings.color_mode = "PNG", "RGBA"
scn.render.filepath = os.path.join(SAIDA, "f_")
motores = [i.identifier for i in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]
scn.render.engine = next(e for e in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE") if e in motores)
try:
    scn.eevee.taa_render_samples = 16
except AttributeError:
    pass
scn.view_settings.view_transform = "Standard"

FONT = {"titulo": bpy.data.fonts.load(os.path.join(FONTES, "BigShouldersDisplay-Black.ttf")),
        "mono": bpy.data.fonts.load(os.path.join(FONTES, "IBMPlexMono-Regular.ttf")),
        "monob": bpy.data.fonts.load(os.path.join(FONTES, "IBMPlexMono-Bold.ttf")),
        "legenda": bpy.data.fonts.load(os.path.join(FONTES, "Montserrat-ExtraBold.ttf"))}

bpy.ops.object.camera_add(location=(0, -10, 0), rotation=(math.radians(90), 0, 0))
CAM = bpy.context.object
scn.camera = CAM


def material(nome, cor="#FFFFFF", alpha=1.0, forca=1.0, img=None, poca=False):
    """Emissão + transparência. Nó Value 'ALPHA' controla a opacidade (animável)."""
    m = bpy.data.materials.new(nome)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    val = nt.nodes.new("ShaderNodeValue")
    val.name = "ALPHA"
    val.outputs[0].default_value = alpha
    em.inputs["Strength"].default_value = forca
    em.inputs["Color"].default_value = lin(cor)
    fac = val.outputs[0]
    if img:
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.name = "IMG"
        tex.image = bpy.data.images.load(img, check_existing=True)
        tex.extension = "CLIP"
        if cor == "#FFFFFF":
            nt.links.new(tex.outputs["Color"], em.inputs["Color"])
        mul = nt.nodes.new("ShaderNodeMath")
        mul.operation = "MULTIPLY"
        nt.links.new(tex.outputs["Alpha"], mul.inputs[0])
        nt.links.new(val.outputs[0], mul.inputs[1])
        fac = mul.outputs[0]
    if poca:  # mancha de luz radial (palco)
        co = nt.nodes.new("ShaderNodeTexCoord")
        gr = nt.nodes.new("ShaderNodeTexGradient")
        gr.gradient_type = "SPHERICAL"
        vm = nt.nodes.new("ShaderNodeVectorMath")
        vm.operation = "SCALE"
        vm.inputs["Scale"].default_value = 2.0
        nt.links.new(co.outputs["Object"], vm.inputs[0])
        nt.links.new(vm.outputs["Vector"], gr.inputs["Vector"])
        mul = nt.nodes.new("ShaderNodeMath")
        mul.operation = "MULTIPLY"
        nt.links.new(gr.outputs["Fac"], mul.inputs[0])
        nt.links.new(val.outputs[0], mul.inputs[1])
        fac = mul.outputs[0]
    nt.links.new(fac, mix.inputs[0])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs[0])
    if hasattr(m, "surface_render_method"):
        m.surface_render_method = "BLENDED"
    else:
        m.blend_method = "BLEND"
    return m


def alfa_val(m):
    return m.node_tree.nodes["ALPHA"].outputs[0]


def alfa(m, f0, f1, v0, v1, curva="out2"):
    anim(alfa_val(m), "default_value", None, f0, f1, v0, v1, curva)


def vazio(loc=(0, 0, 0), pai=None):
    o = bpy.data.objects.new("grupo", None)
    scn.collection.objects.link(o)
    o.parent = pai
    o.location = loc
    return o


def plano(w, h, loc, cor="#FFFFFF", alpha=1.0, img=None, pai=None, poca=False, forca=1.0):
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0), rotation=(math.radians(90), 0, 0))
    o = bpy.context.object
    o.scale = (w, h, 1)
    o.data.materials.append(material("m", cor, alpha, forca, img, poca))
    o.parent = pai
    o.location = loc
    return o


def plano_img(arquivo, altura, loc, pai=None, alpha=1.0):
    caminho = os.path.join(ASSETS, arquivo)
    im = bpy.data.images.load(caminho, check_existing=True)
    w, h = im.size
    return plano(altura * w / h, altura, loc, img=caminho, pai=pai, alpha=alpha)


def texto(corpo, fonte, tam, cor, loc, pai=None, alinh="CENTER", alpha=1.0, forca=1.0):
    bpy.ops.object.text_add(location=(0, 0, 0), rotation=(math.radians(90), 0, 0))
    o = bpy.context.object
    o.data.body = corpo
    o.data.font = FONT[fonte]
    o.data.size = tam
    o.data.align_x, o.data.align_y = alinh, "CENTER"
    o.data.materials.append(material("t", cor, alpha, forca))
    o.parent = pai
    o.location = loc
    return o


def copia(obj, mat, loc=None, escala=1.0):
    c = obj.copy()
    scn.collection.objects.link(c)
    c.material_slots[0].link = "OBJECT"
    c.material_slots[0].material = mat
    c.scale = [s * escala for s in obj.scale]
    if loc is not None:
        c.location = loc
    return c


def brilho(obj, cor, n=4, passo=0.035, a0=0.22):
    """Glow barato: cópias atrás, maiores e transparentes (mesmos dados, material próprio)."""
    img = obj.material_slots[0].material.node_tree.nodes.get("IMG")
    caminho = img.image.filepath if img else None
    return [copia(obj, material("g", cor, a0 / k, 2.0, img=caminho),
                  (obj.location[0], obj.location[1] + 0.004 * k, obj.location[2]), 1 + passo * k)
            for k in range(1, n + 1)]


def espessura(obj, cor, n=6, prof=0.012):
    """Volume falso: pilha de cópias escuras atrás do plano (dá 3D quando o objeto gira)."""
    img = obj.material_slots[0].material.node_tree.nodes.get("IMG")
    caminho = img.image.filepath if img else None
    return [copia(obj, material("e", cor, 1.0, 1.0, img=caminho),
                  (obj.location[0], obj.location[1] + prof * k, obj.location[2])) for k in range(1, n + 1)]


def card(w, h, loc, pai=None, cor="painel", borda=0.03):
    g = vazio(loc, pai)
    plano(w + borda * 2, h + borda * 2, (0, 0.006, 0), COR["osso"], 0.85, pai=g)
    plano(w, h, (0, 0, 0), COR[cor], pai=g)
    return g


# ---------- texto vivo (atualizado a cada quadro) ----------
TYPE, SCRAMBLE = [], []


def digitar(obj, final, f0, cps=16, cursor=True):
    obj.data.body = ""
    TYPE.append((obj.data, final, f0, cps, cursor))
    DIGITACAO.append({"t": round((G0 + f0) / FPS, 3), "chars": len(final.replace(" ", "")), "cps": cps})


def embaralhar(obj, final, f0, f1):
    obj.data.body = ""
    SCRAMBLE.append((obj.data, final, f0, f1))


SIMB = "ABCDEFGHJKLMNPQRSTUVWXYZ0123456789#%&@$"


def atualizar(cena_, *_):
    f = cena_.frame_current
    for d, final, f0, cps, cursor in TYPE:
        n = 0 if f < f0 else int((f - f0) * cps / FPS) + 1
        s = final[:n]
        if cursor and f >= f0 and (n < len(final) or (f // 8) % 2 == 0):
            s += "_"
        d.body = s
    for d, final, f0, f1 in SCRAMBLE:
        if f < f0:
            d.body = ""
            continue
        rnd = random.Random(f)
        travadas = int(len(final) * min(1, (f - f0) / max(1, f1 - f0)))
        d.body = "".join(c if (i < travadas or c == " ") else rnd.choice(SIMB) for i, c in enumerate(final))


bpy.app.handlers.frame_change_pre.append(atualizar)


def camera(f0, f1, d0, d1, curva="lin", x0=0, x1=0, z0=0, z1=0, rz0=0, rz1=0):
    anim(CAM, "location", 1, f0, f1, -d0, -d1, curva)
    if x0 != x1:
        anim(CAM, "location", 0, f0, f1, x0, x1, curva)
    if z0 != z1:
        anim(CAM, "location", 2, f0, f1, z0, z1, curva)
    if rz0 != rz1:
        anim(CAM, "rotation_euler", 2, f0, f1, math.radians(rz0), math.radians(rz1), curva)


def mats(raiz):
    """Materiais de um grupo (para fade)."""
    out = []
    for o in [raiz] + list(raiz.children_recursive):
        for s in getattr(o, "material_slots", []):
            if s.material and s.material not in out:
                out.append(s.material)
    return out


def esconde_ate(raiz, f):
    """Invisível até o quadro f; aparece em 4 quadros."""
    for m in mats(raiz):
        v = alfa_val(m)
        alvo = v.default_value
        anim(v, "default_value", None, 0, f, 0, 0)
        anim(v, "default_value", None, f, f + 4, 0, alvo, "out2")


def entra(obj, f0, dur, de=(0, 0, 0), escala0=None, curva="expo"):
    fim = tuple(obj.location)
    for i in range(3):
        if de[i]:
            anim(obj, "location", i, 0, f0, fim[i] + de[i], fim[i] + de[i])
            anim(obj, "location", i, f0, f0 + dur, fim[i] + de[i], fim[i], curva)
    if escala0 is not None:
        s1 = tuple(obj.scale)
        for i in range(3):
            anim(obj, "scale", i, f0, f0 + dur, s1[i] * escala0, s1[i], curva)


# ---------- cenas ----------
def c1():
    # "Eu recriei a Godot inteira" — palco escuro azulado, cabeça Godot 3D, câmera afastando rápido
    plano(7, 3.2, (0, 0.6, -1.0), COR["azul"], 0.35, poca=True)
    g = vazio((0, 0, -0.35))
    ic = plano_img("godot_azul.png", 1.4, (0, 0, 0), pai=g)
    for c in espessura(ic, "#1C3550"):
        c.parent = g
    anim(g, "rotation_euler", 2, 0, N - 1, math.radians(-14), math.radians(10), "out2")
    t1 = texto("", "titulo", 0.62, COR["osso"], (-0.45, 0, 0.92))
    digitar(t1, "EU RECRIEI A", 12, cps=20, cursor=False)
    t2 = texto("GODOT", "titulo", 0.62, COR["azul"], (1.55, 0, 0.92))
    esconde_ate(t2, 43)
    entra(t2, 43, 8, escala0=1.25, curva="out3")
    camera(0, N - 1, 6.4, 9.0, "out2", rz0=-3, rz1=0)


def c2():
    # "em Rust, em apenas uma semana" — RUST em neon com reflexo, "EM 1 SEMANA" embaralhando
    plano(8, 3.0, (0, 0.6, -1.1), COR["laranja"], 0.28, poca=True)
    texto("EM", "titulo", 0.45, COR["osso"], (0, 0, 1.25))
    r = texto("RUST", "titulo", 1.9, COR["laranja"], (0, 0, 0.15), forca=1.6)
    gl = brilho(r, COR["laranja"], n=5)
    ref = copia(r, material("ref", COR["laranja"], 0.09), (0, 0, -1.65))
    ref.scale = (1, -1, 1)
    for o in [r, ref] + gl:
        v = alfa_val(o.material_slots[0].material)
        a = v.default_value
        anim(v, "default_value", None, 0, 11, 0, 0)
        anim(v, "default_value", None, 11, 15, 0, a, "out2")
        s0 = tuple(o.scale)
        for i in range(3):
            anim(o, "scale", i, 11, 21, s0[i] * 0.6, s0[i], "expo")
    sem = texto("", "monob", 0.34, COR["osso"], (0, 0, -1.05))
    embaralhar(sem, "EM 1 SEMANA", 31, 61)
    camera(0, N - 1, 7.0, 9.5, "lin")


def c3():
    # "Pra quem não sabe, a Godot é uma engine… escrita em C++" — narrador + cards empilhando, deriva lenta
    nar = card(1.7, 2.05, (-2.25, 0.4, -0.05))
    plano_img("narrador_a.png", 1.6, (0, -0.01, 0.15), pai=nar)
    texto("@jonaltos", "mono", 0.13, COR["lilas"], (0, -0.01, -0.85), pai=nar)
    nar.rotation_euler[2] = math.radians(14)
    esconde_ate(nar, 11)
    entra(nar, 11, 14, de=(-3, 0, 0))
    rot = texto("", "mono", 0.14, COR["cinza"], (0.0, 0, 1.45), alinh="LEFT")
    digitar(rot, "REGISTRO 01 // GODOT ENGINE", 54, cps=22)
    # editor (mockup próprio, nada copiado da Godot além do ícone recolorido)
    ed = card(4.0, 2.3, (0.85, 0, -0.1))
    ed.scale = (0.9, 0.9, 0.9)
    ed.rotation_euler[2] = math.radians(-10)
    plano(4.0, 0.18, (0, -0.005, 1.06), COR["painel2"], pai=ed)
    texto("Godot Engine — projeto.tscn", "mono", 0.09, COR["osso"], (-1.85, -0.01, 1.06), pai=ed, alinh="LEFT")
    plano(0.85, 2.0, (-1.52, -0.005, -0.1), COR["painel2"], pai=ed)
    for k, nome in enumerate(["Node2D", "  Sprite2D", "  Camera2D", "  Player", "    Collision"]):
        texto(nome, "mono", 0.085, COR["osso"], (-1.88, -0.01, 0.75 - k * 0.17), pai=ed, alinh="LEFT", alpha=0.8)
    plano(2.3, 2.0, (0.1, -0.005, -0.1), "#101018", pai=ed)
    for k in range(-5, 6):
        plano(0.006, 2.0, (0.1 + k * 0.2, -0.008, -0.1), COR["azul"], 0.2, pai=ed)
    for k in range(-4, 5):
        plano(2.3, 0.006, (0.1, -0.008, -0.1 + k * 0.22), COR["azul"], 0.2, pai=ed)
    plano_img("godot_azul.png", 0.55, (0.1, -0.012, -0.1), pai=ed)
    plano(0.75, 2.0, (1.6, -0.005, -0.1), COR["painel2"], pai=ed)
    for k, nome in enumerate(["Inspector", "position", "rotation", "scale", "visible"]):
        texto(nome, "mono", 0.08, COR["osso"], (1.27, -0.01, 0.75 - k * 0.17), pai=ed, alinh="LEFT", alpha=0.7)
    esconde_ate(ed, 89)
    entra(ed, 89, 16, de=(4, 0, 0))
    for m in mats(nar):  # o narrador recua quando o editor chega
        v = alfa_val(m)
        anim(v, "default_value", None, 93, 105, v.default_value, v.default_value * 0.35, "out2")
    # código C++
    cod = card(2.9, 1.45, (1.25, -0.6, -0.6))
    cod.rotation_euler[2] = math.radians(-6)
    linhas = ['#include "core/object.h"', "", "class Node : public Object {", "    GDCLASS(Node, Object);",
              "public:", "    void _process(double delta);", "};"]
    for k, l in enumerate(linhas):
        texto(l, "mono", 0.1, COR["azul"] if k == 2 else COR["osso"], (-1.3, -0.01, 0.5 - k * 0.15), pai=cod,
              alinh="LEFT")
    texto("C++", "titulo", 0.5, COR["azul"], (1.15, -0.01, 0.48), pai=cod)
    esconde_ate(cod, 161)
    entra(cod, 161, 14, de=(0, 0, -2.5))
    camera(0, N - 1, 9.9, 9.3, "lin", x0=-0.05, x1=0.15, rz0=-1.5, rz1=1.0)


def c4():
    # "troquei toda a estrutura… importei pra Rust" — documento em máquina de escrever, voo para o RUST
    rnd = random.Random(3)
    for k in range(9):  # camada cifrada
        s = " ".join("".join(rnd.choice("0123456789abcdef") for _ in range(4)) for _ in range(14))
        o = texto(s, "mono", 0.12, COR["laranja"], (0, 0.8, 2.0 - k * 0.5), alpha=0.07)
        anim(o, "location", 2, 0, N - 1, o.location[2], o.location[2] + 0.6, "lin")
    doc = card(4.8, 3.0, (0, 0, 0), cor="escuro")
    cab = texto("", "monob", 0.17, COR["osso"], (-2.2, -0.01, 1.2), pai=doc, alinh="LEFT")
    digitar(cab, "PROCESSO: GODOT  ->  RUST", 10, cps=18)
    plano(4.4, 0.006, (0, -0.01, 0.95), COR["cinza"], 0.6, pai=doc)
    for k, (s, f) in enumerate([("[x] estrutura", 113), ("[x] linguagem", 176), ("[x] lógicas", 205)]):
        t = texto("", "mono", 0.2, COR["osso"], (-2.0, -0.01, 0.55 - k * 0.42), pai=doc, alinh="LEFT")
        digitar(t, s, f, cps=20)
        x = texto("OK", "monob", 0.2, COR["laranja"], (1.9, -0.01, 0.55 - k * 0.42), pai=doc)
        esconde_ate(x, f + 10)
    imp = texto("", "mono", 0.2, COR["osso"], (-2.0, -0.01, -0.85), pai=doc, alinh="LEFT")
    digitar(imp, "> importado para", 225, cps=26, cursor=False)
    r = texto("RUST", "titulo", 0.5, COR["laranja"], (0.75, -0.012, -0.85), pai=doc, forca=1.5)
    for o in [r] + brilho(r, COR["laranja"], n=3):
        o.parent = doc
        esconde_ate(o, 238)
    camera(0, 236, 8.6, 7.4, "lin", x0=-0.1, x1=0.15, rz0=1.2, rz1=-0.8)
    camera(236, N - 1, 7.4, 1.2, "in2", x0=0.15, x1=0.95, z0=0, z1=-0.85, rz0=-0.8, rz1=-4)


def c5():
    # "tudo tá rodando em Rust… interfaces… motores" — terminal com cargo run
    plano(8, 3.0, (0, 0.8, -1.4), COR["laranja"], 0.18, poca=True)
    term = card(4.9, 2.75, (0, 0, 0), cor="escuro")
    term.rotation_euler[2] = math.radians(8)
    plano(4.9, 0.2, (0, -0.005, 1.27), COR["painel2"], pai=term)
    for k, c in enumerate((COR["laranja"], COR["cinza"], COR["cinza"])):
        plano(0.07, 0.07, (-2.3 + k * 0.13, -0.01, 1.27), c, pai=term)
    texto("rusdot — cargo run", "mono", 0.09, COR["cinza"], (0, -0.01, 1.27), pai=term)
    x0, z0, dz = -2.25, 0.95, 0.27
    cmd = texto("", "mono", 0.15, COR["osso"], (x0, -0.01, z0), pai=term, alinh="LEFT")
    digitar(cmd, "$ cargo run --release", 10, cps=22)
    log = [("   Compiling rusdot_core v0.1.0", 22, "cinza"), ("   Compiling rusdot_render v0.1.0", 25, "cinza"),
           ("   Compiling rusdot_physics v0.1.0", 28, "cinza"), ("    Finished release em 41.2s", 40, "osso"),
           ("     interfaces", 89, "osso"), ("     motores", 160, "osso")]
    for k, (s, f, c) in enumerate(log):
        z = z0 - (k + 1) * dz
        t = texto(s, "mono", 0.15, COR[c], (x0, -0.01, z), pai=term, alinh="LEFT")
        esconde_ate(t, f)
        if f >= 89:
            ok = texto("[ok]", "monob", 0.15, COR["laranja"], (x0, -0.012, z), pai=term, alinh="LEFT")
            esconde_ate(ok, f)
    fim = texto("", "monob", 0.17, COR["osso"], (x0, -0.01, z0 - 7 * dz), pai=term, alinh="LEFT")
    digitar(fim, "> tudo rodando em RUST", 188, cps=24)
    camera(0, N - 1, 7.6, 9.2, "lin", x0=0.2, x1=-0.15, rz0=-1, rz1=1.5)


def c6():
    # Revelação: Godot azul -> Rusdot laranja (ganha as garras), "RUSDOT" em máquina de escrever
    pa = plano(6, 2.6, (0, 0.6, -1.35), COR["azul"], 0.3, poca=True)
    pl = plano(7, 3.0, (0, 0.6, -1.35), COR["laranja"], 0.35, poca=True)
    gz = vazio((0, 0, 0.55))
    az = plano_img("godot_azul.png", 1.55, (0, 0, 0), pai=gz)
    for c in espessura(az, "#1C3550"):
        c.parent = gz
    gr = vazio((0, 0, 0.42))
    rd = plano_img("rusdot.png", 2.0, (0, 0, 0), pai=gr)
    for c in espessura(rd, "#4A1205") + brilho(rd, COR["laranja"], n=4, passo=0.03, a0=0.18):
        c.parent = gr
    # azul: aparece e some no "mostrar" (q24); laranja entra com escala
    for m in mats(gz) + [pa.material_slots[0].material]:
        v = alfa_val(m)
        a = v.default_value
        anim(v, "default_value", None, 0, 10, 0, a, "out2")
        anim(v, "default_value", None, 23, 26, a, 0, "out2")
    anim(gz, "rotation_euler", 2, 0, 24, math.radians(-8), 0, "out2")
    for m in mats(gr) + [pl.material_slots[0].material]:
        v = alfa_val(m)
        a = v.default_value
        anim(v, "default_value", None, 0, 24, 0, 0)
        anim(v, "default_value", None, 24, 27, 0, a, "out2")
    for i in range(3):
        anim(gr, "scale", i, 24, 38, 0.82, 1.0, "expo")
    anim(gr, "rotation_euler", 2, 24, N - 1, math.radians(6), math.radians(-4), "out2")
    nome = texto("", "titulo", 0.75, COR["osso"], (0, 0, -0.98))
    digitar(nome, "RUSDOT", 44, cps=7, cursor=False)
    sub = texto("", "mono", 0.14, COR["cinza"], (0, 0, -1.4))
    digitar(sub, "GAME ENGINE // escrita em Rust", 94, cps=26)
    camera(0, N - 1, 9.8, 8.6, "lin")


def c7():
    # "então vem comigo que eu vou te mostrar tudo" — narrador ao lado da logo, câmera afastando
    plano(8, 3.0, (0.9, 0.6, -1.3), COR["laranja"], 0.3, poca=True)
    gr = vazio((1.15, 0, 0.3))
    rd = plano_img("rusdot.png", 2.0, (0, 0, 0), pai=gr)
    for c in espessura(rd, "#4A1205") + brilho(rd, COR["laranja"], n=3, passo=0.03, a0=0.16):
        c.parent = gr
    anim(gr, "rotation_euler", 2, 0, N - 1, math.radians(-4), math.radians(-12), "lin")
    nar = card(1.6, 1.95, (-1.75, 0.2, 0.1))
    plano_img("narrador_b.png", 1.5, (0, -0.01, 0.15), pai=nar)
    texto("@jonaltos", "mono", 0.12, COR["lilas"], (0, -0.01, -0.8), pai=nar)
    nar.rotation_euler[2] = math.radians(12)
    esconde_ate(nar, 12)
    entra(nar, 12, 14, de=(-3, 0, 0))
    vem = texto("", "titulo", 0.55, COR["osso"], (1.15, 0, -1.2))
    digitar(vem, "VEM COMIGO", 34, cps=14, cursor=False)
    camera(0, N - 1, 7.9, 9.4, "lin")
    # saída: tudo some nos últimos 10 quadros
    vistos = set()
    for o in list(scn.objects):
        for s in getattr(o, "material_slots", []):
            if s.material and s.material.name not in vistos:
                vistos.add(s.material.name)
                v = alfa_val(s.material)
                a = v.default_value
                fc = None
                v.keyframe_insert("default_value", frame=N - 11)
                v.default_value = 0
                v.keyframe_insert("default_value", frame=N - 1)
                v.default_value = a


globals()[CENA]()
os.makedirs(SAIDA, exist_ok=True)
json.dump(DIGITACAO, open(os.path.join(SAIDA, f"digitacao_{CENA}.json"), "w"))
TESTE = sys.argv[sys.argv.index("--") + 1:][2:]  # quadros avulsos para conferir (ex.: 10 40 70)
if TESTE:
    for f in map(int, TESTE):
        scn.frame_set(f)
        scn.render.filepath = os.path.join(SAIDA, f"teste_{CENA}_{f:04d}.png")
        bpy.ops.render.render(write_still=True)
else:
    bpy.ops.render.render(animation=True)
