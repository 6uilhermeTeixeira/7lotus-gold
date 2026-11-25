# Áreas do projeto

As sete áreas deste projeto estão em um único repositório Git na raiz. Os serviços ficam em `services/1lotus/` a `services/7lotus/`. Esta tabela descreve o ownership atual; nomes de deploy e
serviços em execução podem divergir e devem ser verificados no ambiente de implantação.

| Área | Responsabilidade atual | Entradas principais | Origem histórica |
|---|---|---|---|
| `1lotus` | Interface única, navegação e gateway local. | `app.py`, `assets/`, `deploy/systemd/` | antigo `unified-ui` |
| `2lotus` | Eventos operacionais, telemetria e auditoria do runner; mantém compatibilidade com APIs legadas. | `python-service/app/`, `api/`, `mt5/` | `lotus-runner` |
| `3lotus` | Runner Windows/MT5 que avalia localmente bundles validados e envia telemetria. | `lotus_runner/`, `mt5/` | `2lotus-live-core` |
| `4lotus` | Composição da estratégia unificada e geração de bundle versionado. | `lotus_app/`, `scripts/build_unified_bundle.py` | importação inicial do projeto local Lotus |
| `5lotus` | Estratégias individuais promovidas, com revisão e bundles versionados. | `promoted_app.py`, `catalog/`, `profiles/` | novo |
| `6lotus` | Pesquisa XAUUSD/M5, replay shadow, portal e pipeline histórico. | `python-service/`, `market-data-pipeline/` | antigo `5lotus` |
| `7lotus` | Histórico de mercado, documentação e painel de leitura. | `history_app.py`, `fusion_candles.py`, `docs/` | antigo `1lotus` |

O site institucional é um projeto irmão em `../../../7lotus-institucional`, servido localmente na porta
`7770`. Ele não integra o painel nem o caminho operacional do `7lotus-gold`.

## Painel unificado local

A interface em `127.0.0.1:7771` mantém o único menu local: Histórico
`/historico`, Operation Core `/operacao`, Runner `/runner`, Estratégias
`/estrategias`, Promovidas `/promovidas`, Pesquisa `/pesquisa` e Documentação `/documentacao`.
Os serviços de histórico e operação continuam independentes e se conectam por sockets Unix internos;
a documentação é servida de uma cópia estática. APIs, dados e autenticação
continuam com o repositório dono. As antigas portas locais 7772–7777 não são
usadas pela interface atual.

## Fluxo de promoção e operação

```text
6lotus pesquisa --revisão--> 5lotus estratégias individuais
                                  | composição revisada
                                  v
                         4lotus bundle unificado --> 3lotus decisão local
                                                            |
                                                            v
                                                2lotus eventos/auditoria
```

`7lotus` documenta e consulta histórico, sem ser dependência de runtime. As fronteiras e garantias
estão em [`architecture.md`](architecture.md). Os contratos executáveis ficam com seus produtores.

## Divergências operacionais conhecidas

- `2lotus` ainda contém endpoints e texto compatíveis com o antigo fluxo de decisão. A arquitetura
  alvo deixa a avaliação local no `3lotus`; confirme o deploy antes de descrever o estado ativo.
- Os READMEs de `2lotus` e `6lotus` mencionam hospedagem provisória do Live Core/conta demo. Isso é
  estado de deploy, não altera o ownership pretendido nesta tabela.
- O laboratório em `6lotus` conserva documentação histórica com o nome anterior; confirme o contrato vigente antes de operar.

## Navegação Codex

Ownership por tarefa e estrutura do diff packet: [`CODEX-NAVIGATION-GUIDE.md`](CODEX-NAVIGATION-GUIDE.md).
