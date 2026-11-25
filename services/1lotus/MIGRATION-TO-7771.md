# Migração para a porta 7771

## Estado em 20/11/2026

- A interface unificada escuta em `127.0.0.1:7771`.
- Ela encaminha telas e APIs para os cinco serviços por sockets Unix internos.
  Esses serviços são geridos por unidades `systemd --user`.
- A documentação foi gerada em `apps/unified-ui/site/` e é servida pela interface.
- `1lotus` contém o histórico/documentação; `2lotus` contém dados e telemetria;
  `3lotus` contém o runner; `4lotus` contém bundles; `5lotus` contém pesquisa.
- O Runner respondeu `execution_enabled: false` na checagem local.

## Migração realizada

1. Serviços migrados para sockets Unix; documentação gerada estaticamente.
2. Interface iniciada na 7771; antigas portas TCP 7772–7777 desligadas.
3. Rotas das seis áreas e APIs principais verificadas via porta 7771.
4. Qualquer cliente MT5 configurado para 7772 ou 7773 ainda exige atualização
   manual de URL e da lista Allow WebRequest; não havia conta conectada ao runner
   na verificação da migração.
5. As pastas e páginas de conteúdo dos serviços foram preservadas em `services/`.
   Somente as interfaces em portas separadas deixaram de ser expostas.
