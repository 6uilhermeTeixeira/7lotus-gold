# Sistema visual — Gold Lotus

Este documento define a linguagem visual comum dos painéis locais Gold Lotus. Cada Lotus continua
sendo um repositório independente; implemente os mesmos tokens e padrões localmente, sem criar uma
dependência de runtime entre eles.

## Princípios

- Priorize leitura rápida de estado, risco, período e origem dos dados.
- Use superfícies escuras neutras; verde indica estado positivo ou selecionado, amarelo atenção e
  vermelho erro/perda. Não use cor como único indicador.
- Mantenha navegação, cabeçalhos, espaçamento e controles previsíveis entre painéis.
- Dê prioridade a tabelas e gráficos legíveis em telas estreitas, com rolagem explícita quando
  necessário.
- Preserve estados de carregamento, vazio, erro e atualização. Nunca apresente ausência de dados
  como zero ou como estado saudável.
- Painéis são ferramentas locais de operação e pesquisa. O estilo não deve confundir pesquisa,
  shadow, demo e execução real.

## Tokens

Os valores canônicos estão em [`design-tokens.json`](design-tokens.json). Em CSS, use as
propriedades `--lotus-*`; aliases antigos podem permanecer temporariamente para minimizar alterações
em superfícies existentes.

Veja [design-preview.html](design-preview.html) para uma prévia autocontida de cores, tipografia,
navegação, cartões, controles e tabela responsiva.

| Uso | Token |
|---|---|
| Fundo da aplicação | `--lotus-bg` |
| Sidebar | `--lotus-sidebar` |
| Cartão/painel | `--lotus-surface` |
| Superfície elevada | `--lotus-surface-raised` |
| Divisórias e bordas | `--lotus-border` |
| Texto principal/secundário | `--lotus-text`, `--lotus-muted` |
| Estado ativo/positivo | `--lotus-accent` |
| Atenção/erro | `--lotus-warning`, `--lotus-danger` |

## Layout e componentes

- Sidebar desktop: 248 px; cabeçalho superior: 64 px; conteúdo: largura máxima de 1.360 px.
- Use uma escala de espaçamento de 4, 8, 12, 16, 24 e 32 px.
- Use raios de 6 px para controles, 8 px para cartões e 12 px para superfícies maiores.
- Alvos interativos devem ter pelo menos 40 px de altura; navegação principal, 44 px.
- Estados de foco devem ser visíveis por teclado. Respeite `prefers-reduced-motion`.
- Breakpoints comuns: 860 px para navegação móvel e 560 px para layouts compactos.
- Números que mudam (preços, saldos, contagens e horários) devem usar algarismos tabulares.
- Para tabelas densas, mantenha rótulos, unidades, datas e estados legíveis; em telas pequenas,
  prefira rolagem horizontal dentro da tabela a comprimir colunas críticas.

## Aplicação

O shell (sidebar, cabeçalho e navegação móvel) deve compartilhar a mesma geometria e interação.
Conteúdo específico continua pertencendo ao painel responsável: histórico em `1lotus`, operação e
auditoria em `2lotus`, runner em `3lotus`, estratégias em `4lotus` e pesquisa em `5lotus`.

Na revisão visual, compare desktop largo, tablet e celular; confira navegação por teclado, estados
de foco, contraste, tabelas, gráficos, carregamento, vazio e erro. Esta definição não afirma que a
interface já passou por essa revisão visual.
