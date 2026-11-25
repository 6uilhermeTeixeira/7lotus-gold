# Piloto local de Graphify em 5lotus

**Data:** 2026-11-19
**Escopo:** extração local de código em `5lotus`, sem skill, hooks ou MCP persistentes.

## Execução

Foi usado `uvx` do ambiente `.tools-venv` já existente, com saída fora dos repositórios:

```bash
cd 5lotus
../.tools-venv/bin/uvx --from graphifyy graphify extract . \
  --code-only --no-cluster --out /tmp/gold-lotus-graphify-pilot
```

O Graphify construiu um grafo com **2.919 nós e 8.625 arestas** a partir de **230 arquivos de
código**. `python-service/data/` e `market-data-pipeline/src/lotus/data/` foram ignorados. O código
AST foi processado localmente sem chamada de LLM.

## Resultado prático

- Uma busca ampla por registro/roteamento/testes devolveu 463 nós candidatos e truncou a resposta.
- Uma busca ancorada em `strategy_definition()` e filtrada por chamadas ainda encontrou 65 nós.
- `explain StrategyDefinition` identificou a definição em
  `python-service/app/strategies/registry.py`, mas listou apenas duas conexões diretas. Busca textual
  simples encontra a definição, roteadores e teste de contrato com menor custo de configuração.
- 67 migrations SQL ficaram sem extração porque `tree_sitter_sql` não está instalado. Isso limita
  perguntas sobre esquema, histórico e relações Supabase.
- O benchmark embutido estimou redução de 120,3x em perguntas genéricas contra o corpus inteiro.
  Esse resultado sintético não mede tokens reais das tarefas Lotus nem comprova melhoria; não use
  como economia projetada.

## Decisão

**Não instalar integração Graphify sempre ativa ainda.** O grafo pode ajudar em navegação entre
símbolos, mas as consultas avaliadas tiveram excesso de nós e omissão de migrations. Manter a
ferramenta como opção efêmera para perguntas de call graph; reavaliar após uma tarefa real em que
`rg`/leitura manual seja custoso. Para trabalho sobre banco, considerar o extra `sql` e repetir a
avaliação antes de tornar o grafo parte do fluxo normal.

## Reprodução

O pacote está em `/tmp/gold-lotus-graphify-pilot/graphify-out/graph.json` neste ambiente; é
descartável e não é fonte versionada. Consultas usadas:

```bash
../.tools-venv/bin/uvx --from graphifyy graphify query \
  "Where are active strategy profiles registered, routed to decision handlers, and validated by tests?" \
  --graph /tmp/gold-lotus-graphify-pilot/graphify-out/graph.json --budget 1000
../.tools-venv/bin/uvx --from graphifyy graphify benchmark \
  /tmp/gold-lotus-graphify-pilot/graphify-out/graph.json
```
