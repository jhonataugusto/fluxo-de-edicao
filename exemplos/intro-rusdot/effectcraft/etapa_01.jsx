// Etapa 1 — gancho: S1 macro em contra-plongée na Godot (0–1,5 s) e S2 plongée com "RUST" chegando (1,5–3,0 s).
#include "C:/Users/jhonata/Documents/videos/eu_recriei_a_godot_em_rust/_CLAUDE/effectcraft/lib.jsx"
var c = comp();
c.motionBlur = true;
limpar(c, 0, 3.0);

// S1 + S2: mesmo palco
ambiente(c, "azul", 0, 3.0);
var g = camada(c, "icone_godot_v2", 0, 3.0, P(0, 0, 0), 80);
chaves(tr(g, "Y Rotation"), [[0, -18], [3.0, 8]], "suave");
camera(c, "cam S1 macro", 0, 1.5, 85,
    [[0, P(380, 640, -4600), P(40, 10, 0), 5], [1.5, P(330, 580, -4050), P(40, 20, 0), 7]], 120, "lin");

// S2: "RUST" vem do fundo e assenta na palavra (2,19 s)
var r = camada(c, "txt_rust", 1.5, 3.0, P(0, -900, 4000), 85);
chaves(tr(r, "Position"), [[1.79, P(0, -900, 4000)], [2.19, P(0, -600, -150)]], "chega");
opacidade(r, [[1.79, 0], [1.9, 100]]);
camera(c, "cam S2 plongee", 1.5, 3.0, 35,
    [[1.5, P(0, -1700, -2000), P(0, -150, 0), 0], [3.0, P(160, -1950, -2350), P(0, -180, 0), -2]], 30, "suave");
writeLn("etapa 1 ok: " + c.numLayers + " camadas");
