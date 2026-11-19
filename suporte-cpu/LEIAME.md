# Suporte de CPU estilo "offset" (pernas em Z frisadas)

Feito para o **Dell Pro Max Tower T2 (FCT2250)**, com base de 187,7 x 438 mm.
Duas pernas laterais com perfil em Z espelhadas (cada pé abre para um lado), frisos,
cantos arredondados e **borda** em volta: lateral, frente e trás. Veja `render_*.png`.

- Altura: 55 mm até onde o gabinete apoia + borda de 14 mm.
- Medidas totais: 278 x 455 mm (os pés saem 37 mm para fora de cada lado). Vão aberto de 54 mm no meio para a fonte puxar ar.
- **Ajuste de largura:** as duas pernas são soltas uma da outra. Coloque o gabinete e encoste
  as pernas nele: a borda lateral de cada perna segura o gabinete na medida exata.
- Frente e trás: borda com 1 mm de folga para os 438 mm do Dell.

## Imprimir
Cada perna tem 3 pedaços, unidos por chaves "gravata-borboleta" encaixadas de cima para baixo.

| Arquivo | Qtd |
|---|---|
| perna_esq_frente.stl, perna_esq_meio.stl, perna_esq_tras.stl | 1 de cada |
| perna_dir_frente.stl, perna_dir_meio.stl, perna_dir_tras.stl | 1 de cada |
| chave_prateleira.stl | 4 |
| chave_pe.stl | 4 |

Cada pedaço tem 112 x 69 x 152 mm, cabe numa mesa 220 x 220 e já vem em pé, com o perfil na mesa,
sem suporte. Sugestão: PLA/PETG branco fosco, 4 paredes, 15–20% gyroid, camada 0,2 mm.

Quer as duas pernas no mesmo sentido? Mude `ESPELHADO = False`.
Para mudar medidas, edite `gerar_suporte_z.py` e rode
`pip install manifold3d trimesh numpy && python3 gerar_suporte_z.py`.
(As versões anteriores, moldura com batentes de clique, estão no histórico do git.)
