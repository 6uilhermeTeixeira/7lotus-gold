# Interface unificada Gold Lotus

A interface local está em **http://127.0.0.1:7771/**. Histórico, Operation Core,
Runner, Estratégias e Pesquisa continuam em `../2lotus` a `7lotus`, com dados e
contratos preservados. Os serviços agora escutam em sockets Unix internos, sem
abrir as antigas portas TCP. A documentação é uma cópia estática gerada pelo MkDocs.

## Operação

O usuário `systemd --user` inicia `gold-lotus.target`, que agrupa
`lotus-local-1.service` a `lotus-local-7.service`.
O antigo `lotus-local-docs.service` foi desligado.
Os modelos de unidade e overrides sem credenciais ficam em [`deploy/systemd/`](deploy/systemd/README.md).

```bash
systemctl --user status lotus-local-1.service
systemctl --user restart lotus-local-1.service
```

Para atualizar a documentação estática após editar `services/7lotus/docs/`:

```bash
cd /home/ai-agent/projects/7lotus-gold/services/7lotus
./.venv/bin/python -m mkdocs build -d ../1lotus/site --clean
```

As telas e APIs internas têm prefixo `/p/history/`, `/p/operations/`,
`/p/runner/`, `/p/strategies/`, `/p/promoted/` e `/p/research/`. Clientes externos que antes
usavam 7772 ou 7773 precisam usar a rota correspondente em 7771. Para o bridge
MT5 do Runner, a URL é `http://127.0.0.1:7771/p/runner/decision`; essa origem
também deve constar na lista Allow WebRequest. A execução continua desativada.

As rotas de UI antigas não são mais expostas em portas independentes. Os arquivos
de páginas dos serviços continuam no código porque fornecem o conteúdo exibido
pela interface unificada; não foram apagados dados, bundles nem APIs.

O site em `site/` é gerado e fica fora do Git. O estado mutável do MT5 e do
Runner fica em `/home/ai-agent/lotus-runtime`; os diretórios dos serviços
apontam para ele por links locais. Dados de backtest e bundles já versionados
continuam nos diretórios responsáveis.
