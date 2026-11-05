// Etapa 7 — efeitos do pack (overlays em vídeo + tremida de câmera nos impactos).
// Rodar depois das etapas 1–6. Refaz só as camadas "PACK ..." e as expressões de tremida.
#include "C:/Users/jhonata/Documents/videos/eu_recriei_a_godot_em_rust/_CLAUDE/effectcraft/lib.jsx"
var OVERLAYS = "C:/Users/jhonata/Documents/videos/eu_recriei_a_godot_em_rust/_CLAUDE/overlays/";
var c = comp();
for (var i = c.numLayers; i >= 1; i--) if (c.layer(i).name.indexOf("PACK") == 0) c.layer(i).remove();

function video(nome) {
    for (var i = 1; i <= app.project.numItems; i++) if (app.project.item(i).name == nome) return app.project.item(i);
    return app.project.importFile(new ImportOptions(new File(OVERLAYS + nome)));
}

// Overlay 2D em Screen (o preto some), começando em t0 a partir do segundo `desde` do clipe.
function overlay(nome, t0, t1, desde, escalaPct) {
    var L = c.layers.add(video(nome));
    L.startTime = t0 - (desde || 0);
    L.inPoint = t0;
    L.outPoint = t1;
    L.name = "PACK " + nome + " @" + t0;
    try { L.blendingMode = BlendingMode.SCREEN; } catch (e) {}
    if (escalaPct) tr(L, "Scale").setValue([escalaPct, escalaPct]);
    L.moveToBeginning();
    return L;
}

// Rajada: entra rápido, segura um pouco, sai devagar.
function rajada(nome, t, dur, pico, desde, escalaPct) {
    var L = overlay(nome, t - 0.08, t + dur, desde, escalaPct);
    opacidade(L, [[t - 0.08, 0], [t, pico], [t + dur * 0.4, pico], [t + dur, 0]], "suave");
    return L;
}

// Brasas reais por cima dos trechos laranja (o clipe tem 10 s: emenda).
var brasas = [[3.0, 6.0], [10.4, 20.4], [20.4, 30.4], [30.4, 32.3]];
for (var i = 0; i < brasas.length; i++) tr(overlay("fire_embers_2.mp4", brasas[i][0], brasas[i][1], 0.3), "Opacity").setValue(45);

// Light leaks em vídeo nas trocas grandes de plano (somam aos leaks PNG da etapa 6).
var leaksVid = [[1.5, "light_leaks_3.mp4", 2.0], [6.0, "light_leaks_3.mp4", 5.0], [10.4, "light_leaks_2.mp4", 1.0],
                [17.9, "light_leaks_2.mp4", 4.0], [25.8, "light_leaks_2.mp4", 7.0]];
for (var i = 0; i < leaksVid.length; i++) rajada(leaksVid[i][1], leaksVid[i][0], 0.9, 80, leaksVid[i][2]);

// Linhas de luz nos movimentos rápidos (chicote).
rajada("random_light_lines.mp4", 9.0, 0.45, 55, 1.0);
rajada("random_light_lines.mp4", 29.86, 0.5, 60, 2.5);

// REV: shockwave vermelho + raios roxos quando a Godot vira Rusdot.
var M = 26.5;
rajada("shockwave.mp4", M, 1.1, 100, 0.0, 140);
rajada("particular_explosion.mp4", M + 0.05, 0.7, 70, 0.0);
rajada("plexus_4.mp4", 27.0, 1.3, 35, 0.5);

// Tremida de câmera nos impactos: senóide que decai, somada ao caminho da câmera (Position e POI juntos).
var impactos = [[2.19, 26], [3.42, 18], [M, 40], [30.4, 24]];
function tremida(cam, lista) {
    var e = "var d=[0,0,0];";
    for (var i = 0; i < lista.length; i++)
        e += "var t=time-" + lista[i][0] + ";if(t>0&&t<0.5){var a=" + lista[i][1] + "*Math.exp(-t*9);d=[Math.sin(t*71)*a,Math.cos(t*53)*a*0.7,0];}";
    e += "value+d;";
    tr(cam, "Position").expression = e;
    tr(cam, "Point of Interest").expression = e;
}
for (var i = 1; i <= c.numLayers; i++) {
    var L = c.layer(i);
    if (!(L instanceof CameraLayer)) continue;
    var meus = [];
    for (var k = 0; k < impactos.length; k++) if (impactos[k][0] >= L.inPoint && impactos[k][0] < L.outPoint) meus.push(impactos[k]);
    if (meus.length) tremida(L, meus);
    else { tr(L, "Position").expression = ""; tr(L, "Point of Interest").expression = ""; }
}
writeLn("etapa 7 ok: " + c.numLayers + " camadas");
