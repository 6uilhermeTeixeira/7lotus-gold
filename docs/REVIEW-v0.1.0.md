# Revisão de preparação — v0.1.0

Atualizado em 2026-11-21. Este documento registra o estado local antes do primeiro commit conjunto. Não descreve uma validação de execução real nem substitui os contratos do código.

## Escopo e decisões

- O Git conjunto está na raiz. Os seis históricos anteriores foram removidos. A separação `apps/unified-ui` e `services/1lotus`–`5lotus` permanece, sem mover módulos neste primeiro corte.
- Nenhuma fórmula de estratégia, parâmetro de backtest ou regra de promoção foi alterada nesta preparação.
- Os JSON de catálogo e snapshots de backtest usados pelo painel continuam candidatos ao versionamento. CSVs de pesquisa, dados Parquet/BI5, logs, bancos e runtime ficam fora pelo `.gitignore`; alguns scripts de reconstrução exigem esses insumos externos.

## Segurança e configuração

- Os exemplos de configuração do `5lotus` tinham 13 campos sensíveis preenchidos; agora estão vazios para preenchimento local. Não foram alterados arquivos `.env` reais.
- A varredura dos 670 arquivos candidatos (aproximadamente 52 MiB) não encontrou assinaturas conhecidas de chave privada, token GitHub, token de API, JWT ou URL com credenciais. Essa busca por padrões não garante ausência de segredos desconhecidos; revisar a seleção final antes do commit.
- O gateway e o runner permanecem restritos a loopback/socket local. A execução de ordens continua desativada por padrão.

## Resiliência e observabilidade

- O runner agora rejeita candles incompletos, OHLC inválido e números não finitos antes de guardá-los em cache; ticks e livro de ofertas também rejeitam números não finitos antes de escrever no SQLite.
- Relatórios de execução enviados ao runner são reduzidos aos campos auditados antes de gravar, encaminhar ou registrar em log. Campos extras do payload não entram nesses destinos.
- O padrão de porta do runner Windows, o EA e o preset shadow foram alinhados à instalação na porta `7772`. O painel Linux continua usando socket Unix através da interface `7771`.
- O `2lotus` e o `5lotus` já tratam timeouts, erros HTTP e limite de requisições no acesso ao Supabase; a outbox do runner preserva eventos quando a telemetria falha. A validação de comportamento sob falha real de rede e MT5 exige ambiente separado.

## Organização pendente

- `2lotus` e `5lotus` contêm cópias idênticas de módulos como `adaptive.py`, `indicators.py`, `local_dataset.py`, `security.py`, `telemetry.py` e `workspace.py`. Consolidar depois de mapear importações, contratos e deploys; a deduplicação não integra o v0.1.0.
- Há documentação histórica em `2lotus` e `5lotus` com nomes e implantação anteriores. Confirmar cada fluxo no runtime antes de usar esses guias para operar contas.
- Não houve TODO/FIXME relevante no código de produção do painel na busca inicial. Isso não substitui um teste de navegação completo.

## Verificação realizada

- `3lotus`: 24 testes passaram com o `pytest` atualizado; Ruff passou nos arquivos Python alterados.
- Antes do primeiro commit, os cinco locks Python e o manifesto do pipeline foram auditados com `pip-audit`. Os achados em ferramentas de teste e pesquisa foram corrigidos por atualizações pontuais de versão e os seis alvos ficaram sem vulnerabilidades conhecidas na nova auditoria. Não há `package.json` de aplicação para `npm audit`.
- O runner Windows/EA MQL5 não foi compilado neste host Linux. Os processos locais ativos não foram reiniciados por esta revisão; o código novo entrará em uso após reinício planejado.
- A tag `v0.1.0` não faz parte desta revisão. Antes de publicar, revisar `git status --short`, os arquivos staged e os controles de segurança aplicáveis.
