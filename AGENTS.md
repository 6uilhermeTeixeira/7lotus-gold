# Mapa de trabalho Gold Lotus

Este diretório contém a interface em `apps/unified-ui` e cinco serviços em
`services/1lotus`–`services/5lotus`. Os históricos Git separados foram removidos;
o repositório conjunto está na raiz. Leia [`docs/CODEX-NAVIGATION-GUIDE.md`](docs/CODEX-NAVIGATION-GUIDE.md)
e [`docs/PROJECT-MAP.md`](docs/PROJECT-MAP.md) antes de escolher o dono de uma mudança.
O site institucional fica no repositório irmão `../7lotus-institucional`, fora deste painel.

- Confira `git status --short` na raiz antes de editar e preserve mudanças locais existentes.
- `docs/WORKSPACE-STATUS.md` registra fronteiras e divergências documentais, não substitui código.
- Use `docs/SESSION-HANDOFF.md` como ponto de retomada e revalide as afirmações com o repo atual.
- Leia arquitetura/contratos do repositório dono antes de alterar API, dados ou execução.
- Estratégias pesquisadas, promovidas e executadas pertencem a fases/áreas distintas. Não pule
  promoção/revisão nem habilite execução real a partir de resultados de pesquisa.
- Nunca coloque credenciais, `.env`, payloads privados ou dados de conta em documentação ou índice.
- Não execute testes por padrão; rode verificações focadas quando solicitadas.
