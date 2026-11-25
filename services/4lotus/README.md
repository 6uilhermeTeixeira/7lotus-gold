# 4lotus

Fonte da estratégia unificada Lotus: compõe estratégias individuais aprovadas
no 5lotus por meio de gatilhos, filtros de contexto, filtros temporais e roteadores.
O serviço de inspeção usa `127.0.0.1:7774` e
nunca participa do caminho crítico de decisão da VPS.

Abra `/` para o painel unificado: histórico, catálogo e replay, comparação e simulador
ficam em uma página. As rotas de cada seção permanecem acessíveis diretamente.

```bash
uv sync
uv run uvicorn lotus_app.main:app --host 127.0.0.1 --port 7774
uv run python scripts/build_bundle.py --output dist/4lotus-strategies.zip
```

Os arquivos atuais em `bundles/` são perfis individuais legados. O novo builder
`scripts/build_unified_bundle.py` exige perfis aprovados no 5lotus e produz um
artefato de composição com dependências e hashes fixos. Ele aceita apenas a
política `shadow_only` e `execution_enabled=false` até que o contrato de
roteamento e risco seja implementado e validado no 3lotus. Nenhuma composição
foi promovida automaticamente.
