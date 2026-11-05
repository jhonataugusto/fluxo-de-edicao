---
name: direcao-de-cena
description: Raciocina sobre enquadramento "3D" (imagens 2D em espaço 3D com câmera virtual), posicionamento de texto e elementos, interação entre elementos e o personagem, e ritmo para retenção, no estilo do jonato. Use ao planejar, montar ou revisar um plano ou uma intro de motion (EffectCraft, After Effects, Blender), quando pedirem "onde coloco esse texto", "que ângulo uso aqui", "isso está bem enquadrado?", "melhora a composição", "revisa os planos", "por que esse plano não funciona", ou antes de renderizar uma motion. Combina com motion-design (timing e easing) e motion-design-critique (diagnóstico de erro).
---

# Direção de cena

Você é o diretor de fotografia e o diretor de arte da motion. Seu trabalho é decidir **onde a câmera está, o que o quadro mostra, onde cada texto e elemento fica e como eles conversam**, e justificar cada escolha. Não é dar sugestões soltas: é uma ficha por plano, com números e com o porquê.

## Fontes de verdade (nessa ordem)
1. **Pedido do jonato no momento.**
2. **Perfil dele** (gosto): `C:\Users\jhonata\Documents\fluxo-video\perfis\jonato\` — `identidade.md` (cores, fontes, OC), `estilo-motion.md`, `estilo-camera.md`, `analises\sintese.md`. Leia antes de decidir. Onde o perfil fala, ele vence sobre o "bom senso genérico".
3. **Ofício pesquisado** (vale para qualquer vídeo), nesta skill:
   - `references/camera-e-profundidade.md` — lente, ângulo, movimento, paralaxe, cartões 2D no espaço 3D, transições espaciais.
   - `references/texto-e-elementos.md` — área segura, UI do YouTube, tempo de leitura, hierarquia, olhar, interação com o OC.
   - `references/edicao-e-retencao.md` — corte, ritmo, gancho, som, erros comuns.
   - `references/fontes.md` — de onde veio cada regra e o quanto confiar.

**Inegociáveis (vencem até o perfil):** legibilidade (área segura, tempo de leitura, contraste) e acessibilidade (no máximo 3 flashes por segundo em área grande). Se o pedido quebrar uma delas, avise e proponha a alternativa mais próxima.

## Como raciocinar sobre um plano
Para cada plano, responda nesta ordem. Uma decisão sem porquê não vale.

1. **Intenção.** Que frase da narração o plano serve, e o que o espectador deve sentir/entender? (Murch: emoção > história > ritmo > olhar > plano 2D > espaço 3D. Se dois critérios brigarem, sacrifique de baixo para cima.)
2. **Assunto único.** Qual é o ponto focal? Só um por vez. O resto fica parado, escurecido ou fora de foco.
3. **Câmera.**
   - Ângulo pelo significado: contra-plongée = poder/ameaça/admiração; plongée e top-down = contexto, mapa, vulnerabilidade; dutch = algo errado (sutil) ou crise (forte); frontal = documento, leitura.
   - Lente: 35–50 mm padrão; ~20–28 mm para escala/vertigem (aproxime a câmera); 85 mm+ para isolar e achatar.
   - Movimento amarrado à frase: push-in = ênfase/revelação; pull-out = contexto/escala; orbit = assunto central e mundo girando; rack focus = trocar a atenção.
   - Perfil: câmera nunca parada (deriva 1–5 %/s); no gancho, afastamento de 10–35 %/s; na revelação, aproximação de 15–25 %/s.
4. **Profundidade.** Frente (parcial, saindo do quadro), meio (assunto), fundo (amplo). Use várias pistas juntas: oclusão, tamanho relativo, névoa/desfoque no fundo, sombra de contato, paralaxe.
5. **Composição no quadro final** (não na cena 3D). Terços, espaço de respiro na direção do olhar/movimento, linhas-guia levando ao assunto. Confira nos 3–5 momentos-chave do plano: início, revelação, ênfase, assentamento, saída.
6. **Texto.** Dentro da área segura e fora das zonas da UI do YouTube. No máximo 2 linhas e uma ideia. Entra junto com a palavra falada (até ~3 frames antes) e fica parado durante a leitura. Tempo mínimo = máx(1 s; palavras × 0,6 s). O rótulo fica junto da coisa, não num canto.
7. **Interação.** Como este elemento se relaciona com os outros? Causa e efeito: empurra, revela por máscara ou abre o próximo. Nada aparece do nada. O OC olha ou aponta para o que importa 4–8 frames antes de surgir, e reage depois da revelação (0,5–1,5 s) como plateia.
8. **Corte para o próximo plano.** Eye-trace: o foco novo começa perto de onde o anterior terminou. Direção de tela consistente (vetor do vídeo). Corte na ação ou no movimento. Transição com a assinatura do perfil (clarão), nunca dissolve longo nem tela preta não intencional.
9. **Som.** Cada movimento importante tem SFX no frame exato; silêncio antes da revelação principal.

## Checagem visual (obrigatória antes de dar um plano por bom)
Não confie no código: olhe o quadro.
1. Renderize os momentos-chave (`effectcraft-cli --bridge 47322 render-frame --comp "<comp>" --time T --max-side 1280 --out F.png`).
2. Rode `python -P ~/.claude/skills/direcao-de-cena/scripts/guias_quadro.py F.png [mais.png ...]`. O script grava `F_guias.png` (terços, área segura de 5 %, zonas da UI do YouTube, centro) e imprime alertas de conteúdo forte nas zonas da UI e nas bordas.
3. Rode `effectcraft-cli --bridge 47322 script ~/.claude/skills/direcao-de-cena/scripts/checar_bordas.jsx` (ou `script checar_bordas.jsx F.ecproj` sem o app). Ele confere, a cada 1/15 s, se algum overlay em Add/Screen (leak, flare, partícula em vídeo) deixa a borda entrar no quadro: a "linha reta vazando" que o olho pega na hora e o detector de pixel não pega. Zero alertas antes de renderizar.
4. Leia os `_guias.png` e responda: o ponto focal está num terço ou centro intencional? Algum texto invade zona proibida? Aparece borda de cartão ou vazio? Há mais de um acento neon? A leitura em Z leva ao assunto?

## Formato da resposta
Por plano, uma ficha curta:

```
PLANO S3 (3,0–4,5 s) — "em 7 dias"
Intenção: choque do prazo curto → energia
Câmera: dutch 28 mm, roll 14→9°, contra-plongée leve, push-in 20 %/s   porquê: instabilidade + ênfase
Profundidade: OC em frente à direita (sai do quadro), letras no meio, poeira no fundo
Texto: "7 DIAS" no terço superior central, 0,5 s parado após assentar (2 palavras → 1,2 s total)
Interação: OC olha para o "7" 6 frames antes de ele virar; impacto no "S" com tremida
Corte: foco termina no centro → próximo plano começa com o OC no centro
Checagem: [OK | ALERTA + correção]
```

Em revisões, ordene os problemas por impacto (legibilidade > intenção/foco > continuidade > polimento) e dê a correção em números (posição, mm, tempo, opacidade).

## Ferramentas
- EffectCraft: a intro é montada por `etapa_NN.jsx` com `lib.jsx` (`camada`, `camera`, `chaves`, `ambiente`) na pasta `_CLAUDE\effectcraft` do vídeo. `P(x,y,z)` é relativo ao centro; y para baixo; z positivo afasta da câmera.
- Sempre GPU para render.
- Assets (overlays, SFX, fundos, presets): pack local em `C:\Users\jhonata\Documents\fluxo-de-edicao\assets\` (fora do Git). O que tem em cada pasta e como usar: `ASSETS.md` na raiz do repositório. Imagens da internet: registre origem e licença em `_CLAUDE\assets_web\creditos.md`.
