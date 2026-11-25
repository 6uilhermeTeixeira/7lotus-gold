# Arquitetura

```text
6lotus -- revisão --> 5lotus -- composição --> 4lotus -- bundle --> 3lotus
                                                            |
                                                            v
                                                     2lotus (eventos)
```

O 3lotus decide localmente a partir de um bundle validado. Falhas de rede não
transferem a decisão para outro serviço. Eventos operacionais usam uma outbox
SQLite e chegam ao 2lotus de forma idempotente.

## Fronteiras

- 7lotus não é dependência de runtime.
- 1lotus é o gateway local.
- 3lotus contém somente execução, controles locais e coleta necessária à decisão.
- 2lotus não produz decisão de trading.
- 4lotus não recebe chamadas da VPS no caminho crítico.
- 5lotus contém somente estratégias individuais aprovadas.
- 6lotus não possui autorização operacional.

O bundle unificado permanece em shadow até o 3lotus implementar e validar
explicitamente a política de roteamento e risco da composição.

O projeto irmão `../../../7lotus-institucional` publica conteúdo estático e não acessa bancos ou APIs internas.
