// Biblioteca de montagem da intro 3D (imagens 2D em espaço 3D + câmera cinematográfica) no EffectCraft.
// Incluída por cada etapa_NN.jsx. Unidades em pixels; P(x, y, z) é relativo ao centro do quadro (y para baixo).
var ASSETS = "C:/Users/jhonata/Documents/videos/eu_recriei_a_godot_em_rust/_CLAUDE/assets2d/";
var NOME_COMP = "Intro 3D v01";

function comp() {
    for (var i = 1; i <= app.project.numItems; i++) {
        var it = app.project.item(i);
        if (it instanceof CompItem && it.name == NOME_COMP) return it;
    }
    var c = app.project.items.addComp(NOME_COMP, 1920, 1080, 1, 32.3, 30);
    c.bgColor = [0.02, 0.02, 0.03];
    return c;
}

function foot(nome) {
    for (var i = 1; i <= app.project.numItems; i++) {
        if (app.project.item(i).name == nome + ".png") return app.project.item(i);
    }
    return app.project.importFile(new ImportOptions(new File(ASSETS + nome + ".png")));
}

function P(x, y, z) { return [960 + x, 540 + y, z]; }

function tr(L, nome) { return L.property("Transform").property(nome); }

// Camada 3D a partir de uma imagem, viva só entre t0 e t1.
function camada(c, nome, t0, t1, pos, escala, rot) {
    var L = c.layers.add(foot(nome));
    L.threeDLayer = true;
    L.motionBlur = true;
    L.inPoint = t0;
    L.outPoint = t1;
    tr(L, "Position").setValue(pos);
    var s = escala || 100;
    tr(L, "Scale").setValue([s, s, s]);
    if (rot) {
        if (rot[0]) tr(L, "X Rotation").setValue(rot[0]);
        if (rot[1]) tr(L, "Y Rotation").setValue(rot[1]);
        if (rot[2]) tr(L, "Z Rotation").setValue(rot[2]);
    }
    L.name = nome + " @" + t0;
    return L;
}

// Sólido 2D (preto, clarão) por cima de tudo.
function solido(c, cor, nome, t0, t1) {
    var L = c.layers.addSolid(cor, nome, 1920, 1080, 1);
    L.inPoint = t0;
    L.outPoint = t1;
    return L;
}

// Keyframes [[t, valor], ...] com curva: "suave" (ease in/out), "chega" (rápido e assenta), "sai" (lento e acelera), "lin".
function chaves(prop, lista, curva) {
    for (var i = 0; i < lista.length; i++) prop.setValueAtTime(lista[i][0], lista[i][1]);
    if (!curva || curva == "lin") return;
    var dims = (prop.name == "Scale") ? 3 : 1;
    for (var k = 1; k <= prop.numKeys; k++) {
        var entra = 70, sai = 70;
        if (curva == "chega") { sai = (k == 1) ? 8 : 70; entra = 92; }
        if (curva == "sai") { sai = 92; entra = (k == prop.numKeys) ? 8 : 70; }
        var a = [], b = [];
        for (var d = 0; d < dims; d++) { a.push(new KeyframeEase(0, entra)); b.push(new KeyframeEase(0, sai)); }
        try { prop.setTemporalEaseAtKey(k, a, b); } catch (e2) {}
    }
}

function opacidade(L, lista, curva) { chaves(tr(L, "Opacity"), lista, curva || "suave"); }

function escala(L, lista, curva) {
    var l2 = [];
    for (var i = 0; i < lista.length; i++) l2.push([lista[i][0], [lista[i][1], lista[i][1], lista[i][1]]]);
    chaves(tr(L, "Scale"), l2, curva || "chega");
}

// Câmera de um plano: caminho [[t, posição, alvo, rolagem], ...], lente em mm, abertura (desfoque) em px.
function camera(c, nome, t0, t1, mm, caminho, abertura, curva) {
    var cam = c.layers.addCamera(nome, [960, 540]);
    cam.inPoint = t0;
    cam.outPoint = t1;
    var op = cam.property("Camera Options");
    op.property("Zoom").setValue(1920 * mm / 36);
    op.property("Depth of Field").setValue(1);
    op.property("Aperture").setValue(abertura || 40);
    var pos = [], alvo = [], rolar = [], foco = [];
    for (var i = 0; i < caminho.length; i++) {
        var k = caminho[i], dx = k[2][0] - k[1][0], dy = k[2][1] - k[1][1], dz = k[2][2] - k[1][2];
        pos.push([k[0], k[1]]);
        alvo.push([k[0], k[2]]);
        rolar.push([k[0], k[3] || 0]);
        foco.push([k[0], Math.sqrt(dx * dx + dy * dy + dz * dz)]);
    }
    chaves(tr(cam, "Position"), pos, curva || "suave");
    chaves(tr(cam, "Point of Interest"), alvo, curva || "suave");
    chaves(tr(cam, "Z Rotation"), rolar, curva || "suave");
    chaves(op.property("Focus Distance"), foco, curva || "suave");
    return cam;
}

