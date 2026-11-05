# Síntese das referências — perfil jonato

Analisado em 2026-11-04 com `ferramentas/analisar_ref.py` (fluxo óptico + RANSAC, PySceneDetect, ebur128).
Trechos: 0–30 s de cada vídeo. Medidas completas em `*_medidas.json`; quadros em `*_folha_NN.jpg`.

## Ref 01 — Odda, "RECRIEI SUBWAY SURFERS EM 24 HORAS!" (NchCN4x3w1Q, 59,94 fps)
O que chamou a atenção (jonato): o vídeo mais visto do canal; edição e motions.
- Introdução 100% motion graphics, sem rosto.
- **Palco:** ícones brancos em 3D (contorno grosso, leve volume) sobre um "chão" de cor única com sombra suave. Cada trecho tem uma cor (vermelho → vinho → azul-marinho → preto).
- **Câmera virtual nunca para:** afastamento contínuo de 10 a 36 %/s em 7 de 9 planos (0 % dos frames parados nesses planos); aproximação só em 2 planos (+13 e +24 %/s).
- **Prints e cards** em perspectiva 3D, com borda branca fina e sombra, entrando de fora da tela e se empilhando.
- **Transformação de ícone** (controle → relógio) por um wipe de traço branco (2,67 s).
- **Texto** com revelação embaralhada ("7 MESES", 15,2–16,6 s).
- **Smash zoom** no rosto (16,73 s, ~6 frames ≈ 0,1 s) seguido de corte seco.
- **Glow neon** ciano no "-24H" com reflexo no chão (25 s).
- **Silêncio visual:** ~2 s de preto (26,7–28,75 s) antes da revelação final (personagem + logo, aproximação +24 %/s).
- Ritmo: 9 cortes em 30 s (3,0 por 10 s); plano mediano 2,56 s. Transições fortes de ~11 frames (0,18 s) em 22,04 e 24,82 s. Áudio −16,7 LUFS.

## Ref 02 — Cellbit, "CICADA 3301 – PARTE 1" (Ep5qn8pLCMA, 23,976 fps)
O que chamou a atenção (jonato): estilo "documentário / ARG".
- **Rosto em fundo escuro** com luz verde de lado (brilho médio 14–24 de 255).
- **Transição assinatura:** clarão de luz verde (light leak) de 1–3 frames (0,04–0,12 s) em 7 de 10 cortes.
- **Documentos e telas** em perspectiva, com deriva lenta (1–5 %/s); a câmera quase nunca para.
- **Texto máquina de escrever** acompanhando a narração (~12–15 caracteres/s, estimado pelos quadros), fonte fina e arredondada; depois a câmera "voa" para dentro do texto (até 80 %/s, 6,1–12,9 s).
- **Camadas ARG:** chuva de texto cifrado, pontos vermelhos sobre o documento, ícones com glitch e linhas de varredura (chaves vermelha/azul), QR codes, mapa-múndi em dupla exposição sobre a filmagem, poeira flutuando, grão.
- **Cor:** fundo quase preto, **um único** acento neon (verde) e vermelho só para alerta ("lobinho97" offline, "CHAT ENIGMA CICADA").
- Ritmo: 10 cortes em 30 s (3,33 por 10 s); plano mediano 2,38 s. Áudio −20,0 LUFS (mais baixo, mais "cinema").

## Síntese: "dossiê animado"
O que as duas têm em comum e vira regra do perfil:
1. **A câmera nunca está parada.** Odda afasta rápido (10–36 %/s); Cellbit deriva devagar (1–5 %/s). Perfil: deriva lenta por padrão, afastamento rápido nos momentos de energia.
2. **Ritmo de ~3 cortes a cada 10 s** (plano mediano ~2,4–2,6 s) nas duas.
3. **Um acento de cor só**, sobre fundo escuro ou monocromático. No perfil, o acento é o ciano dos olhos do personagem.
4. **Transição curta e luminosa** (light leak de 1–3 frames ou wipe de ~0,18 s), nunca dissolve longo.
5. **Pausa antes da revelação** (preto ou quase silêncio de ~1–2 s).

O que é de cada uma e entra como repertório (catálogo), não como regra:
- Odda: palco de ícones 3D com chão colorido, cards em perspectiva empilhando, troca de cor por trecho, smash zoom, texto embaralhado.
- Cellbit: máquina de escrever, câmera voando para dentro do texto, camadas cifradas, dupla exposição, grão e poeira.

## O que ainda não foi medido
- **Curvas de animação** (comparação com `power2.out`, `expo.out`…): medir na primeira motion real, quadro a quadro.
- **Som** (densidade e tipo de SFX): só o volume integrado foi medido.
