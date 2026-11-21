# Fusion M1 na Pesquisa

O painel Pesquisa lê releases Parquet imutáveis publicados pelo 1lotus em
`LOTUS_FUSION_CANDLES_ROOT`. O serviço local configura esta raiz como
`/home/ai-agent/lotus-data/fusion-candles`. M1 e M5 têm ponteiros `CURRENT`
independentes. O loader valida o manifesto e o comando de replay também valida
o SHA-256 do Parquet antes de gerar resultados.

No gráfico de Pesquisa, selecione **Fusion MT5**. A fonte mantém os timestamps
na hora do servidor da corretora (`broker_server_time`). O valor numérico do
eixo é apenas uma codificação para posicionar as barras; não converte o horário
para UTC. Resultados de estratégias Dukascopy não são sobrepostos à fonte Fusion.
O gráfico mostra até 5.000 candles recentes do período selecionado; escolha
**Até (servidor Fusion)** para navegar por datas anteriores.
O seletor de ano na mesma tela abre o snapshot ZigZag M1 correspondente.

## Estudo ZigZag M1

O estudo `zigzag-scalper-m1` é exclusivamente de pesquisa. Ele usa pivôs M30
confirmados por dois candles completos de cada lado, identifica rompimento no
fechamento M30 e entra no primeiro candle M1 do período seguinte. Mantém stop
de 240 pontos, alvo de 1.000 pontos e horizonte de até dez minutos. Usa o
spread gravado no M1, slippage de dois pontos e comissão de US$ 4,50 por lote.
Se stop e alvo forem alcançados no mesmo M1, o stop prevalece. Não aplica
filtro de sessão UTC enquanto não houver mapeamento validado do relógio do broker.

Gere ou atualize um ano por vez, fora de requisições web:

```bash
python-service/.venv/bin/python python-service/scripts/cache_fusion_m1_zigzag.py --year 2026
```

Os snapshots ficam em `lotus-data/research/fusion-m1/<versão>/`, separados dos
backtests operacionais. Registram versão do release, hash do CSV de origem,
parâmetros, fingerprint do código e trades. Cada ano tem um ponteiro `CURRENT`
para o snapshot vigente sem sobrescrever versões anteriores. A API de leitura é
`GET /api/research/fusion-m1/zigzag?year=2026`; a cobertura M1/M5 fica em
`GET /api/research/fusion/status`. São dados exploratórios e não promovem um
perfil para execução.
