# Candles Fusion Markets M1 e M5

O `1lotus` importa os candles XAUUSD da conta demo Fusion em releases Parquet
imutáveis e independentes por resolução. Os ponteiros vigentes ficam em
`LOTUS_DATA_ROOT/fusion-candles/m1/releases/CURRENT` e
`LOTUS_DATA_ROOT/fusion-candles/m5/releases/CURRENT`. As telas leem esses
releases publicados; não acessam diretamente o terminal MT5.

Na publicação verificada em 2026-11-21, o M1 tinha **1.776.825 candles** de
2021-11-16 23:29:00 a 2026-11-20 23:27:00. O M5 tinha **355.684 candles** de
2021-11-15 23:00:00 a 2026-11-19 22:50:00. Esses horários são do servidor
`FusionMarkets-Demo` e não são convertidos implicitamente para UTC. Os números
na interface são lidos dos manifestos atuais, portanto podem aumentar com
novos releases.

Os exportadores MQL5 são `mt5/FusionM1CandleHistoryExporter.mq5` e
`mt5/FusionCandleHistoryExporter.mq5`. O importador valida o CSV `.ready.csv`,
preserva a origem por SHA-256, gera o Parquet, registra manifesto e hash e só
então atualiza o ponteiro `CURRENT` da resolução correspondente.

No painel local da porta 7771, **Histórico → Fusion** permite consultar M1/M5.
**Estratégias → Catálogo e replay** mostra a cobertura M1 e abre
**Estratégias → Fusion M1** para visualizar o preço publicado; isso não troca
o dataset dos backtests ou bundles. **Pesquisa → Estratégias** abre Fusion M1
por padrão e, quando há snapshot, mostra o resultado do estudo ZigZag em modo
shadow. O seletor de fonte também oferece Dukascopy com as curvas de retorno
das estratégias. Os resultados históricos Dukascopy não são sobrepostos aos
candles Fusion.
