// Etapa 5 — REV Godot vira Rusdot no "mostrar" (25,8–29,5 s) e FIN personagem chega, câmera heroica (29,5–32,3 s).
#include "C:/Users/jhonata/Documents/videos/eu_recriei_a_godot_em_rust/_CLAUDE/effectcraft/lib.jsx"
var c = comp();
limpar(c, 25.8, 32.3);
var M = 26.5; // "mostrar"

ambiente(c, "laranja", 25.8, 32.3);
var g = camada(c, "icone_godot_v2", 25.8, 26.8, P(0, -60, 0), 72);
opacidade(g, [[25.8, 40], [26.1, 100]]);
escala(g, [[M - 0.07, 90], [M + 0.2, 0]], "sai");
chaves(tr(g, "Z Rotation"), [[25.8, 0], [M + 0.2, 35]], "sai");

var r = camada(c, "icone_rusdot", M, 32.3, P(0, -80, 0), 0);
escala(r, [[M, 0], [M + 0.47, 85]], "chega");
chaves(tr(r, "Y Rotation"), [[M, -40], [32.3, 6]], "chega");

var clarao = solido(c, [1, 0.85, 0.75], "clarão", M - 0.05, M + 0.35);
opacidade(clarao, [[M - 0.05, 0], [M, 85], [M + 0.35, 0]], "lin");

var letras = ["R", "U", "S", "D", "O", "T"];
for (var k = 0; k < 6; k++) {
    var t = 27.0 + k * 0.13, fim = P(-470 + k * 188, 330, 0);
    var L = camada(c, "rd_" + letras[k], 25.8, 32.3, P(-470 + k * 188, 580, 0), 70);
    chaves(tr(L, "Position"), [[t, P(-470 + k * 188, 580, 0)], [t + 0.33, fim]], "chega");
    opacidade(L, [[t, 0], [t + 0.15, 100]]);
}
opacidade(camada(c, "txt_sub", 25.8, 32.3, P(0, 450, 0), 150), [[28.0, 0], [28.4, 100]]);
camera(c, "cam REV", 25.8, 29.5, 50,
    [[25.8, P(0, 80, -3400), P(0, 120, 0), 0], [29.5, P(0, 60, -2800), P(0, 120, 0), 0]], 30, "lin");

// FIN: card do personagem chega da esquerda; contra-plongée heroica afastando
var card = camada(c, "oc_aceno", 29.5, 32.3, P(-3600, 40, -150), 62, [0, 18, 0]);
chaves(tr(card, "Position"), [[29.86, P(-3600, 40, -150)], [30.4, P(-1050, 40, -150)]], "chega");
camera(c, "cam FIN heroica", 29.5, 32.3, 35,
    [[29.5, P(-300, 520, -2500), P(-320, 200, 0), -3], [32.3, P(-340, 600, -3300), P(-340, 200, 0), 0]], 35, "suave");
// fim: segura no Rusdot + OC acenando (sem apagar para preto)
writeLn("etapa 5 ok: " + c.numLayers + " camadas");
