# 2Lotus market data pipeline

Pipeline isolado de coleta e publicação do histórico XAUUSD da Dukascopy usado pelo ambiente de pesquisa 2Lotus.

- `src/lotus/ingestion/dukascopy.py`: coletor horário resumível.
- `scripts/publish-dataset.py`: publicação das partições Parquet e do release corrente.
- `scripts/collection-status.py`: diagnóstico do manifesto compartilhado.

Os dados permanecem fora do repositório, no diretório apontado por `LOTUS_DATA_ROOT`.

## Coleta automática nesta VM

O serviço `lotus-dukascopy-download.service` executa a coleta XAUUSD desde
2016-01-01 até ontem em UTC, retomando pelo manifesto e pelos arquivos válidos.
Ele é habilitado no `systemd --user` para iniciar no boot da VM. Nesta máquina,
`LOTUS_DATA_ROOT` aponta para `/home/ai-agent/lotus-data`; ajuste o caminho da
unidade ao instalar em outro host.

A concorrência começa com 4 requisições simultâneas, em janelas de 24 horas, e
reduz à metade quando há pressão alta de retries ou HTTP 503. Pressão menor
reduz um worker; dois blocos limpos aumentam um worker, até o máximo de 8.
Após falhas persistentes, o coletor aguarda antes de abrir a janela seguinte.
Um reinício repete a sequência desde 4, mas as horas concluídas são ignoradas.
Falhas recuperáveis são tentadas novamente; se ainda houver falhas, a unidade
tenta retomar após cinco minutos. O log vai para o journal do usuário:

```bash
systemctl --user status lotus-dukascopy-download.service
journalctl --user -u lotus-dukascopy-download.service -f
```

Para instalar ou atualizar a unidade nesta VM:

```bash
mkdir -p ~/.config/systemd/user
cp deploy/systemd/lotus-dukascopy-download.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable lotus-dukascopy-download.service
```

O `enable` agenda o início no próximo boot da sessão persistente. Use
`systemctl --user start lotus-dukascopy-download.service` para iniciar
manualmente sem reiniciar a VM.
