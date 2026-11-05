// Etapa 3 — S5 travelling pelos módulos (6,0–9,0 s), S6 close no C++ (9,0–10,4 s), R1 corredor C++ -> Rust (10,4–13,9 s).
#include "C:/Users/jhonata/Documents/videos/eu_recriei_a_godot_em_rust/_CLAUDE/effectcraft/lib.jsx"
var c = comp();
limpar(c, 6.0, 13.9);

// S5: módulos apagados (azul = Godot), colunas escuras na frente para paralaxe
ambiente(c, "azul", 6.0, 9.0);
var mods = ["RENDER", "FÍSICA", "ÁUDIO", "INTERFACES", "MOTORES", "SCRIPTS"];
for (var k = 0; k < mods.length; k++) camada(c, "mod_" + mods[k] + "_off", 6.0, 9.0, P(-1750 + k * 700, 60, 0), 80);
camada(c, "txt_engine", 6.0, 9.0, P(0, -330, 350), 90);
camera(c, "cam S5 travelling", 6.0, 9.0, 50,
    [[6.0, P(-1600, -80, -2300), P(-1400, 0, 0), 0], [9.0, P(1300, -120, -2300), P(1500, 0, 0), 0]], 45, "lin");

// S6: painéis C++ ao fundo (contexto, desfocados); foco único no "C++" que surge na palavra (9,6 s);
// OC irritado no terço esquerdo, olhando para o "C++" (reação = plateia). Push-in lento frontal.
ambiente(c, "azul", 9.0, 10.4);
camada(c, "codigo_cpp", 9.0, 10.4, P(-420, 40, 900), 95, [0, -14, 0]);
camada(c, "codigo_cpp", 9.0, 10.4, P(520, -60, 1300), 95, [0, -8, 0]);
var oi = camada(c, "oc_irritado", 9.0, 10.4, P(-470, 110, -250), 24, [0, 15, 0]);
chaves(tr(oi, "Position"), [[9.0, P(-470, 500, -250)], [9.35, P(-470, 110, -250)]], "chega");
var cpp = camada(c, "txt_cpp", 9.0, 10.4, P(260, -170, 0), 100);
escala(cpp, [[9.55, 0], [9.82, 100]], "chega");
camera(c, "cam S6 close", 9.0, 10.4, 50,
    [[9.0, P(-140, 0, -2350), P(-60, -30, 0), -2], [10.4, P(-80, -20, -2050), P(-40, -50, 0), 0]], 45, "suave");

// R1: corredor; cada painel vira de C++ (azul) para Rust (laranja) quando a câmera se aproxima
ambiente(c, "laranja", 10.4, 13.9);
for (var k = 0; k < 9; k++) {
    var z = k * 800;
    var tvira = 10.4 + 3.5 * (z + 1500) / 8000;
    for (var lado = -1; lado <= 1; lado += 2) {
        var base = 90 * lado;
        var a = camada(c, "codigo_cpp", 10.4, 13.9, P(650 * lado, 0, z), 70, [0, base, 0]);
        var b = camada(c, "codigo_rust", 10.4, 13.9, P(650 * lado, 0, z), 70, [0, base, 0]);
        chaves(tr(a, "Y Rotation"), [[tvira - 0.17, base], [tvira, base + 90]], "sai");
        chaves(tr(b, "Y Rotation"), [[tvira, base - 90], [tvira + 0.2, base]], "chega");
        opacidade(a, [[tvira, 100], [tvira + 0.01, 0]], "lin");
        opacidade(b, [[tvira - 0.01, 0], [tvira, 100]], "lin");
    }
}
// ponto focal do corredor: o logo do Rust no fim do túnel (destino), crescendo enquanto a câmera chega
var lr = camada(c, "logo_rust_osso", 10.4, 13.9, P(0, 0, 10200), 200);
opacidade(lr, [[10.4, 35], [12.6, 100]]);
chaves(tr(lr, "Z Rotation"), [[10.4, -40], [13.9, 0]], "suave");
camera(c, "cam R1 corredor", 10.4, 13.9, 24,
    [[10.4, P(0, 0, -1500), P(0, 0, 1500), -2], [13.9, P(0, 30, 6300), P(0, 20, 9300), 3]], 8, "suave");
writeLn("etapa 3 ok: " + c.numLayers + " camadas");
