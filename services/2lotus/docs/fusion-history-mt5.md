# Coletor MT5 de candles Fusion

## Estado deste host

- Container `gold-lotus-fusion-history-mt5` criado e ativo, com política `unless-stopped`.
- noVNC responde em `127.0.0.1:6081`; porta limitada ao loopback da VM.
- Downloads do instalador MT5 e WebView2 já estão no volume persistente.
- O prefixo Wine de 64 bits foi reparado e o instalador da Fusion Markets concluiu a instalação.
- O MT5 abriu, autenticou a conta demo no servidor informado e salvou a sessão no perfil Wine.
- Os arquivos temporários de texto usados no login foram removidos após a confirmação no diário.
- Histórico XAUUSD/M5 exportado da conta demo Fusion e publicado no `1lotus`: 355.684 candles,
  de 2021-11-15 23:00:00 a 2026-11-19 22:50:00 (hora do servidor). O release ativo é
  `f03adc6712a69a4e`. A disponibilidade anterior a 2021-11-15 depende do servidor da corretora.

## Fronteiras

- Este terminal é um runtime independente em `2lotus/.runtime/fusion-history-mt5/`.
- Ele serve somente para histórico Fusion Markets. Não compartilha prefixo Wine, perfil, arquivos
  de conta nem instalação do MT5 operacional.
- O terminal fica em Wine/Docker, com noVNC em `127.0.0.1:6081`; VNC não fica publicado na rede.
- O código do exportador continua em `1lotus/mt5/FusionCandleHistoryExporter.mq5`.
- CSVs de origem, releases Parquet e manifestos ficam em `$HOME/lotus-data/fusion-candles/`;
  `1lotus` lê esse mesmo diretório via `LOTUS_DATA_ROOT`.
- O terminal não carrega EA de trading. O exportador chama `CopyRates` e grava candles fechados.

## Preparar o terminal

Inicie o runtime com:

```bash
cd /home/ai-agent/projects/7lotus-gold/services/2lotus
./scripts/run-fusion-history-mt5.sh start
```

Abra `http://127.0.0.1:6081/vnc.html?host=127.0.0.1&port=6081` na VM e conclua a instalação
assistida do MT5, se necessário. No terminal, conecte manualmente à conta **Demo** da Fusion
Markets e confirme o servidor/símbolo exatos. Não grave senha em arquivos do projeto.

Para abrir o noVNC no navegador de outro computador, crie um túnel SSH naquele computador:

```bash
ssh -L 6081:127.0.0.1:6081 ai-agent@IP_DA_VM
```

No MT5, use **Arquivo > Login na Conta de Negociação** (ou **File > Login to Trade Account**).
Preencha **Login**, **Senha** e **Servidor** com os dados da conta demo enviados pela Fusion
Markets. Escolha o servidor demo exato informado pela corretora. As credenciais são digitadas na
janela do MT5 pelo noVNC; este projeto não usa um arquivo de senhas para o coletor.

Copie e compile o exportador no MetaEditor do terminal:

```bash
./scripts/install-fusion-history-exporter.sh
```

No MT5, abra `FusionCandleHistoryExporter` como Script e ajuste `CaptureSymbol` caso a corretora
use sufixo no símbolo XAUUSD. O script recusa servidores cujo nome não contenha `Fusion`, exclui
a vela em formação e não contém funções de negociação. Aguarde a sincronização do histórico antes
da primeira exportação; a quantidade disponível depende do servidor da corretora e do limite de
barras configurado no terminal.

## Importar e publicar no 1lotus

Quando o Script terminar e criar o arquivo `.ready.csv`, publique-o com o nome exato do servidor
MT5 da conta demo:

```bash
./scripts/import-fusion-candles.sh FusionMarkets-Demo XAUUSD
```

O importador arquiva uma cópia do CSV por SHA-256 em `$HOME/lotus-data/fusion-candles/source/`,
valida OHLC, ordem e volumes, gera um Parquet versionado e atualiza `releases/CURRENT`. O painel
de histórico do `1lotus` lê o release publicado. A base do release preserva hora do servidor da
corretora; não presume UTC.

O runtime pode ser parado e iniciado sem apagar prefixo Wine, CSVs ou releases:

```bash
./scripts/run-fusion-history-mt5.sh stop
./scripts/run-fusion-history-mt5.sh start
```

O container usa `restart: unless-stopped` e volta com o Docker no boot. O usuário ainda precisa
abrir o terminal e autenticar a conta demo pela interface MT5; nenhuma credencial é automatizada.
