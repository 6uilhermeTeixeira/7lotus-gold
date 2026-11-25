# Gold Lotus

O 7lotus é a fonte canônica para decisões transversais do ecossistema. Código,
segredos, datasets e estado operacional pertencem aos projetos responsáveis.

| Projeto | Responsabilidade | Rota na interface local |
|---|---|---|
| 1lotus | Interface unificada | `/` |
| 7lotus | Histórico de ticks do ouro e documentação | `/historico` |
| Docs | Planejamento e documentação | `/documentacao` |
| 2lotus | Telemetria, auditoria e resultados | `/operacao` |
| 3lotus | Runner da VPS e ponte MT5 | `/runner` |
| 4lotus | Estratégia unificada e bundles | `/estrategias` |
| 5lotus | Estratégias individuais promovidas | `/promovidas` |
| 6lotus | Pesquisa e desenvolvimento | `/pesquisa` |

Todas as rotas acima são servidas em `http://127.0.0.1:7771/`. Os serviços
permanecem independentes e se conectam à interface por sockets locais.

Execução real não é habilitada por esta reorganização.
