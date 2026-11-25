# 7lotus-gold

Workspace local para histórico de XAUUSD, pesquisa e replay de estratégias, promoção de bundles, acompanhamento operacional e runner MT5. A interface única fica em `http://127.0.0.1:7771/`. O primeiro versionamento conjunto foi `v0.1.0`.

O sistema inicia em modo de pesquisa/shadow. O runner rejeita execução em conta real e exige guardas separados no Python e no EA para qualquer teste em demo. Resultado de backtest não promove uma estratégia nem autoriza ordens.

## Arquitetura

| Área | Responsabilidade | Entrada principal |
|---|---|---|
| [`services/1lotus`](services/1lotus/README.md) | Interface unificada e gateway local | `app.py` |
| [`services/7lotus`](services/7lotus/README.md) | Histórico de mercado e documentação | `history_app.py` |
| [`services/2lotus`](services/2lotus/README.md) | Eventos, telemetria, auditoria e APIs de compatibilidade | `python-service/app/main.py` |
| [`services/3lotus`](services/3lotus/README.md) | Runner de decisão local e ponte MT5 | `lotus_runner/main.py` |
| [`services/4lotus`](services/4lotus/README.md) | Estratégia unificada e bundle de composição | `lotus_app/main.py` |
| [`services/5lotus`](services/5lotus/README.md) | Estratégias individuais promovidas e bundles | `promoted_app.py` |
| [`services/6lotus`](services/6lotus/README.md) | Pesquisa, backtests e pipeline histórico | `python-service/app/main.py` |

O fluxo alvo é **pesquisa `6lotus` → estratégias promovidas `5lotus` → composição `4lotus` → runner `3lotus` → eventos `2lotus`**. O `7lotus` fornece histórico e documentação, sem participar da decisão. O [mapa de ownership](services/7lotus/docs/repositories.md) e a [arquitetura](services/7lotus/docs/architecture.md) descrevem as fronteiras. Os serviços HTTP locais usam sockets Unix; somente o gateway abre a porta `7771` em loopback. O bridge MT5 na VPS usa o runner Windows descrito em `services/3lotus/`.

## Pré-requisitos

- Python 3.12, `uv` e um ambiente Linux com `systemd --user` para a instalação local existente. A interface usa apenas a biblioteca padrão do Python.
- MetaTrader 5 e MetaEditor em Windows para compilar e executar o EA de coleta/bridge; o painel local abre sem o terminal.
- Dados de mercado em `LOTUS_DATA_ROOT` para histórico completo. Sem os releases, o histórico mostra o estado ausente. Supabase e credenciais são necessários apenas para os recursos que dependem deles.

## Configuração

1. Leia [`.env.example`](.env.example) para as variáveis compartilhadas e os exemplos em `services/2lotus/.env.example`, `services/3lotus/.env.example` e `services/6lotus/.env.example` para cada serviço.
2. Crie os `.env` **somente** nos diretórios dos serviços que vai usar e preencha os valores locais. O exemplo da raiz é uma referência; as unidades `systemd` e o runner não o carregam automaticamente. O exemplo do runner contém um caminho Windows; não o copie sem ajustar `LOTUS_RUNNER_HOME` ao sistema onde ele roda.
3. Mantenha `LOTUS_RUNNER_EXECUTION_ENABLED=false`, `DAYTRADE_ENABLE_LIVE_DECISIONS=false` e `LIVE_CANARY_ARMED=false` durante pesquisa e validação. Não coloque chaves, contas, bancos locais ou logs no Git.
4. Para o histórico, aponte `LOTUS_DATA_ROOT` para o diretório externo de releases (neste host, `/home/ai-agent/lotus-data`). Estado mutável do runner e do MT5 fica fora do repositório, em `/home/ai-agent/lotus-runtime`.

## Rodar o painel local

No host já preparado com as unidades, inicie e confira o conjunto:

```bash
systemctl --user start gold-lotus.target
systemctl --user status gold-lotus.target lotus-local-{1,2,3,4,5,6,7}.service
```

Abra `http://127.0.0.1:7771/`. As seções são `/historico`, `/operacao`, `/runner`, `/estrategias`, `/promovidas`, `/pesquisa` e `/documentacao`. Os modelos de instalação e os cuidados com caminhos absolutos estão em [`services/1lotus/deploy/systemd/`](services/1lotus/deploy/systemd/README.md).

Para desenvolver sem as unidades, instale as dependências com `uv sync` em `services/7lotus`, `services/4lotus`, `services/2lotus/python-service` e `services/6lotus/python-service`. Execute cada linha abaixo em um terminal separado, a partir da raiz do projeto e com as variáveis do serviço já configuradas. Os comandos usam os ambientes virtuais locais criados pelo `uv`. O diretório `/run/user/$(id -u)` precisa existir:

```bash
cd services/7lotus && .venv/bin/python -m uvicorn history_app:app --uds "/run/user/$(id -u)/gold-lotus-history.sock"
cd services/2lotus/python-service && .venv/bin/python -m uvicorn app.main:app --uds "/run/user/$(id -u)/gold-lotus-operations.sock"
cd services/3lotus && LOTUS_RUNNER_SOCKET="/run/user/$(id -u)/gold-lotus-runner.sock" python3.12 -m lotus_runner.main
cd services/5lotus && .venv/bin/python -m uvicorn promoted_app:app --uds "/run/user/$(id -u)/gold-lotus-promoted.sock"
cd services/4lotus && .venv/bin/python -m uvicorn lotus_app.main:app --uds "/run/user/$(id -u)/gold-lotus-strategies.sock"
cd services/6lotus/python-service && .venv/bin/python -m uvicorn app.main:app --uds "/run/user/$(id -u)/gold-lotus-research.sock"
cd services/1lotus && python3 app.py
```

Sem as dependências externas configuradas, algumas seções podem mostrar diagnóstico de indisponibilidade. Gere a documentação estática depois de alterar `services/7lotus/docs/`:

```bash
cd services/7lotus
.venv/bin/python -m mkdocs build -d ../1lotus/site --clean
```

## Rodar o bot em shadow

No Windows, instale o `3lotus` conforme seu [guia](services/3lotus/README.md), valide `py -m lotus_runner.main --check` e compile `mt5/LotusRunnerBridge.mq5` no MetaEditor. Use o preset `LotusRunnerBridge-shadow.set`, mantenha `EnableOrderExecution=false` e autorize somente a URL local do runner no WebRequest do MT5. O runner avalia o bundle local e armazena contexto e auditoria em SQLite; a telemetria para `2lotus` usa uma outbox. Testes de execução demo têm um procedimento separado em `services/3lotus/docs/demo-execution.md`.

## Dados e primeiro commit

Os JSON de catálogo e snapshots de backtest usados pelo painel permanecem no código. CSVs grandes de pesquisa, Parquet/BI5, bancos, logs, ambientes virtuais, documentação gerada e segredos são ignorados pelo [`.gitignore`](.gitignore). Alguns scripts de pesquisa exigem dados externos ou resultados intermediários em `services/6lotus/python-service/data/research/`; consulte os caminhos de entrada de cada script antes de reproduzi-los.

Antes de `git add`, revise `git status --short --untracked-files=all` e a seleção com `git diff --cached --stat`. A criação do repositório Git local não publica código nem habilita ordens.

O diagnóstico e as verificações desta preparação estão em [`docs/REVIEW-v0.1.0.md`](docs/REVIEW-v0.1.0.md).
