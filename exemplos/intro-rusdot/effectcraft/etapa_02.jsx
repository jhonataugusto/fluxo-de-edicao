// Etapa 2 — gancho: S3 "7 DIAS" virando com dutch angle (3,0–4,5 s) e S4 personagem visto de cima (4,5–6,0 s).
#include "C:/Users/jhonata/Documents/videos/eu_recriei_a_godot_em_rust/_CLAUDE/effectcraft/lib.jsx"
var c = comp();
limpar(c, 3.0, 6.0);

// S3: letras viram uma a uma (Y 90 -> 0), câmera baixa inclinada e em órbita rápida
ambiente(c, "laranja", 3.0, 4.5);
var letras = ["7", "D", "I", "A", "S"], xs = [-620, -250, -30, 190, 430];
for (var k = 0; k < letras.length; k++) {
    var L = camada(c, "ch_" + letras[k], 3.0, 4.5, P(xs[k], 0, 0), 100);
    var t = 3.08 + k * 0.1;
    chaves(tr(L, "Y Rotation"), [[t, 90], [t + 0.33, 0]], "chega");
}
var oe = camada(c, "oc_empolgado", 3.0, 4.5, P(620, 110, 400), 48, [0, -20, 0]);
chaves(tr(oe, "Position"), [[3.0, P(620, 510, 400)], [3.35, P(620, 110, 400)]], "chega");
camera(c, "cam S3 dutch", 3.0, 4.5, 28,
    [[3.0, P(-950, 280, -1350), P(0, 0, 0), 14], [4.5, P(700, 220, -1550), P(60, 0, 0), 9]], 50, "chega");

// S4: card do personagem deitado; câmera de cima desce para frente enquanto ele levanta
ambiente(c, "laranja", 4.5, 6.0);
var card = camada(c, "oc_normal", 4.5, 6.0, P(0, 0, 0), 62, [-88, 0, 0]);
chaves(tr(card, "X Rotation"), [[4.5, -88], [6.0, -12]], "chega");
camera(c, "cam S4 de cima", 4.5, 6.0, 35,
    [[4.5, P(0, -2600, -80), P(0, 0, 0), 0], [6.0, P(160, -420, -2300), P(0, -40, 0), 0]], 40, "suave");
writeLn("etapa 2 ok: " + c.numLayers + " camadas");
