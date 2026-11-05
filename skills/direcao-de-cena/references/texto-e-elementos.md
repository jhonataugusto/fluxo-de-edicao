# Texto, elementos e interação

Formato: **regra → porquê → como aplicar**. Heurísticas de criador (não estudo) vêm marcadas. Fontes em `fontes.md`.

## 1. Onde o texto pode ficar (1920×1080)
| Zona | Limite | Fonte |
|---|---|---|
| Área segura de gráficos | 5 % por lado: x 96–1824, y 54–1026 | EBU R95 (verificado) |
| Área segura de ação | 3,5 % por lado: x 67–1853, y 38–1042 | EBU R95 |
| Faixa de baixo (barra de progresso, controles, legendas automáticas) | **~15 % de baixo: y > 918** — nada importante | convenção; o YouTube não publica pixels para 16:9 orgânico |
| Faixa de cima (título e botões ao pausar/passar o mouse) | ~10 % de cima: y < 108 — evitar em momentos-chave | convenção |
| Tela final | últimos 5–20 s; até 4 elementos; cards e marca d'água somem | YouTube Help (verificado) |

→ Texto principal no terço central e superior. Nos últimos 5–20 s, fundo sem texto importante.

## 2. Texto em tela
- **Tempo em tela: dá para ler duas vezes.** → SSW: 2× a 200 palavras/min ≈ 0,6 s/palavra; Netflix pt-BR: 17 caracteres/s, mínimo 5/6 s, máximo 7 s por legenda. → `duração = máx(1 s; palavras × 0,6 s)`, teto ~7 s.
- **Uma ideia por tela, até 2 linhas de ~42 caracteres.** → Redundância (Mayer): imagem + narração rende mais que imagem + narração + o texto inteiro. → Na tela só palavra-chave, nome, data, número. Nunca a frase narrada inteira.
- **Texto entra com a palavra falada.** → Contiguidade temporal (Mayer, efeito grande). → Ancore no início da palavra na transcrição, no máximo ~3 frames antes.
- **Anime a entrada e pare para a leitura.** → Texto em movimento compete com a leitura. → Entrada de 200–400 ms com desaceleração; saída ~200 ms com aceleração; parado durante a leitura. Palavra por palavra só em frase curta. Exceção do perfil: máquina de escrever em Plex Mono a ~12–15 caracteres/s acompanhando a narração.
- **Tamanho e contraste pensando no celular.** → Contraste ≥ 4,5:1 (WCAG). → Corpo ≥ 48 px (~4,5 % da altura), título ≥ 80 px em 1080p; sombra, contorno ou caixa sobre fundo com textura (grão, poeira, leaks). Teste o quadro reduzido a ~25 % (tamanho de celular).
- **Texto em 3D:** inclinação máxima de ~25–30° em relação à câmera no momento da leitura; desfoque zero no texto que precisa ser lido; nunca atrás de partícula ou leak forte durante a leitura.

## 3. Hierarquia e olhar
- **Um ponto focal por vez.** → Atenção sincronizada (Smith & Mital): quando só uma coisa se move, quase todos olham para ela; movimento, contraste e brilho atraem o olho. → Só o elemento novo se move; o resto parado ou escurecido em 30–50 %.
- **Sinalize em vez de adicionar.** → Sinalização (Mayer). → Círculo, sublinhado animado, push-in ou escurecer o entorno, em vez de mais um elemento.
- **Corte o interessante-mas-irrelevante.** → Coerência (Mayer); "detalhes sedutores" atrapalham (g = −0,33, Sundararajan & Adesope 2020), pior quando o espectador não controla o ritmo. → Cada elemento serve à frase daquele momento. Decoração (poeira, grão, leaks) fica em baixo contraste.
- **Rótulo junto da coisa.** → Contiguidade espacial. → Etiqueta presa ao objeto, não em caixa no canto. Elementos ligados se movem juntos (destino comum); elementos distintos entram em cascata de 50–100 ms.
- **Eye-trace entre planos.** → O olho deve começar o plano novo perto de onde terminou o anterior (Frame.io). → Coloque o novo foco perto do antigo; para conferir, sobreponha os dois quadros. Quebre só de propósito, para chocar.
- **Leitura em Z** (convenção de design): do maior para o menor, de cima à esquerda para baixo à direita. Personagem do lado oposto ao texto, equilibrando.

## 4. Interação entre elementos e o OC
- **O OC olha/aponta para o que importa.** → O gesto de apontar do apresentador melhora a busca visual e o aprendizado em vídeo-aulas (Pi et al.); olhar e apontar deslocam a atenção automaticamente. → Cabeça/olhos do OC viram para o elemento 4–8 frames antes de ele surgir. No 2.5D: posicione o OC num terço, com o olhar apontando para o assunto e espaço de respiro nessa direção; troque o PNG de emoção no beat.
- **Reação como plateia.** → O plano de reação diz ao espectador como sentir. → Depois da revelação, 0,5–1,5 s de reação do OC (susto, desconfiança, riso). É também o alívio cômico nos trechos densos.
- **Causa e efeito físicos.** → Relações ficam legíveis (UX in Motion: parentesco, máscara, sobreposição). → Um elemento empurra, revela por máscara ou abre o próximo; impacto gera tremida/poeira/flash proporcional ao "peso". Nada surge do nada.
- **12 princípios aplicados:** desaceleração em tudo (linear só em mecanismo), antecipação curta antes de grandes entradas, overshoot leve e follow-through em cartões e setas, squash/stretch só no personagem.
- **Mostre, não diga.** → Princípio multimídia; desenho contínuo engaja mais que slide parado (Guo et al.). → Construa o gráfico/mapa ao vivo, sincronizado com a fala. A imagem deve acrescentar ou contrastar com a narração, nunca repetir (Vox).

## 5. Ritmo visual e acessibilidade
- **Algo novo a cada ~5–10 s; mais denso no gancho.** (heurística de criadores: ~1 troca a cada 1,7 s nos primeiros 30 s). Perfil: ~3 trocas a cada 10 s, plano mediano 2,4–2,6 s. → A novidade pode ser pequena: push-in, destaque, reação do OC.
- **Excesso de estímulo também derruba.** → Carga cognitiva; segmentação (Mayer). → Depois de bloco denso, 2–4 s de respiro com imagem simples.
- **Flashes: no máximo 3 por segundo** em área grande (WCAG 2.3.1: variação de luminância ≥ 10 %; vermelho saturado conta à parte). Abaixo de ~25 % da tela, tolera mais. → Glitch/ARG piscando ≤ 3/s ou em área pequena. Clarões de transição: espaçados ≥ 0,4 s.
- **Capítulos de ≤ 6 min** com gancho próprio (Guo, Kim & Rubin: engajamento mediano ≤ 6 min; fala energética engaja mais).
