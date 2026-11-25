# Guia de navegação Codex — Gold Lotus

Use [`repositories.md`](repositories.md) como mapa canônico do workspace e
[`architecture.md`](architecture.md) para o fluxo alvo e as fronteiras.

## Navegação

1. Identifique a área dona antes de abrir módulos de outros Lotus.
2. Confira `git status --short` na raiz e preserve alterações locais já existentes.
3. Leia o README, contrato/arquitetura e testes da área dona; verifique código se houver drift.
4. Para mudanças entre áreas, confirme produtor e consumidor do bundle, API, evento ou dado.
5. Leia credenciais apenas por canais explicitamente necessários; nunca as copie para mapas, índice
   ou handoff.

## Pacote de revisão (diff packet)

Prepare um packet por área com objetivo, ownership, arquivos/superfícies alteradas, contrato
afetado, consumidores verificados, testes/inspeções executados, limitações e estado dos arquivos antes/depois.
Separe alterações locais preexistentes. Identifique explicitamente se uma afirmação descreve
arquitetura alvo ou implantação ativa. Resultados de backtest não autorizam promoção ou execução.
