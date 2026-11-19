# Suporte de monitor com pernas em "Z" frisadas

Duas pernas impressas em 3D + um tampo de madeira (você compra/corta).
O tampo entra nas luvas de cima das pernas, sem parafuso nem cola. Veja `render_*.png`.

## Tampo de madeira
- **18 mm de espessura x 200 mm de profundidade**, comprimento à sua escolha (ex.: 600 mm).
- MDF, pinus ou compensado. Cada ponta entra 70 mm na perna.
- Altura final: 110 mm da mesa até o topo.

## Imprimir
| Arquivo | Qtd |
|---|---|
| perna_esquerda.stl | 1 |
| perna_direita.stl | 1 |

Cada perna: 212 x 110 x 75 mm, cabe numa mesa 220 x 220. Já vem deitada na posição certa
(lateral externa na mesa, luva aberta para cima), sem suporte.
Sugestão: PLA/PETG branco fosco, 4 paredes, 15–20% gyroid, camada 0,2 mm.
Cole pezinhos de borracha embaixo para não riscar a mesa.

Para outra espessura de tampo, altura etc., mude os parâmetros em `gerar_suporte_monitor.py`
e rode `pip install manifold3d trimesh numpy && python3 gerar_suporte_monitor.py`.
