# Intro 3D "eu recriei a godot em rust" — espaço 3D abstrato, câmera cinematográfica, gancho rápido + respiro.
# Uso: blender -b -P cenas3d.py -- <pasta_saida> [quadros de teste...]
# Áudio de referência: audio/voz_cortada_v02.wav com 1,0 s de pausa inserida em 24,79 s (antes da revelação).
import bpy, sys, os, math, json
from mathutils import Vector, Quaternion

ARGS = sys.argv[sys.argv.index("--") + 1:]
SAIDA, TESTE = ARGS[0], [int(f) for f in ARGS[1:]]
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # _CLAUDE
ASSETS = os.path.join(BASE, "assets")
FONTES = r"C:\Users\jhonata\Documents\fluxo-video\perfis\jonato\fontes"
FPS, TOTAL = 30, 969


def q(s):  # segundos -> quadro
    return round(s * FPS)


# Planos: (nome, início s, fim s)
PLANOS = [("S1", 0.0, 1.5), ("S2", 1.5, 3.0), ("S3", 3.0, 4.5), ("S4", 4.5, 6.0), ("S5", 6.0, 9.0), ("S6", 9.0, 10.4),
          ("R1", 10.4, 13.9), ("R2", 13.9, 17.9), ("R3", 17.9, 21.9), ("R4", 21.9, 24.8), ("P", 24.8, 25.8),
          ("REV", 25.8, 29.5), ("FIN", 29.5, 32.3)]
COR = {"laranja": "#E8441C", "rust": "#DB310B", "azul": "#478CBF", "osso": "#EDE6DA", "grafite": "#18181D",
       "claro": "#CFC9BE", "escuro": "#050506", "frio": "#C9D6FF", "fundo": "#050508"}


