# Áreas do projeto

As seis áreas deste projeto estão em um único repositório Git na raiz. A interface fica em `apps/unified-ui/`;
os serviços ficam em `services/1lotus/` a `services/5lotus/`. Esta tabela descreve o ownership atual; nomes de deploy e
serviços em execução podem divergir e devem ser verificados no ambiente de implantação.

| Área | Responsabilidade atual | Entradas principais | Origem histórica |
|---|---|---|---|
| `unified-ui` | Interface única, navegação, gateway local e modelos de implantação; sem dados de mercado próprios. | `app.py`, `assets/`, `deploy/systemd/` | novo |
| `1lotus` | Histórico de mercado, documentação do ecossistema e painel de leitura; fora do caminho de decisão. | `history_app.py`, `fusion_candles.py`, `docs/` | novo |
| `2lotus` | Eventos operacionais, telemetria e auditoria do runner; mantém compatibilidade com APIs legadas. | `python-service/app/`, `api/`, `mt5/` | `lotus-runner` |
| `3lotus` | Runner Windows/MT5 que avalia localmente bundles validados e envia telemetria. | `lotus_runner/`, `mt5/` | `2lotus-live-core` |
| `4lotus` | Fonte das estratégias promovidas e geração de bundles versionados. | `lotus_app/`, `scripts/build_bundle.py` | importação inicial do projeto local Lotus |
| `5lotus` | Pesquisa XAUUSD/M5, replay shadow, portal e pipeline de dados histórico. | `python-service/`, `market-data-pipeline/` | `2Lotus` |

O site institucional é um projeto irmão em `../../../7lotus-institucional`, servido localmente na porta
`7778`. Ele não integra o painel nem o caminho operacional do `7lotus-gold`.

## Painel unificado local

A interface em `127.0.0.1:7771` mantém o único menu local: Histórico
`/historico`, Operation Core `/operacao`, Runner `/runner`, Estratégias
`/estrategias`, Pesquisa `/pesquisa` e Documentação `/documentacao`.
Os cinco serviços continuam independentes e se conectam por sockets Unix internos;
a documentação é servida de uma cópia estática. APIs, dados e autenticação
continuam com o repositório dono. As antigas portas locais 7772–7777 não são
usadas pela interface atual.

## Fluxo de promoção e operação

```text
5lotus pesquisa --revisão--> 4lotus bundle imutável --> 3lotus decisão local
                                                            |
                                                            v
                                                2lotus eventos/auditoria
```

`1lotus` documenta e consulta histórico, sem ser dependência de runtime. As fronteiras e garantias
estão em [`architecture.md`](architecture.md). Os contratos executáveis ficam com seus produtores.

## Divergências operacionais conhecidas

- `2lotus` ainda contém endpoints e texto compatíveis com o antigo fluxo de decisão. A arquitetura
  alvo deixa a avaliação local no `3lotus`; confirme o deploy antes de descrever o estado ativo.
- Os READMEs de `2lotus` e `5lotus` mencionam hospedagem provisória do Live Core/conta demo. Isso é
  estado de deploy, não altera o ownership pretendido nesta tabela.
- `5lotus/README.md` deve usar esta tabela como referência para os nomes e fronteiras dos Lotus.

## Navegação Codex

Ownership por tarefa e estrutura do diff packet: [`CODEX-NAVIGATION-GUIDE.md`](CODEX-NAVIGATION-GUIDE.md).
