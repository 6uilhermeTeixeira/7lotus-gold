# Revisão de promoção shadow — ZigZag Scalper V3.1

**Decisão:** incluir no catálogo Promovidas em modo exclusivamente shadow, por solicitação explícita do operador em 2026-11-25. A estratégia continua no catálogo de pesquisa do 6lotus.

## Identidade e proveniência

- ID canônico: `zigzag-scalper-v3-1`; ID legado: `core-zigzag-v7`.
- Perfil: `zigzag_scalper_v7_directional_shadow`, versão `3.1`.
- Implementação e dependências foram fixadas por SHA-256 no perfil versionado.
- Hash do artefato de origem: `ab85161ae59f141d80d9ff2847227b901fa2b40d8fbf3dce3ee028e1dcbe289d`.
- Hash do perfil: `a76ba015cf270b1a1651e75618cc7a5f5e969f898c9f8428b2b57a803c60df18`.
- A entrada não seleciona nem modifica a estratégia ativa do runner. `execution.enabled` permanece `false`.

## Limitação de validação

O replay disponível em `6lotus/python-service/data/backtests/core-zigzag-v7-365.json` está marcado `provisional_shadow`; sua justificativa exige replay independente com sinais, saídas e dimensionamento regenerados. O registro estrutural declara `replay_supported=False`. Por isso, esta decisão promove somente o cadastro para acompanhamento shadow; não afirma que a validação independente foi concluída nem autoriza composição ou execução. Uma revisão posterior deverá substituir esta versão após completar essa validação.
