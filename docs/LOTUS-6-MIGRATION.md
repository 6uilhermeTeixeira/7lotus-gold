# Migração para seis serviços

## Fluxo

`6lotus` pesquisa → revisão → `5lotus` estratégias independentes → revisão
de complementaridade → `4lotus` composição → `3lotus` runner → `2lotus`
eventos. O `7lotus` fornece histórico e documentação; o `1lotus` é o gateway local.

## Estado no repositório

- O laboratório anterior foi movido de `services/5lotus` para `services/6lotus`.
- O novo `5lotus` contém catálogo de leitura e builder para perfis individuais.
  O catálogo começa vazio; cada entrada exige `id`, `version`, `source_ref`, `review_ref`
  e `profile_sha256`, além de um perfil JSON com hash canônico válido.
- O `4lotus` contém um builder de composição com dependências fixadas por hash.
  O formato exige `schema_version: "1.0"`, `id`, `version`, lista de IDs
  `strategies`, `routing_policy: "shadow_only"` e
  `execution_enabled: false`.
- O gateway inclui `/promovidas` e mantém `/pesquisa` para o laboratório.
- Os templates systemd incluem o serviço 6 e redirecionam o serviço 5 ao
  catálogo novo. Instalações existentes não foram modificadas por estes arquivos.

## Para concluir a implantação

1. Registrar a revisão de cada estratégia que será promovida e adicionar
   seu perfil e catálogo no `5lotus`, com versão e hash imutáveis.
2. Definir regras de prioridade, sinais simultâneos, risco compartilhado e
   saída da estratégia unificada. Implementar a política no `4lotus` e seu
   consumidor no `3lotus`; validar em shadow e demo antes de qualquer execução.
3. Ajustar as unidades locais instaladas, variáveis de ambiente e caminhos de
   dados para `6lotus`; criar o ambiente virtual do novo `5lotus`.
4. Verificar os seis sockets e as rotas pela porta `7771`. Não habilitar
   execução real durante a migração.

Os READMEs históricos dentro de `6lotus` podem citar seu nome anterior.
Consulte o mapa canônico em `services/7lotus/docs/repositories.md`.
