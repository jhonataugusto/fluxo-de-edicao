# Correções para Blender 5.x (vale sobre as outras referências)

Conferido no Blender 5.2.3 LTS em 2026-11-04 (`blender -b --factory-startup`). Quando outra referência desta skill disser outra coisa, vale este arquivo.

## Animação (layered actions)
- `action.fcurves` **não existe mais** (removido no 5.0). Os trechos de `bpy-keyframing.md` e `fcurve-modifiers.md` que usam `action.fcurves` quebram.
- Caminho atual:
  ```python
  from bpy_extras import anim_utils
  ad = obj.animation_data
  cb = anim_utils.action_get_channelbag_for_slot(ad.action, ad.action_slot)
  for fc in cb.fcurves:
      for kp in fc.keyframe_points:
          kp.interpolation = "BEZIER"
      mod = fc.modifiers.new("NOISE")  # modificadores de F-curve continuam iguais
  ```
- Alternativa que não depende da API de F-curves: definir `bpy.context.preferences.edit.keyframe_new_interpolation_type` antes de inserir as chaves, ou gravar uma chave por quadro com a curva calculada em Python.
- `obj.location[0] = 5.0` funciona normalmente (o `blender-diagnostics.md` diz que dá TypeError: está errado).

## Motor de render
- O identificador do EEVEE é `"BLENDER_EEVEE"` (não `"BLENDER_EEVEE_NEXT"`). Melhor ler o enum:
  `[i.identifier for i in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items]`.
- O EEVEE atual tem ray tracing (`scene.eevee.use_raytracing`) e iluminação global. As tabelas que dizem "EEVEE só tem reflexo screen-space / sem GI" estão desatualizadas.
- **Bloom do EEVEE não existe** (`use_bloom` removido no 4.2). Glow agora é no compositor: nó Glare. No 5.x o compositor fica em `scene.compositing_node_group` (crie um node group de compositor e atribua).
- Os toggles de SSR/Refraction, Contact Shadows por luz e DOF nas Render Properties do EEVEE antigo não existem. A profundidade de campo é só na câmera (`cam.data.dof.use_dof`, `focus_distance` ou `focus_object`, `aperture_fstop`).
- Cycles na GPU: além de `scene.cycles.device = "GPU"`, configure `bpy.context.preferences.addons["cycles"].preferences.compute_device_type` ("CUDA"/"OPTIX") e ative os devices (`get_devices()`).

## Materiais
- Transparência no EEVEE: `mat.surface_render_method = "BLENDED"` (ou `"DITHERED"`). `blend_method` ainda existe no 5.2, mas o EEVEE atual usa `surface_render_method`.
- Procure nós pelo tipo (`n.type == "BSDF_PRINCIPLED"`), nunca pelo nome (nomes são traduzidos).
- Volumes (neblina, feixes de luz): funcionam no EEVEE atual, mas o resultado final mais confiável é no Cycles.

## Geometry Nodes
- O tipo do nó de saída do grupo é `"NodeGroupOutput"` (não `"NodeGroupOutputNode"`).

## Render e saída
- Fundo transparente: `scene.render.film_transparent = True`, além de `color_mode = "RGBA"` (a referência de render não menciona o `film_transparent`).
- View transform e looks: leia os enums de `scene.view_settings` em vez de fixar nomes (variam por versão e pela config de cor).
- No Windows não existe `/tmp`: use a pasta de trabalho do vídeo (ex.: `_CLAUDE/`).

## Regras locais (fluxo do jonato)
- Render em segundo plano (`blender -b`) faz parte do fluxo de edição dele: quando a etapa pedir um render, ele pode ser feito por script e em segundo plano, avisando antes quanto tempo deve levar.
- Nada de serviços de geração pagos sem o "sim" explícito do jonato, um por vez.
