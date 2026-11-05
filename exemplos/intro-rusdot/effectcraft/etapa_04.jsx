// Etapa 4 — R2 módulos se encaixando em órbita (13,9–17,9 s), R3 grua com INTERFACES acendendo (17,9–21,9 s),
// R4 engrenagens MOTORES e pausa no escuro (21,9–25,8 s).
#include "C:/Users/jhonata/Documents/videos/eu_recriei_a_godot_em_rust/_CLAUDE/effectcraft/lib.jsx"
var c = comp();
limpar(c, 13.9, 25.8);

var grade = [[-430, -280], [430, -280], [-430, 280], [430, 280]];

// R2: chegam explodidos e encaixam nas palavras; acendem ao encaixar; "RUST" no fim
ambiente(c, "laranja", 13.9, 17.9);
var nomes = ["ESTRUTURA", "LINGUAGEM", "LÓGICAS", "NÚCLEO"], chega = [14.1, 14.8, 15.76, 16.42];
var de = [[-2100, -1300, -1400], [2200, -1100, 1300], [-2000, 1300, 1500], [2100, 1200, -1300]];
for (var k = 0; k < 4; k++) {
    var fim = P(grade[k][0], grade[k][1], 0), ini = P(de[k][0], de[k][1], de[k][2]);
    var off = camada(c, "mod_" + nomes[k] + "_off", 13.9, 17.9, ini, 100);
    var on = camada(c, "mod_" + nomes[k] + "_on", 13.9, 17.9, ini, 100);
    chaves(tr(off, "Position"), [[chega[k] - 0.35, ini], [chega[k] + 0.2, fim]], "chega");
    chaves(tr(on, "Position"), [[chega[k] - 0.35, ini], [chega[k] + 0.2, fim]], "chega");
    opacidade(on, [[chega[k] + 0.1, 0], [chega[k] + 0.35, 100]]);
}
var rust = camada(c, "txt_rust", 13.9, 17.9, P(0, -760, -100), 80);
escala(rust, [[17.28, 0], [17.55, 80]], "chega");
var arco = [];
for (var k = 0; k <= 4; k++) {
    var a = (-55 + 70 * k / 4) * Math.PI / 180;
    arco.push([13.9 + k, P(2900 * Math.sin(a), -380 - 60 * k, -2900 * Math.cos(a)), P(0, -120, 0), 0]);
}
camera(c, "cam R2 orbita", 13.9, 17.9, 40, arco, 35, "lin");

// R3: grade montada; INTERFACES acende na palavra (20,68 s); grua de baixo para cima
ambiente(c, "laranja", 17.9, 21.9);
var nomes3 = ["INTERFACES", "RENDER", "FÍSICA", "ÁUDIO"];
for (var k = 0; k < 4; k++) {
    camada(c, "mod_" + nomes3[k] + "_off", 17.9, 21.9, P(grade[k][0], grade[k][1], 0), 100);
    if (k == 0) opacidade(camada(c, "mod_INTERFACES_on", 17.9, 21.9, P(grade[0][0], grade[0][1], -2), 100),
        [[20.6, 0], [20.9, 100]]);
}
camera(c, "cam R3 grua", 17.9, 21.9, 35,
    [[17.9, P(-650, 800, -2300), P(-430, -150, 0), 4], [21.9, P(-380, -1500, -2000), P(-430, -260, 0), 0]], 40, "suave");

// R4: engrenagens girando; anéis acendem em sequência na palavra (22,84 s); afastamento; pausa: escurece
ambiente(c, "laranja", 21.9, 25.8);
var eng = [[-350, -100, 0, 100, 60], [330, 250, 150, 66, -90], [640, -330, -100, 50, 120]];
for (var k = 0; k < 3; k++) {
    var e = eng[k], pos = P(e[0], e[1], e[2]);
    var g0 = camada(c, "engrenagem_off", 21.9, 25.8, pos, e[3]);
    var g1 = camada(c, "engrenagem_on", 21.9, 25.8, pos, e[3]);
    chaves(tr(g0, "Z Rotation"), [[21.9, 0], [25.8, e[4] * 3.9]], "lin");
    chaves(tr(g1, "Z Rotation"), [[21.9, 0], [25.8, e[4] * 3.9]], "lin");
    opacidade(g1, [[22.84 + k * 0.1, 0], [23.1 + k * 0.1, 100]]);
}
camada(c, "txt_motores", 21.9, 25.8, P(330, 280, -200), 80);
var om = camada(c, "oc_empolgado", 22.6, 25.8, P(-620, 200, -300), 34, [0, 18, 0]);
chaves(tr(om, "Position"), [[22.6, P(-620, 640, -300)], [23.0, P(-620, 200, -300)]], "chega");
camera(c, "cam R4 afasta", 21.9, 25.8, 50,
    [[21.9, P(100, 0, -1200), P(80, 0, 0), -2], [24.8, P(150, -150, -3200), P(120, 0, 0), 0],
     [25.8, P(150, -160, -3350), P(120, 0, 0), 0]], 40, "chega");
// pausa: escurece sem apagar (nunca tela preta)
var sombra = solido(c, [0.02, 0.01, 0.01], "pausa", 24.8, 25.8);
opacidade(sombra, [[24.8, 0], [25.2, 62], [25.8, 62]]);
writeLn("etapa 4 ok: " + c.numLayers + " camadas");
