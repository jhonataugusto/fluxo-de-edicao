// Etapa 6 — global: partículas (CC Particle World) em toda a intro e light leak em cada troca de plano.
// Rodar depois das etapas 1–5. Refaz só as camadas "GLOBAL ...".
#include "C:/Users/jhonata/Documents/videos/eu_recriei_a_godot_em_rust/_CLAUDE/effectcraft/lib.jsx"
var c = comp();
limpar_global(c);

// azul nos trechos da Godot ("antes"), laranja no resto
var trechos = [[0, 3.0, "azul"], [3.0, 6.0, "laranja"], [6.0, 10.4, "azul"], [10.4, 32.3, "laranja"]];
for (var i = 0; i < trechos.length; i++) particulas(c, trechos[i][0], trechos[i][1], trechos[i][2], "GLOBAL particulas " + trechos[i][0]);

var cortes = [[1.5, "azul"], [3.0, "laranja"], [4.5, "laranja"], [6.0, "azul"], [9.0, "azul"], [10.4, "laranja"],
              [13.9, "laranja"], [17.9, "laranja"], [21.9, "laranja"], [25.8, "laranja"], [29.5, "laranja"]];
for (var i = 0; i < cortes.length; i++) leak(c, cortes[i][0], cortes[i][1]);
writeLn("etapa 6 ok: " + c.numLayers + " camadas");