def lin(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return [((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c] + [1]


EASE = {"lin": lambda t: t, "out2": lambda t: 1 - (1 - t) ** 2, "out3": lambda t: 1 - (1 - t) ** 3,
        "expo": lambda t: 1 if t >= 1 else 1 - 2 ** (-10 * t), "in2": lambda t: t * t,
        "inout2": lambda t: 2 * t * t if t < .5 else 1 - (-2 * t + 2) ** 2 / 2,
        "inout3": lambda t: 4 * t ** 3 if t < .5 else 1 - (-2 * t + 2) ** 3 / 2}


def anim(alvo, caminho, idx, f0, f1, v0, v1, curva="out3"):
    """Chave em todo quadro com a curva escolhida."""
    for f in range(f0, f1 + 1):
        t = 0 if f1 == f0 else (f - f0) / (f1 - f0)
        v = v0 + (v1 - v0) * EASE[curva](min(max(t, 0), 1))
        if idx is None:
            setattr(alvo, caminho, v)
            alvo.keyframe_insert(caminho, frame=f)
        else:
            getattr(alvo, caminho)[idx] = v
            alvo.keyframe_insert(caminho, index=idx, frame=f)


def anim_vec(obj, caminho, f0, f1, v0, v1, curva="out3"):
    for i in range(3):
        if v0[i] != v1[i] or f0 == 0:
            anim(obj, caminho, i, f0, f1, v0[i], v1[i], curva)


# ---------- cena ----------
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.preferences.edit.keyframe_new_interpolation_type = "LINEAR"
scn = bpy.context.scene
scn.render.resolution_x, scn.render.resolution_y, scn.render.fps = 1920, 1080, FPS
scn.frame_start, scn.frame_end = 0, TOTAL - 1
scn.render.engine = "BLENDER_EEVEE"
ee = scn.eevee
for prop, val in (("use_raytracing", True), ("taa_render_samples", 24), ("use_shadows", True),
                  ("volumetric_tile_size", "8"), ("use_volumetric_shadows", True)):
    try:
        setattr(ee, prop, val)
    except (AttributeError, TypeError):
        pass
scn.render.use_motion_blur = True
scn.render.motion_blur_shutter = 0.5
vts = [i.identifier for i in scn.view_settings.bl_rna.properties["view_transform"].enum_items]
scn.view_settings.view_transform = "AgX" if "AgX" in vts else "Standard"
try:
    looks = [i.identifier for i in scn.view_settings.bl_rna.properties["look"].enum_items]
    alvo_look = next((l for l in looks if "Medium High Contrast" in l), None)
    if alvo_look:
        scn.view_settings.look = alvo_look
except Exception:
    pass
scn.render.image_settings.file_format, scn.render.image_settings.color_mode = "PNG", "RGB"
scn.render.filepath = os.path.join(SAIDA, "f_")

# Mundo: escuro, com neblina leve (profundidade sem "espaço sideral")
mundo = bpy.data.worlds.new("mundo")
scn.world = mundo
mundo.use_nodes = True
nt = mundo.node_tree
bg = next(n for n in nt.nodes if n.type == "BACKGROUND")
bg.inputs["Color"].default_value = lin(COR["fundo"])
bg.inputs["Strength"].default_value = 1.0
vol = nt.nodes.new("ShaderNodeVolumePrincipled")
vol.inputs["Density"].default_value = 0.0045
vol.inputs["Anisotropy"].default_value = 0.35
nt.links.new(vol.outputs[0], next(n for n in nt.nodes if n.type == "OUTPUT_WORLD").inputs["Volume"])

FONT = {"titulo": bpy.data.fonts.load(os.path.join(FONTES, "BigShouldersDisplay-Black.ttf")),
        "mono": bpy.data.fonts.load(os.path.join(FONTES, "IBMPlexMono-Bold.ttf"))}


# ---------- materiais ----------
def mat_pbr(nome, cor, rough=0.35, metal=0.0, coat=0.3):
    m = bpy.data.materials.new(nome)
    m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = lin(cor)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    for nome_in in ("Coat Weight", "Clearcoat"):
        if nome_in in p.inputs:
            p.inputs[nome_in].default_value = coat
            break
    return m


def mat_luz(nome, cor, forca=6.0):
    m = bpy.data.materials.new(nome)
    m.use_nodes = True
    nt_ = m.node_tree
    nt_.nodes.clear()
    em = nt_.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = lin(cor)
    em.inputs["Strength"].default_value = forca
    nt_.links.new(em.outputs[0], nt_.nodes.new("ShaderNodeOutputMaterial").inputs[0])
    return m


def forca_luz(m):
    return next(n for n in m.node_tree.nodes if n.type == "EMISSION").inputs["Strength"]


def mat_img(nome, arquivo, forca=1.0):
    m = bpy.data.materials.new(nome)
    m.use_nodes = True
    nt_ = m.node_tree
    nt_.nodes.clear()
    tex = nt_.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(os.path.join(ASSETS, arquivo), check_existing=True)
    em = nt_.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = forca
    nt_.links.new(tex.outputs["Color"], em.inputs["Color"])
    nt_.links.new(em.outputs[0], nt_.nodes.new("ShaderNodeOutputMaterial").inputs[0])
    return m


M = {"grafite": mat_pbr("grafite", COR["grafite"], 0.32, 0.0, 0.4), "claro": mat_pbr("claro", COR["claro"], 0.45),
     "escuro": mat_pbr("escuro", COR["escuro"], 0.22), "osso": mat_pbr("osso", COR["osso"], 0.4)}


# ---------- construtores ----------
def vazio(loc=(0, 0, 0), pai=None, nome="grupo"):
    o = bpy.data.objects.new(nome, None)
    scn.collection.objects.link(o)
    o.parent = pai
    o.location = loc
    return o


def curva_obj(nome, polys, prof, bevel, mat, fill=True, z=0.0):
    cu = bpy.data.curves.new(nome, "CURVE")
    cu.dimensions = "2D" if fill else "3D"
    if fill:
        cu.fill_mode = "BOTH"
    cu.extrude = prof if fill else 0
    cu.bevel_depth = bevel
    cu.bevel_resolution = 3
    for p in polys:
        sp = cu.splines.new("POLY")
        sp.points.add(len(p) - 1)
        for i, (x, y) in enumerate(p):
            sp.points[i].co = (x, y, z, 1)
        sp.use_cyclic_u = True
    o = bpy.data.objects.new(nome, cu)
    scn.collection.objects.link(o)
    o.data.materials.append(mat)
    return o


def icone(nome, altura, loc, pai=None, borda="laranja", prof=0.09):
    """Ícone 3D a partir dos contornos: corpo grafite, detalhes claros/escuros, aresta frontal emissiva."""
    dados = json.load(open(os.path.join(ASSETS, f"icone_{nome}.json")))
    g = vazio(loc, pai, nome)
    g.rotation_euler[0] = math.radians(90)  # plano XY -> de frente para -Y
    g.scale = (altura,) * 3
    pz = {"corpo": 0.0, "claro": 0.012, "escuro": 0.02}
    mats = {"corpo": M["grafite"], "claro": M["claro"], "escuro": M["escuro"]}
    for c in dados["camadas"]:
        if not c["polys"]:
            continue
        o = curva_obj(f"{nome}_{c['papel']}", c["polys"], prof * (1 if c["papel"] == "corpo" else 0.35), 0.006,
                      mats[c["papel"]])
        o.parent = g
        o.location = (0, 0, pz[c["papel"]] + (0 if c["papel"] == "corpo" else prof * 0.75))
    corpo = next(c for c in dados["camadas"] if c["papel"] == "corpo")
    luz = mat_luz(f"{nome}_aresta", COR[borda], 3.5)
    ar = curva_obj(f"{nome}_aresta", corpo["polys"], 0, 0.006, luz, fill=False, z=prof + 0.004)
    ar.parent = g
    g["aresta"] = luz.name
    return g


def texto3d(corpo, fonte, tam, mat, loc, pai=None, extr=0.05, alinh="CENTER", rot_x=90):
    cu = bpy.data.curves.new("txt", "FONT")
    cu.body = corpo
    cu.font = FONT[fonte]
    cu.size = tam
    cu.extrude = extr
    cu.bevel_depth = 0.006
    cu.bevel_resolution = 2
    cu.align_x, cu.align_y = alinh, "CENTER"
    o = bpy.data.objects.new("txt", cu)
    scn.collection.objects.link(o)
    o.data.materials.append(mat)
    o.parent = pai
    o.location = loc
    o.rotation_euler[0] = math.radians(rot_x)
    return o


def caixa(dim, loc, mat, pai=None, bevel=0.03):
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.object
    o.scale = dim
    o.data.materials.append(mat)
    if bevel:
        md = o.modifiers.new("bevel", "BEVEL")
        md.width = bevel
        md.segments = 3
        md.affect = "EDGES"
        md.limit_method = "NONE"
    o.parent = pai
    o.location = loc
    return o


CPP = ["class Node : public Object {", "  GDCLASS(Node, Object);", "public:", "  void _process(double dt);",
       "  Vector2 position;", "};"]
RUST = ["pub struct Node {", "    pub position: Vec2,", "}", "impl Node {", "  pub fn process(&mut self,", "    dt: f64) {}"]


def lamina(loc, rot_z, pai, linhas_a=CPP, linhas_b=RUST, cor_a="azul", cor_b="laranja"):
    """Lâmina de código: frente C++ (azul), verso Rust (laranja). Girar 180° em Z troca o lado."""
    g = vazio(loc, pai, "lamina")
    g.rotation_euler[2] = math.radians(rot_z)
    caixa((1.7, 0.04, 1.05), (0, 0, 0), M["grafite"], g, bevel=0.015)
    ma, mb = mat_luz("la", COR[cor_a], 2.2), mat_luz("lb", COR[cor_b], 2.6)
    for k, l in enumerate(linhas_a):
        texto3d(l, "mono", 0.085, ma, (-0.75, -0.022, 0.38 - k * 0.15), g, extr=0.0, alinh="LEFT")
    for k, l in enumerate(linhas_b):
        t = texto3d(l, "mono", 0.085, mb, (0.75, 0.022, 0.38 - k * 0.15), g, extr=0.0, alinh="LEFT")
        t.rotation_euler[2] = math.radians(180)
    caixa((1.7, 0.046, 0.012), (0, 0, -0.52), mat_luz("fio", COR[cor_a], 5), g, bevel=0)
    return g


def modulo(loc, dim, rotulo, pai, cor="laranja", ligado=0.0):
    g = vazio(loc, pai, "modulo")
    caixa(dim, (0, 0, 0), M["grafite"], g, bevel=0.06)
    faixa = mat_luz("faixa", COR[cor], ligado)
    caixa((dim[0] * 0.8, 0.01, 0.05), (0, -dim[1] / 2 - 0.006, -dim[2] * 0.3), faixa, g, bevel=0)
    texto3d(rotulo, "mono", 0.16, M["claro"], (0, -dim[1] / 2 - 0.004, dim[2] * 0.12), g, extr=0.0)
    g["faixa"] = faixa.name
    return g


def engrenagem(loc, raio, dentes, pai, cor="laranja", esp=0.25):
    g = vazio(loc, pai, "engrenagem")
    g.rotation_euler[0] = math.radians(90)
    bpy.ops.mesh.primitive_cylinder_add(vertices=64, radius=raio, depth=esp)
    cil = bpy.context.object
    cil.data.materials.append(M["grafite"])
    cil.parent = g
    for k in range(dentes):
        a = 2 * math.pi * k / dentes
        d = caixa((raio * 0.28, raio * 0.22, esp * 0.96), (math.cos(a) * raio * 1.05, math.sin(a) * raio * 1.05, 0),
                  M["grafite"], g, bevel=0.01)
        d.rotation_euler[2] = a
    bpy.ops.mesh.primitive_torus_add(major_radius=raio * 0.62, minor_radius=0.025)
    anel = bpy.context.object
    m = mat_luz("anel", COR[cor], 1.0)
    anel.data.materials.append(m)
    anel.parent = g
    anel.location = (0, 0, esp / 2 + 0.01)
    g["anel"] = m.name
    return g


def placa_personagem(loc, pai, altura=1.6):
    g = vazio(loc, pai, "placa")
    caixa((altura * 1.06, 0.05, altura * 1.06), (0, 0.03, 0), M["grafite"], g, bevel=0.02)
    bpy.ops.mesh.primitive_plane_add(size=altura, rotation=(math.radians(90), 0, 0))
    p = bpy.context.object
    p.data.materials.append(mat_img("narrador", "narrador_a.png", 1.1))
    p.parent = g
    p.location = (0, 0, 0)
    contorno = [[[-altura * .53, -altura * .53], [altura * .53, -altura * .53], [altura * .53, altura * .53],
                 [-altura * .53, altura * .53]]]
    ar = curva_obj("placa_aresta", contorno, 0, 0.008, mat_luz("pa", COR["laranja"], 3), fill=False)
    ar.parent = g
    ar.rotation_euler[0] = math.radians(90)
    ar.location = (0, -0.006, 0)
    texto3d("@jonaltos", "mono", 0.11, mat_luz("arroba", "#C9A3E6", 3), (0, -0.01, -altura * 0.62), g, extr=0)
    return g


def luzes(centro, rim=650, chave=350, cor_rim="laranja"):
    cx, cy, cz = centro
    for loc, energia, cor, tam in (((cx + 2.5, cy + 3.5, cz + 2.5), rim, COR[cor_rim], 3),
                                   ((cx - 3.5, cy - 3.0, cz + 2.0), chave, COR["frio"], 4),
                                   ((cx, cy, cz + 5), chave * 0.4, COR["frio"], 6)):
        dados = bpy.data.lights.new("luz", "AREA")
        dados.energy, dados.size = energia, tam
        dados.color = lin(cor)[:3]
        o = bpy.data.objects.new("luz", dados)
        scn.collection.objects.link(o)
        o.location = loc
        c = o.constraints.new("TRACK_TO")
        c.target = vazio(centro, nome="alvo_luz")
        c.track_axis, c.up_axis = "TRACK_NEGATIVE_Z", "UP_Y"
        yield o


# ---------- câmeras ----------
def olhar(de, para, rolar=0.0):
    d = Vector(para) - Vector(de)
    qt = d.to_track_quat("-Z", "Y")
    return (qt @ Quaternion((0, 0, 1), math.radians(rolar))).to_euler()


def camera(nome, plano, lente, fstop, caminho, curva="inout2"):
    """caminho: lista de (s, posição, alvo, rolar). A câmera vale do início ao fim do plano (marcador)."""
    dados = bpy.data.cameras.new(nome)
    dados.lens = lente
    dados.clip_start, dados.clip_end = 0.05, 300
    dados.dof.use_dof = True
    dados.dof.aperture_fstop = fstop
    cam = bpy.data.objects.new(nome, dados)
    scn.collection.objects.link(cam)
    foco = vazio(caminho[0][2], nome=f"foco_{nome}")
    dados.dof.focus_object = foco
    for (s0, p0, a0, r0), (s1, p1, a1, r1) in zip(caminho, caminho[1:]):
        f0, f1 = q(s0), q(s1)
        for f in range(f0, f1 + 1):
            t = EASE[curva](0 if f1 == f0 else (f - f0) / (f1 - f0))
            p = Vector(p0).lerp(Vector(p1), t)
            a = Vector(a0).lerp(Vector(a1), t)
            cam.location = p
            cam.rotation_euler = olhar(p, a, r0 + (r1 - r0) * t)
            cam.keyframe_insert("location", frame=f)
            cam.keyframe_insert("rotation_euler", frame=f)
            foco.location = a
            foco.keyframe_insert("location", frame=f)
    ini = next(p for p in PLANOS if p[0] == plano)
    m = scn.timeline_markers.new(plano, frame=q(ini[1]))
    m.camera = cam
    if q(ini[1]) == 0:
        scn.camera = cam
    return cam


def deriva(c, a):  # soma vetores
    return tuple(x + y for x, y in zip(c, a))


# ---------- conjuntos (cada plano tem o seu canto do espaço) ----------
X = {k: i * 60.0 for i, k in enumerate(["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"])}

# A — S1/S2: engrenagem Godot 3D, "RUST" chegando
A = (X["A"], 0, 0)
gd = icone("godot", 2.0, A, borda="azul")
anim(gd, "rotation_euler", 2, 0, q(3.0), math.radians(-18), math.radians(8), "out2")
list(luzes(A))
rust = texto3d("RUST", "titulo", 1.1, mat_luz("rust", COR["laranja"], 3.2), deriva(A, (0, -0.4, 2.05)), extr=0.12,
               rot_x=55)
anim_vec(rust, "location", 0, q(2.19) - 12, deriva(A, (0, 14, 3.5)), deriva(A, (0, 14, 3.5)), "lin")
anim_vec(rust, "location", q(2.19) - 12, q(2.19), deriva(A, (0, 14, 3.5)), deriva(A, (0, -0.4, 2.05)), "expo")
camera("cS1", "S1", 85, 2.0, [(0.0, deriva(A, (0.9, -4.2, -1.1)), deriva(A, (0.25, 0, 0.05)), 5),
                              (1.5, deriva(A, (0.7, -3.5, -0.95)), deriva(A, (0.25, 0, 0.08)), 7)], "lin")
camera("cS2", "S2", 35, 4.0, [(1.5, deriva(A, (0, -5.6, 5.0)), deriva(A, (0, 0, 0.9)), 0),
                              (3.0, deriva(A, (0.6, -6.6, 5.6)), deriva(A, (0, 0, 1.0)), -2)], "out2")

# B — S3: "7 DIAS" em blocos que viram, dutch angle baixo, órbita rápida
B = (X["B"], 0, 0)
list(luzes(B, rim=1100))
for k, ch in enumerate("7 DIAS"):
    if ch == " ":
        continue
    t = texto3d(ch, "mono", 0.9, M["osso"] if ch != "7" else mat_luz("sete", COR["laranja"], 3.0),
                deriva(B, (-1.6 + k * 0.62, 0, 0)), extr=0.18)
    f0 = q(3.0) + 3 + k * 3
    anim(t, "rotation_euler", 0, 0, f0, math.radians(-90), math.radians(-90), "lin")
    anim(t, "rotation_euler", 0, f0, f0 + 10, math.radians(-90), math.radians(90), "expo")
for k in range(14):  # poeira de blocos para profundidade
    import random
    r = random.Random(k)
    cb = caixa((0.12, 0.12, 0.12), deriva(B, (r.uniform(-4, 4), r.uniform(-3, 6), r.uniform(-1.5, 2))), M["grafite"])
    anim(cb, "rotation_euler", 2, q(3.0), q(4.5), 0, r.uniform(-2, 2), "lin")
camera("cS3", "S3", 28, 2.8, [(3.0, deriva(B, (-3.2, -3.0, -0.7)), deriva(B, (0, 0, 0.1)), 14),
                              (4.5, deriva(B, (1.8, -3.9, -0.5)), deriva(B, (0.2, 0, 0.1)), 9)], "out3")

# C — S4: personagem deitado no espaço; câmera de cima inclina e ele levanta
C = (X["C"], 0, 0)
list(luzes(C, rim=700))
pl = placa_personagem(C, None)
anim(pl, "rotation_euler", 0, q(4.5), q(6.0), math.radians(-90), math.radians(-25), "out3")
camera("cS4", "S4", 35, 2.2, [(4.5, deriva(C, (0, -0.4, 5.2)), deriva(C, (0, 0, 0)), 0),
                              (6.0, deriva(C, (0.4, -4.4, 1.6)), deriva(C, (0, 0, 0.2)), 0)], "inout3")

# D — S5: travelling lateral pelos módulos da engine (azul = Godot), colunas desfocadas na frente
D = (X["D"], 0, 0)
list(luzes(D, rim=600, cor_rim="azul"))
for k, nome in enumerate(["RENDER", "FÍSICA", "ÁUDIO", "INTERFACES", "MOTORES", "SCRIPTS"]):
    modulo(deriva(D, (-5 + k * 2.0, 0, 0)), (1.6, 1.2, 1.0), nome, None, cor="azul", ligado=2.5)
for k in range(5):
    caixa((0.18, 0.18, 4), deriva(D, (-4 + k * 2.3, -2.4, 0)), M["grafite"], bevel=0.02)
eng = texto3d("ENGINE DE JOGOS", "titulo", 0.5, M["osso"], deriva(D, (0, 1.6, 1.05)), extr=0.06)
camera("cS5", "S5", 50, 2.0, [(6.0, deriva(D, (-4.5, -4.9, 0.9)), deriva(D, (-3.5, 0, 0.45)), 0),
                              (9.0, deriva(D, (3.0, -4.9, 1.0)), deriva(D, (3.5, 0, 0.45)), 0)], "lin")

# E — S6: close nas lâminas C++ (azul), "C++" 3D atrás
E = (X["E"], 0, 0)
list(luzes(E, rim=500, cor_rim="azul"))
for k in range(3):
    lamina(deriva(E, (-0.4 + k * 0.5, k * 1.1, 0.05 * k)), -18 + k * 6, None)
cpp = texto3d("C++", "titulo", 1.3, mat_luz("cpp", COR["azul"], 3.0), deriva(E, (1.2, 4.0, 0.6)), extr=0.15)
anim(cpp, "scale", 0, 0, q(9.6), 0.0, 0.0, "lin")
for i in range(3):
    anim(cpp, "scale", i, q(9.6), q(9.6) + 8, 0.0, 1.0, "expo")
camera("cS6", "S6", 85, 4.0, [(9.0, deriva(E, (-1.3, -2.9, 0.3)), deriva(E, (-0.55, -0.05, 0.25)), -3),
                              (10.4, deriva(E, (-0.8, -2.8, 0.4)), deriva(E, (-0.25, -0.05, 0.25)), -1)], "lin")

# F — R1: corredor de lâminas; viram de C++ para Rust quando a câmera passa
F = (X["F"], 0, 0)
list(luzes(deriva(F, (0, 10, 0)), rim=1400))
for k in range(9):
    for lado in (-1, 1):
        y = k * 2.6
        lm = lamina(deriva(F, (lado * 1.35, y, 0)), 90 * lado, None)
        s_passa = 10.4 + 3.5 * (y + 3) / 24  # instante em que a câmera chega perto
        f0 = q(s_passa) - 4
        anim(lm, "rotation_euler", 2, 0, f0, math.radians(90 * lado), math.radians(90 * lado), "lin")
        anim(lm, "rotation_euler", 2, f0, f0 + 10, math.radians(90 * lado), math.radians(90 * lado + 180), "expo")
camera("cR1", "R1", 24, 3.2, [(10.4, deriva(F, (0, -3, 0.25)), deriva(F, (0, 6, 0.1)), -2),
                              (13.9, deriva(F, (0.15, 19.5, 0.35)), deriva(F, (0, 30, 0.2)), 3)], "inout2")

# G — R2: módulos se encaixando; órbita; "RUST" na palavra
G = (X["G"], 0, 0)
list(luzes(G, rim=1000))
pos_final = [(-0.85, 0, 0.6), (0.85, 0, 0.6), (-0.85, 0, -0.6), (0.85, 0, -0.6)]
pos_ini = [(-3.5, 2, 2.5), (3.8, -1, 2.2), (-3.2, 1, -2.6), (3.6, 2.5, -2.2)]
nomes = ["ESTRUTURA", "LINGUAGEM", "LÓGICAS", "NÚCLEO"]
chega = [13.3, 14.8, 15.76, 16.42]
for pf, pi, nome, s in zip(pos_final, pos_ini, nomes, chega):
    md = modulo(deriva(G, pf), (1.6, 1.2, 1.1), nome, None, ligado=0.0)
    anim_vec(md, "location", 0, q(s) - 10, deriva(G, pi), deriva(G, pi), "lin")
    anim_vec(md, "location", q(s) - 10, q(s) + 6, deriva(G, pi), deriva(G, pf), "expo")
    fx = forca_luz(bpy.data.materials[md["faixa"]])
    anim(fx, "default_value", None, q(s) + 2, q(s) + 10, 0.0, 4.0, "out2")
rg = texto3d("RUST", "titulo", 0.9, mat_luz("rust2", COR["laranja"], 3.2), deriva(G, (0, -0.2, 1.75)), extr=0.12)
for i in range(3):
    anim(rg, "scale", i, 0, q(17.28), 0.0, 0.0, "lin")
    anim(rg, "scale", i, q(17.28), q(17.28) + 8, 0.0, 1.0, "expo")
pts = []
for k in range(5):
    a = math.radians(-60 + 70 * k / 4)
    pts.append((13.9 + 4.0 * k / 4, deriva(G, (math.sin(a) * 6.5, -math.cos(a) * 6.5, 1.6 - 0.3 * k)),
                deriva(G, (0, 0, 0.3)), 0))
camera("cR2", "R2", 40, 3.5, pts, "lin")

# H — R3: grua subindo; "INTERFACES" acende
H = (X["H"], 0, 0)
list(luzes(H, rim=900))
for k, (pf, nome) in enumerate(zip(pos_final, ["INTERFACES", "RENDER", "FÍSICA", "ÁUDIO"])):
    md = modulo(deriva(H, pf), (1.6, 1.2, 1.1), nome, None, ligado=0.3)
    if nome == "INTERFACES":
        anim(forca_luz(bpy.data.materials[md["faixa"]]), "default_value", None, q(20.68) - 2, q(20.68) + 8, 0.3,
             5.0, "expo")
camera("cR3", "R3", 35, 2.8, [(17.9, deriva(H, (-1.5, -4.0, -1.0)), deriva(H, (-0.6, 0, 0.4)), 4),
                              (21.9, deriva(H, (-0.4, -3.6, 3.6)), deriva(H, (-0.4, 0, 0.2)), 0)], "inout3")

# I — R4 + pausa: engrenagens MOTORES girando; tudo acende; depois apaga
I = (X["I"], 0, 0)
luz_i = list(luzes(I, rim=1000))
engs = [engrenagem(deriva(I, (-0.9, 0, 0.3)), 0.9, 16, None), engrenagem(deriva(I, (0.85, 0.05, -0.45)), 0.6, 11, None),
        engrenagem(deriva(I, (1.75, 0.0, 0.75)), 0.45, 9, None)]
for k, (e, vel) in enumerate(zip(engs, (1.0, -1.5, 2.0))):
    anim(e, "rotation_euler", 1, q(21.9), q(25.8), 0, vel * 2.4, "lin")
    anel = forca_luz(bpy.data.materials[e["anel"]])
    anim(anel, "default_value", None, q(22.84) + k * 3, q(22.84) + k * 3 + 8, 0.6, 4.5, "expo")
    anim(anel, "default_value", None, q(24.8), q(25.2), 4.5, 0.03, "out2")
mot = texto3d("MOTORES", "titulo", 0.55, mat_luz("mot", COR["osso"], 3), deriva(I, (0.2, -0.5, -1.45)), extr=0.08)
for o in luz_i:
    anim(o.data, "energy", None, q(24.8), q(25.3), o.data.energy, 0.0, "out2")
camera("cR4", "R4", 50, 2.0, [(21.9, deriva(I, (0.3, -2.6, 0.2)), deriva(I, (0.1, 0, 0.1)), -2),
                              (24.8, deriva(I, (0.2, -6.5, 0.9)), deriva(I, (0.2, 0, 0.0)), 0)], "out3")
camera("cP", "P", 50, 2.0, [(24.8, deriva(I, (0.2, -6.5, 0.9)), deriva(I, (0.2, 0, 0.0)), 0),
                            (25.8, deriva(I, (0.2, -6.9, 0.95)), deriva(I, (0.2, 0, 0.0)), 0)], "lin")

# J — REV + FIN: Godot vira Rusdot no "mostrar"; "RUSDOT" sobe letra a letra; personagem chega
J = (X["J"], 0, 0)
luz_j = list(luzes(J, rim=1300))
for o in luz_j:
    e = o.data.energy
    anim(o.data, "energy", None, q(25.8), q(26.3), 0.0, e * 0.6, "out2")
    anim(o.data, "energy", None, q(26.5), q(26.5) + 6, e * 0.6, e, "out2")
gj = icone("godot", 1.8, deriva(J, (0, 0, 0.35)), borda="azul")
rd = icone("rusdot", 2.0, deriva(J, (0, 0, 0.35)), borda="laranja")
f_m = q(26.5)  # "mostrar"
for i in range(3):
    anim(gj, "scale", i, f_m - 2, f_m + 6, 1.8, 0.0, "in2")
    anim(rd, "scale", i, 0, f_m, 0.0, 0.0, "lin")
    anim(rd, "scale", i, f_m, f_m + 14, 0.0, 2.0, "expo")
anim(gj, "rotation_euler", 2, q(25.8), f_m + 6, 0, math.radians(35), "in2")
anim(rd, "rotation_euler", 2, f_m, q(32.3), math.radians(-40), math.radians(6), "expo")
clarao = bpy.data.lights.new("clarao", "POINT")
clarao.color = lin(COR["laranja"])[:3]
oc = bpy.data.objects.new("clarao", clarao)
scn.collection.objects.link(oc)
oc.location = deriva(J, (0, -1.2, 0.4))
anim(clarao, "energy", None, 0, f_m - 1, 0.0, 0.0, "lin")
anim(clarao, "energy", None, f_m - 1, f_m + 1, 0.0, 15000.0, "lin")
anim(clarao, "energy", None, f_m + 1, f_m + 8, 15000.0, 0.0, "out2")
mat_rusdot = mat_luz("rusdot_txt", COR["osso"], 2.5)
for k, ch in enumerate("RUSDOT"):
    t = texto3d(ch, "titulo", 0.62, mat_rusdot, deriva(J, (-0.9 + k * 0.36, -0.2, -1.3)), extr=0.09)
    f0 = q(27.0) + k * 4
    anim(t, "location", 2, 0, f0, J[2] - 3.0, J[2] - 3.0, "lin")
    anim(t, "location", 2, f0, f0 + 10, J[2] - 3.0, J[2] - 1.3, "expo")
pj = placa_personagem(deriva(J, (-2.6, 0.4, 0.3)), None, altura=1.3)
pj.rotation_euler[2] = math.radians(22)
anim(pj, "location", 0, 0, q(29.86), J[0] - 9, J[0] - 9, "lin")
anim(pj, "location", 0, q(29.86), q(29.86) + 16, J[0] - 9, J[0] - 2.6, "expo")
camera("cREV", "REV", 50, 2.8, [(25.8, deriva(J, (0, -10.0, 0.3)), deriva(J, (0, 0, -0.1)), 0),
                                (29.5, deriva(J, (0, -9.0, 0.15)), deriva(J, (0, 0, -0.2)), 0)], "lin")
camera("cFIN", "FIN", 35, 3.5, [(29.5, deriva(J, (-0.6, -5.0, -1.3)), deriva(J, (-0.6, 0, 0.3)), -3),
                                (32.3, deriva(J, (-0.8, -7.4, -1.5)), deriva(J, (-0.7, 0, 0.3)), 0)], "out2")

# ---------- render ----------
os.makedirs(SAIDA, exist_ok=True)
if TESTE:
    for f in TESTE:
        scn.frame_set(f)
        scn.render.filepath = os.path.join(SAIDA, f"teste3d_{f:04d}.png")
        bpy.ops.render.render(write_still=True)
else:
    bpy.ops.render.render(animation=True)
