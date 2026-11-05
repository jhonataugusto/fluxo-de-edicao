# Assets (pack de efeitos e sons)

Os assets **não vão para o GitHub**: são packs de terceiros (cerca de 1 GB) e a licença deles não permite redistribuir. Eles ficam só no computador, numa pasta `assets/` na raiz deste repositório (ignorada pelo `.gitignore`):

```
C:\Users\jhonata\Documents\fluxo-de-edicao\assets\
```

Em outro computador: clone o repositório e copie o pack para `<repo>\assets\` com a mesma estrutura. As skills e os scripts procuram os arquivos lá.

## O que tem e como usar
| Pasta | Arquivos | Uso no fluxo |
|---|---|---|
| `Overlay/` | 46 vídeos (light leaks, partículas, brasas, shockwave, explosão, plexus, speed lines) | Por cima da motion em **Screen/Add**. Copie o que for usar para `_CLAUDE\overlays\` do vídeo (nome sem espaço). Rode `skills/direcao-de-cena/scripts/checar_bordas.jsx` antes do render: overlay que desliza não pode mostrar a borda. |
| `Sfx/Ultimate sfx pack/Ultimate Sfx Pack Collection/` | 205 sons em `WHOOSHES N BUILDUPS`, `IMPACTS`, `SPECIAL`, `Sfx (110+)`, `GUN SOUNDS`, `SWORD SOUNDS`, `VOICES` | Banco de SFX. Exemplo de mixagem por evento (alinha pelo pico, início ou fim): `exemplos/intro-rusdot/scripts/som3d_v03.py`. Para clima "documento/tech", evite armas, espadas e vozes. |
| `Compositing/BG/` | Fundos (jpg/png/webp) | Fundo de cartão ou textura em cena 2.5D. |
| `CC/`, `Presets/`, `Shake/`, `One Frame/`, `Compositing/*.ffx`, `Transition Effects/` | Presets `.ffx` do After Effects | O **EffectCraft não lê `.ffx`**. Use como referência e recrie nativamente: correção de cor por efeito, tremida por expressão (seno com decaimento, ver `exemplos/intro-rusdot/effectcraft/etapa_07.jsx`). |
| `Project File/` | 4 projetos `.aep` com o vídeo de exemplo | Referência de estilo. Só abrem no After Effects. |

## Assets da internet
Logos e imagens de reação (memes, anime chibi, gatos) podem ser baixados quando a cena pedir. Registre sempre a origem e a licença em `_CLAUDE\assets_web\creditos.md` do vídeo (exemplo: `exemplos/intro-rusdot/creditos.md`).
