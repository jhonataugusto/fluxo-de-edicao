// Confere se algum overlay 2D em modo de luz (Add/Screen: leaks, flares, partículas em vídeo) deixa a própria borda
// entrar no quadro enquanto está visível. Borda dentro do quadro = linha reta "vazando" no render.
// Uso: effectcraft-cli --bridge 47322 script checar_bordas.jsx   (comp: a ativa, ou a primeira comp do projeto)
// Só lê; não muda nada. Amostra a cada 1/15 s entre a entrada e a saída de cada camada.
(function () {
    var c = app.project.activeItem;
    if (!(c instanceof CompItem)) {
        for (var i = 1; i <= app.project.numItems; i++) if (app.project.item(i) instanceof CompItem) { c = app.project.item(i); break; }
    }
    var problemas = 0, conferidas = 0;
    for (var i = 1; i <= c.numLayers; i++) {
        var L = c.layer(i);
        if (L.threeDLayer || !L.source || !L.source.width) continue;
        var modo = String(L.blendingMode);
        if (!(L.blendingMode == BlendingMode.ADD || L.blendingMode == BlendingMode.SCREEN ||
              modo.indexOf("ADD") >= 0 || modo.indexOf("SCREEN") >= 0)) continue;
        conferidas++;
        var T = L.property("Transform"), pior = null;
        for (var t = Math.max(0, L.inPoint); t < L.outPoint; t += 1 / 15) {
            if (T.property("Opacity").valueAtTime(t, false) < 3) continue;
            var p = T.property("Position").valueAtTime(t, false), a = T.property("Anchor Point").valueAtTime(t, false);
            var s = T.property("Scale").valueAtTime(t, false), r = T.property("Rotation") ? T.property("Rotation").valueAtTime(t, false) : 0;
            var sx = s[0] / 100, sy = s[1] / 100;
            var x0 = p[0] - a[0] * sx, x1 = x0 + L.source.width * sx, y0 = p[1] - a[1] * sy, y1 = y0 + L.source.height * sy;
            var falta = Math.max(x0, 0) + Math.max(c.width - x1, 0) + Math.max(y0, 0) + Math.max(c.height - y1, 0);
            if (Math.abs(r) > 0.5) falta += 1; // rotação: os cantos entram no quadro; tratar como suspeito
            if (falta > 0.5 && (!pior || falta > pior.falta)) pior = { t: t, falta: falta, ret: [x0, y0, x1, y1] };
        }
        if (pior) {
            problemas++;
            writeLn("ALERTA " + L.name + ": borda dentro do quadro em t=" + pior.t.toFixed(2) + "s (camada em x " +
                Math.round(pior.ret[0]) + "–" + Math.round(pior.ret[2]) + ", y " + Math.round(pior.ret[1]) + "–" +
                Math.round(pior.ret[3]) + "; quadro " + c.width + "x" + c.height + "). Aumente a escala ou use bordas com alfa 0.");
        }
    }
    writeLn(conferidas + " overlays em Add/Screen conferidos; " + problemas + " com borda entrando no quadro.");
})();
