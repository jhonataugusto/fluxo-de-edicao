# Montagem do fluxo de edição

Fase atual: 3 (perfil em conferência) · Atualizado em 2026-11-04

## Ambiente
- Sistema: Windows 11 Pro · Python: 3.13 · FFmpeg: 9.0.2 · Node.js: 24.20 · Git: 2.55 · GPU: RTX 3060 Ti 8 GB
- Blender 5.2.3 LTS (Steam): motion 3D sem interface testado e aprovado no FilmCraft.
- Instalado nesta montagem (2026-11-04): yt-dlp, opencv-python, numpy, scenedetect (pip --user).
- HyperFrames: ainda não liberado (o `npx` foi bloqueado pela permissão automática; liberar antes de usar).

## Decisões
- Revisão: programa de edição — **FilmCraft 0.6**. Teste de 2026-11-04 (`Documents\teste-filmcraft`): importa FCP7 XML com mídia vinculada; ProRes 4444 com transparência ok; tem `filmcraft-cli` (importar, inspecionar, renderizar frame, exportar) e servidor MCP.
- Tipo e formato: <pendente>
- Pastas: ferramentas `Documents\fluxo-video`; projeto <pendente> (ex.: `Documents\videos\<nome>`)
- Transcrição: <pendente> (sugestão: local na GPU)
- Notas faladas: <pendente>
- Animação: <pendente> (Blender testado; HyperFrames a liberar)
- Câmera: <pendente>
- Som: <pendente>
- Revisões: <pendente>
- Nomes: prefixo <pendente>; skill mestra /<pendente>

## Perfil
- jonato (`perfis/jonato/`):
  - [x] referências 01 Odda e 02 Cellbit (0–30 s), medidas e folhas em `analises/`
  - [x] `analises/sintese.md`
  - [x] `identidade.md` — confirmado no grill de 2026-11-04: clima Cellbit + movimento Odda; paleta muda por vídeo ("tinta e sinal" = reserva); personagem como card de narrador
  - [x] `estilo-motion.md`, `estilo-camera.md`
  - [x] fontes em `fontes/` (Big Shoulders Black e Montserrat ExtraBold instanciadas com fontTools)
  - [ ] `estilo-cortes.md` (precisa de uma gravação sua)
  - [ ] `estilo-som.md` (só o volume foi medido: 01 −16,7 LUFS, 02 −20,0 LUFS)
  - [ ] curvas de animação (medir na primeira motion real)

## Fluxo aprovado
<pendente — fase 4>

## Skills escritas
- [ ] regras comuns

## Introdução de teste (2026-11-04)
- Vídeo: `Documents\videos\eu_recriei_a_godot_em_rust\` (só `audio_teste.m4a`, 36,6 s). Trabalho em `_CLAUDE\`.
- Paleta do vídeo: laranja Rusdot `#DB310B` (acento) + azul Godot `#478CBF` ("antes").
- Transcrição: faster-whisper large-v3-turbo (rodou na CPU: falta `cublas64_12.dll`; para GPU, instalar o pacote nvidia-cublas-cu12).
- Motions no Blender (`scripts/cenas.py`, 7 cenas), fundo/clarões/SFX sintetizados (`scripts/fundo_som.py`), XML FCP7 (`scripts/gerar_xml.py`).
- Instalado: faster-whisper, fonttools.

## Próximo passo
Jonato assiste à intro de teste e dá o retorno (vira caderno de aprendizados); depois, fase 2 (entrevista).
