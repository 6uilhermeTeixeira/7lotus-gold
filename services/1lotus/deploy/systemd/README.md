# Unidades locais

Estes arquivos são cópias sem credenciais da configuração local. As unidades
base `lotus-local-1.service` a `lotus-local-7.service` permanecem em
`~/.config/systemd/user/`, pois podem conter variáveis privadas. Os arquivos
em `overrides/` configuram sockets Unix para os serviços internos.

Antes de instalar em outro ambiente, ajuste os caminhos absolutos e o UID nos
arquivos. Não inclua senhas, tokens ou `.env` neste diretório. O serviço da
interface usa `127.0.0.1:7771`; os serviços 2–7 usam sockets em `/run/user/1001/`.

Após instalar ou alterar unidades, execute `systemctl --user daemon-reload` e
verifique `gold-lotus.target` e as sete unidades.
