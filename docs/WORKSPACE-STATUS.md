# Estado do workspace Gold Lotus

**Inventário inicial:** 2026-11-19. **Layout atualizado:** 2026-11-21. Reconfirme antes de cada tarefa; estado de serviços e arquivos
muda com frequência.

- Os seis históricos Git separados foram removidos: interface em `apps/unified-ui/` e cinco
  serviços em `services/1lotus/`–`services/5lotus/`. O Git conjunto foi iniciado na raiz.
  O remoto `origin` aponta para o repositório público
  `6uilhermeTeixeira/7lotus-gold`.
  O site institucional é o repositório irmão `7lotus-institucional/`.
- O alvo local `gold-lotus.target` inicia a interface na porta 7771 e os cinco
  serviços por sockets Unix. A documentação é gerada estaticamente na interface.
  O site tem a unit independente `7lotus-institucional.service` na porta `7778`.
- O mapa e a orientação compartilhados ficam em `services/1lotus/docs/` e são
  versionados junto com a raiz. Este inventário e o handoff permanecem no workspace.
- Na inspeção anterior à remoção do Git havia alterações locais não commitadas em `1lotus` a `5lotus`.
  Na mudança de layout, o antigo `6lotus` também continha alterações locais e foi movido para
  `7lotus-institucional`. Esse registro não identifica o autor nem declara essas mudanças descartáveis. Consulte
  preserve-as; o histórico Git anterior deixou de estar disponível após a remoção dos metadados.
- A documentação do `5lotus` descreve a pesquisa como shadow e afirma que o serviço atual hospeda
  provisoriamente um Live Core/conta demo; o estado-alvo separa o serviço dedicado. Verifique deploy,
  flags e configuração vigentes antes de qualquer conclusão operacional.
- A arquitetura alvo separa pesquisa (`5lotus`), promoção (`4lotus`), runner (`3lotus`) e eventos
  (`2lotus`). Alguns READMEs divergem; use o mapa e confirme em código/configuração/deploy.
- Este inventário não executou testes, não verificou serviços remotos e não inspecionou credenciais.

## Fontes canônicas por função

| Papel | Fonte recomendada |
|---|---|
| Constituição do agente | `../AGENTS.md` e instruções locais de cada repositório |
| Mapa/ownership | `services/1lotus/docs/repositories.md` + `services/1lotus/docs/architecture.md` |
| Estado | Este arquivo + `docs/current-state.md` do repo dono, revalidado contra runtime/código |
| Histórico técnico | ADRs e decisões específicas; os históricos Git separados foram removidos |
