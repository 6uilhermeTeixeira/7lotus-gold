# Handoff de contexto — Gold Lotus

**Atualização 2026-11-25:** o `1lotus` agora contém a interface/gateway em
`127.0.0.1:7771`; o antigo `1lotus` de histórico e documentação foi movido para
`7lotus`. O laboratório anterior em `5lotus` foi movido para `6lotus`, e o
novo `5lotus` contém o catálogo de estratégias independentes promovidas.
O mapa canônico está em `services/7lotus/docs/repositories.md`. As sete unidades
locais estão ativas. Há alterações locais não commitadas de toda a migração;
preserve-as. O restante deste arquivo inclui contexto anterior à reorganização.

**Atualizado:** 2026-11-21.

## Contexto para retomar

- O agrupamento reúne a gateway em `services/1lotus/` e seis serviços em
  `services/`; o mapa canônico está em
  [`services/7lotus/docs/repositories.md`](../services/7lotus/docs/repositories.md).
- O fluxo alvo é pesquisa em `5lotus`, revisão/bundle em `4lotus`, runner local em `3lotus`, eventos
  em `2lotus`; `7lotus` mantém contexto/histórico. O site público está no projeto irmão `../../7lotus-institucional`.
- A realidade operacional e alguns READMEs não coincidem completamente com esse alvo. Verifique
  repo, deployment e flags no escopo da tarefa; não conclua que há execução real autorizada.
- A correção da seção de fronteiras em `services/5lotus/README.md` aponta para o mapa canônico.
- Os seis históricos Git separados foram removidos em 2026-11-21, preservando os arquivos de
  trabalho. O Git conjunto foi iniciado na raiz; `origin` aponta para o
  repositório público `6uilhermeTeixeira/7lotus-gold`. Preserve as alterações locais.

## Próxima ação útil

Escolher uma área dona e uma pergunta/tarefa concreta. Ler as instruções e documentos
canônicos daquele dono, depois verificar código e testes. Para mudanças de estratégia, começar no
registro do `5lotus` e respeitar a revisão/bundle em `4lotus` antes do runner.

Este handoff não contém segredos, estado de conta ou resultados de serviço não verificados.
