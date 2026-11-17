# Suporte para gabinete torre

Moldura que tira o gabinete do carpete: 40 mm de altura, borda de 10 mm que segura o gabinete,
vão central aberto para a fonte puxar ar por baixo. Montagem sem parafuso nem cola:
chaves "gravata-borboleta" encaixadas de cima para baixo.

Medida interna padrão: **230 x 480 mm** (externa 242 x 492 mm).
Para ajustar ao seu gabinete, mude `CASE_W` / `CASE_D` em `gerar_suporte.py` e rode
`pip install manifold3d trimesh numpy && python3 gerar_suporte.py`.

## Imprimir
| Arquivo | Qtd |
|---|---|
| canto.stl | 4 (o mesmo arquivo serve pros 4 cantos) |
| viga.stl | 4 |
| chave.stl | 8 |

Todas as peças cabem numa mesa 220 x 220. Imprimir na posição do arquivo (face plana na mesa),
sem suporte. Sugestão: PETG ou PLA, 4 paredes, 20–25% de infill gyroid, camada 0,2–0,28 mm.
`montagem_preview.stl` é só para visualizar, não imprimir.
