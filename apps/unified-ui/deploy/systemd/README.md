# Unidades locais

Estes arquivos são cópias sem credenciais da configuração local. As unidades
base `lotus-local-1.service` a `lotus-local-5.service` permanecem em
`~/.config/systemd/user/`, pois podem conter variáveis privadas. Os arquivos
em `overrides/` mudam apenas o transporte HTTP para sockets Unix.

Antes de instalar em outro ambiente, ajuste os caminhos absolutos e o UID nos
arquivos. Não inclua senhas, tokens ou `.env` neste diretório. O serviço da
interface usa `127.0.0.1:7771`; os cinco serviços usam sockets em `/run/user/1001/`.

Após instalar ou alterar unidades, execute `systemctl --user daemon-reload` e
verifique `gold-lotus.target`, as cinco unidades e `gold-lotus-ui.service`.