// Fundo e ar do plano, vivos entre t0 e t1.
// O fundo é uma camada 2D no fim da pilha: preenche o quadro para qualquer lado que a câmera olhe (nunca preto).
// A poeira é 3D, em várias profundidades: ganha paralaxe com a câmera. Sutil: ar com partículas, não céu estrelado.
function ambiente(c, cor, t0, t1) {
    var bg = c.layers.add(foot("fundo_" + cor));
    bg.inPoint = t0;
    bg.outPoint = t1;
    tr(bg, "Scale").setValue([82, 82]);
    bg.name = "fundo 2D " + cor + " @" + t0;
    bg.moveToEnd();
    var prof = [[-300, 0, -900, 160, 26], [400, 100, 300, 220, 22], [-500, -150, 1500, 300, 18],
                [300, 200, 2800, 420, 14], [0, -200, 4200, 560, 10]];
    for (var i = 0; i < prof.length; i++) {
        var p = prof[i];
        var d = camada(c, "poeira_" + (i % 3), t0, t1, P(p[0], p[1], p[2]), p[3]);
        opacidade(d, [[t0, p[4]]], "lin");
        chaves(tr(d, "Position"), [[t0, P(p[0], p[1], p[2])], [t1, P(p[0] + 60, p[1] - 140, p[2])]], "lin");
    }
}

// Partículas (brasas/faíscas) com CC Particle World numa camada 2D por cima, entre t0 e t1.
function particulas(c, t0, t1, cor, nome) {
    var s = c.layers.addSolid([0, 0, 0], nome || "GLOBAL particulas", 1920, 1080, 1);
    s.inPoint = t0;
    s.outPoint = t1;
    var e = s.property("Effects").addProperty("CC Particle World");
    function setar(caminho, v) {
        var p = e;
        for (var i = 0; i < caminho.length; i++) p = p.property(caminho[i]);
        p.setValue(v);
    }
    setar(["Birth Rate"], 1.6);
    setar(["Longevity (sec)"], 3.2);
    setar(["Producer", "Position Y"], 0.35);
    setar(["Producer", "Radius X"], 1.4);
    setar(["Producer", "Radius Y"], 0.25);
    setar(["Producer", "Radius Z"], 1.0);
    setar(["Physics", "Animation"], 1);
    setar(["Physics", "Velocity"], 0.22);
    setar(["Physics", "Gravity"], -0.06);
    setar(["Physics", "Resistance"], 1.5);
    setar(["Physics", "Extra"], 0.6);
    setar(["Particle", "Particle Type"], 2);
    setar(["Particle", "Birth Size"], 0.035);
    setar(["Particle", "Death Size"], 0.008);
    setar(["Particle", "Size Variation"], 70);
    setar(["Particle", "Max Opacity"], 70);
    setar(["Particle", "Birth Color"], cor == "azul" ? [0.55, 0.8, 1, 1] : [1, 0.62, 0.3, 1]);
    setar(["Particle", "Death Color"], cor == "azul" ? [0.2, 0.45, 0.8, 1] : [0.9, 0.22, 0.05, 1]);
    setar(["Particle", "Transfer Mode"], 2);
    return s;
}

// Light leak na troca de plano em t: entra rápido, sai devagar, em modo de luz (somar).
// _v3 = brilho gaussiano sem platô nem borda (alfa vai a 0 suave nas bordas); escala 130 % de folga para o deslize.
function leak(c, t, cor) {
    var L = c.layers.add(foot("leak_" + cor + "_v3"));
    L.inPoint = t - 0.12;
    L.outPoint = t + 0.3;
    L.name = "GLOBAL leak " + t;
    tr(L, "Scale").setValue([130, 130]);
    try { L.blendingMode = BlendingMode.ADD; } catch (e) {}
    opacidade(L, [[t - 0.12, 0], [t, 85], [t + 0.3, 0]], "suave");
    chaves(tr(L, "Position"), [[t - 0.12, [1160, 540]], [t + 0.3, [820, 540]]], "lin");
    return L;
}

// Remove as camadas que começam no intervalo [t0, t1) — para refazer uma etapa sem duplicar.
// Camadas "GLOBAL ..." (partículas e leaks) ficam: só a etapa global mexe nelas.
function limpar(c, t0, t1) {
    for (var i = c.numLayers; i >= 1; i--) {
        var L = c.layer(i);
        if (L.name.indexOf("GLOBAL") == 0) continue;
        if (L.inPoint >= t0 - 0.001 && L.inPoint < t1 - 0.001) L.remove();
    }
}

function limpar_global(c) {
    for (var i = c.numLayers; i >= 1; i--) if (c.layer(i).name.indexOf("GLOBAL") == 0) c.layer(i).remove();
}
