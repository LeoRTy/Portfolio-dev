# Suporte para gabinete torre com ajuste por clique

Feito para o **Dell Pro Max Tower T2 (FCT2250)**, com base de 187,7 x 438 mm.
Visual: face externa inclinada com frisos verticais, cantos bem arredondados e quina de cima suave
(ver `render_*.png`). É uma moldura de 40 mm de altura com vão central aberto para a fonte puxar ar por baixo.
Montagem sem parafuso e sem cola: as peças se ligam por chaves "gravata-borboleta".

## Ajuste (batentes com clique)
Em cima da moldura há 12 trilhos. Em cada um entra um **batente** que desliza para dentro e para fora
e trava com um clique a cada 2 mm (8 posições, 16 mm de curso). Cada batente se ajusta sozinho,
então dá para centralizar e esquadrejar o gabinete encostando todos os batentes nele.

Faixa aceita: largura 171,7 a 203,7 mm e profundidade 422 a 454 mm.
Moldura: 247,7 x 498 mm na base (227,7 x 478 mm no topo).

## Como montar
1. Monte a moldura: 4 cantos + 4 vigas, encaixando as chaves de cima para baixo nas juntas.
2. Encaixe os batentes nos trilhos pela face externa da moldura, todos puxados para fora.
3. Coloque o gabinete e empurre cada batente até encostar no gabinete (clique, clique...).

## Imprimir
| Arquivo | Qtd |
|---|---|
| canto.stl | 4 |
| viga.stl | 4 |
| chave.stl | 8 |
| batente.stl | 12 (mínimo recomendado: 8, dois por lado) |

Todas as peças cabem numa mesa 220 x 220 e não precisam de suporte; imprima na posição do arquivo.
Moldura/chaves: PETG ou PLA (branco fosco fica igual ao render), 4 paredes, 20–25% gyroid. **Batentes: PETG de preferência**
(as hastes-mola do clique duram mais), 100% de preenchimento ou 5+ paredes, camada 0,16–0,2 mm.

Se o clique ficar duro ou solto demais, ajuste `NOTCH`/`BUMP`/`SLIDE_CLR` em `gerar_suporte.py`
e rode `pip install manifold3d trimesh numpy && python3 gerar_suporte.py`.
Para outro gabinete, mude `CASE_W` e `CASE_D`.
