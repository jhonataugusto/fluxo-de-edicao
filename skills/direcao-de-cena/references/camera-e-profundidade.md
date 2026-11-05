# Câmera e profundidade em motion 2.5D

Imagens 2D (cartões) num espaço 3D com câmera virtual. Formato: **regra → porquê → como aplicar**. `[síntese]` = inferência a partir das fontes, sem número de fonte. Fontes em `fontes.md`.

## 1. Lente e perspectiva
- **A perspectiva vem da distância; a lente só recorta.** → Da mesma posição, 15 mm recortada = 70 mm (Fstoppers). → Para mais paralaxe, câmera perto + lente aberta. Para achatar (mapa, documento), câmera longe + tele.
- **35–50 mm é o padrão; ~20 mm só para drama.** → 35–50 mm ≈ olho humano; com 20 mm a câmera chega mais perto, o fundo fica pequeno e distante (Video Copilot). → 20–28 mm para escala, poder e vertigem; 85 mm+ para isolar o assunto e para planos "de documento".
- **Lente longa = foco mais curto.** → Na mesma situação, 85 mm desfoca bem mais que 35 mm (School of Motion). → Com 85 mm, diminua a abertura (aperture) para o desfoque não engolir o assunto.
- No EffectCraft/AE: `Zoom = largura × mm / 36` (sensor de 36 mm). Em 1920 px: 28 mm ≈ 1493, 35 mm ≈ 1867, 50 mm ≈ 2667, 85 mm ≈ 4533.

## 2. Ângulo e movimento comunicam
| Escolha | Comunica | Quando usar |
|---|---|---|
| Contra-plongée (câmera baixa) | poder, ameaça, admiração | o "vilão", o número enorme, o personagem heroico |
| Plongée / top-down | vulnerabilidade, contexto, olhar de observador | mapas, "visto de cima", personagem pequeno diante do problema |
| Dutch (rolagem) | sutil: algo errado; forte: crise | só quando o roteiro pede instabilidade |
| Push-in | ênfase, intimidade, revelação | a frase-chave, o detalhe |
| Pull-out | contexto, escala, alívio | mostrar o tamanho da coisa, fechar bloco |
| Orbit | assunto central, mundo girando | apresentar um objeto/logo |
| Rack focus | trocar a atenção | de um elemento para outro sem corte |

- **Uma intenção de câmera por frase narrada.** → Kurzgesagt amarra um movimento a cada linha do texto e a narração define o timing. → Cada keyframe de câmera nasce de uma palavra da transcrição.

## 3. Composição em profundidade
- **Três planos: frente, meio, fundo.** → A paralaxe nasce da diferença de velocidade: perto passa rápido, longe passa devagar (Motion Array, AEJuice). → Frente parcialmente fora do quadro (poeira, borda de cartão desfocada), assunto no meio, fundo amplo.
- **Várias pistas de profundidade juntas** (NYU): oclusão (a mais forte), tamanho relativo, perspectiva atmosférica (longe = menos contraste, mais névoa/cor), gradiente de textura, altura no quadro, sombra. → Fundo com véu de cor e menos contraste; frente sobrepondo o meio; sombra de contato no assunto.
- **[síntese] Terços e linhas-guia valem para o quadro final, não para a cena.** → Confira pela câmera em 3–5 composições-chave por sequência: início, revelação, ênfase, assentamento, saída (Studio Matrx).
- **Espaço de respiro (lead room)** na direção para onde o assunto olha ou se move.

## 4. Câmera virtual: boas práticas
- **Nunca linear; sempre ease.** → Linear arranca e para seco, parece robô; com ease a câmera parece grua/dolly real (Studio Matrx). → Influência 33–60 % para movimentos sutis, 60–85 % para "desenhados"; 80 %+ sai muito lento e acelera no fim. Linear só em deriva contínua que atravessa o corte.
- **Devagar e com poucos keyframes.** → "Na dúvida, desacelere" (Studio Matrx): 3–5 keyframes em 10–15 s, holds quase parados nas vistas-chave. → Rolagem em 0° salvo intenção; giro rápido parado no lugar enjoa (gire andando).
- **[síntese] Câmera e elementos não se movem forte ao mesmo tempo.** → Um assunto claro por movimento. → Se a câmera anda muito, os cartões ficam quase parados, e vice-versa.
- **Motion blur com obturador de 180°** (padrão de cinema e do AE). → Suba só se texto em movimento "picotar"; antes, reduza a velocidade.
- **Profundidade de campo sutil.** → Não passe do que uma câmera real faria (School of Motion). → Foco sempre no assunto; nunca um objeto desfocado na frente cobrindo o texto. Desfoque forte só para frente/fundo decorativos.
- **Cartão empurrado para trás precisa crescer.** → Tamanho aparente cai com a distância: para manter o tamanho, escala × (distância ÷ zoom). → Expressão AE: `C=thisComp.activeCamera; d=length(fromWorld(C.toWorld([0,0,0])), fromWorld(toWorld(anchorPoint))); (d/C.zoom)*value`. Espaçamento de ~500 px entre camadas é um bom começo.
- **Esconda bordas e não achate o cartão.** → A ilusão quebra ao ver a borda, o vão atrás do recorte ou o cartão girado perto de 90° no X. → Fundo 2D maior que o quadro (ou camada 2D no fim da pilha); fundo desfocado preenchendo vãos; limite a órbita; movimentos pequenos funcionam melhor.
- **Overlay de luz que desliza (leak, flare) nunca mostra a borda.** → Com o modo Add/Screen a borda do PNG/vídeo vira uma linha reta clara no quadro (erro real da intro Rusdot v03: leak de 1920 px deslizando 340 px deixou a borda em x≈148). → Brilho gaussiano sem platô (o alfa vai a 0 suave nas bordas; máscara retangular "feather" cria uma caixa visível), escala com folga (≥ 100 % + deslize ÷ largura; 130 % para 340 px) e `scripts/checar_bordas.jsx` antes do render.
- **Una a cena com grão, névoa e light leaks** (camada de acabamento comum a tudo).

## 5. Transições espaciais
- **Direção de tela consistente (regra dos 180°).** → O que sai pela esquerda entra pela direita; cruzar o eixo desorienta. Dá para cruzar com um movimento contínuo de câmera atravessando o eixo ou com um plano neutro no meio. → [síntese] Defina o vetor do vídeo (ex.: "antes/Godot" à esquerda, "depois/Rusdot" à direita) e mantenha.
- **Whip pan:** mesma direção e velocidade nos dois lados, blur escondendo o corte. ~8–10 frames no total (5 antes, 5 depois). Pouco: o excesso cansa.
- **[síntese] Câmera atravessando elementos:** emende o fim de um movimento com o começo do próximo, na mesma direção e velocidade. Atravesse só cartões feitos para isso (nuvem, papel, texto).
- **Câmera sempre andando entre camadas** dá continuidade (ex.: Z de 0 a −1600 em 5 s, Noble Desktop).
