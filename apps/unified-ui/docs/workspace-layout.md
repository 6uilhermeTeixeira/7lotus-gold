# Organização do workspace

`7lotus-gold/` é o repositório Git conjunto. A interface em
`apps/unified-ui/` e os serviços em `services/1lotus/` a `services/5lotus/`
são versionados juntos. O site institucional fica fora deste workspace.

| Local | Tipo | Regra |
|---|---|---|
| `apps/unified-ui/` | Código da interface e modelos de deploy | Versionar na raiz. |
| `apps/unified-ui/site/` | Site MkDocs gerado | Ignorar no Git; regenerar a partir de `services/1lotus/docs/`. |
| `services/1lotus/` a `services/5lotus/` | Código, contratos, backtests e bundles | Versionar na raiz, respeitando os arquivos ignorados de cada serviço. |
| `/home/ai-agent/lotus-data/` | Dados de mercado compartilhados | Estado externo ao código. |
| `/home/ai-agent/lotus-runtime/operations/` | Ambiente MT5 e arquivos de execução do exportador | Acessado pelo link `services/2lotus/.runtime`. |
| `/home/ai-agent/lotus-runtime/runner/` | Banco e logs do Runner | Acessados pelos links `services/3lotus/data` e `services/3lotus/logs`. |
| `/run/user/1001/gold-lotus-*.sock` | Sockets HTTP internos | Temporários; as unidades `systemd --user` os recriam. |

As unidades instaladas estão em `~/.config/systemd/user/`. Os modelos sem
credenciais ficam em `apps/unified-ui/deploy/systemd/`; arquivos de configuração
privados permanecem fora do workspace versionável. O portal é o único serviço TCP do
projeto, em `127.0.0.1:7771`.

Antes de mover qualquer pasta novamente, confirme as referências de
`WorkingDirectory` e `ExecStart` das unidades, os links de estado e o caminho
entre `4lotus` e os backtests de `5lotus`. Depois valide as seis áreas e as APIs
pela porta 7771.
