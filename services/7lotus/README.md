# 7lotus

Histórico de ticks XAUUSD e documentação do ecossistema Lotus.

No workspace local atual, o histórico aparece na interface unificada em
`http://127.0.0.1:7771/historico`. É uma aplicação de leitura
independente: mostra o estado da coleta, a cobertura anual e amostras de candles
e ticks dos releases publicados. Não participa do caminho de decisão ou execução.

```bash
cd services/7lotus
uv sync
LOTUS_DATA_ROOT=/caminho/do/lotus-data uv run uvicorn history_app:app --host 127.0.0.1 --port 7791
```

O armazenamento esperado contém `manifests/dukascopy.sqlite3` e
`releases/CURRENT`, com partições Parquet versionadas. Sem esse diretório o painel
mostra o diagnóstico de ausência, sem inventar dados. A coleta e a publicação
continuam no pipeline do `6lotus/market-data-pipeline`; o painel não grava no dataset.

## Candles Fusion Markets

O exportador independente [mt5/FusionCandleHistoryExporter.mq5](mt5/FusionCandleHistoryExporter.mq5)
consulta somente candles M5 fechados via `CopyRates` no terminal MT5 conectado à
Fusion. Compile no MetaEditor e execute no gráfico do símbolo XAUUSD da conta
Fusion. O símbolo pode ter sufixo: ajuste `CaptureSymbol` e registre o nome exato
na importação. O terminal precisa estar sincronizado; a quantidade exportável
depende do histórico disponibilizado pela corretora e do limite de barras do MT5.

O CSV concluído fica em `Terminal/Common/Files/1lotus-candles/fusion/` com nome
`<símbolo>-M5-candles.ready.csv`. Copie-o para este host e importe:

```bash
LOTUS_DATA_ROOT=/caminho/do/lotus-data uv run python scripts/import_fusion_candles.py \
  /caminho/XAUUSD-M5-candles.ready.csv --server FusionMarkets-Demo --symbol XAUUSD
```

A importação valida OHLC, ordenação e formato, publica um Parquet versionado e
atualiza `fusion-candles/releases/CURRENT`. A página Fusion da interface unificada lê esse
release. Os horários são **horários do servidor da corretora**, sem conversão
implícita para UTC; o exportador e o importador não usam a conta para negociar.

A documentação local é servida em `127.0.0.1:7771/documentacao`. Para prévia
isolada durante edição, use:

```bash
uv sync
uv run mkdocs serve --dev-addr 127.0.0.1:7797
```
