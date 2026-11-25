# 5lotus — estratégias promovidas

Catálogo de estratégias **independentes** aprovadas após pesquisa no 6lotus.
Cada registro em `catalog/` fixa `id`, `version`, `profile_sha256`,
`source_ref` do 6lotus e `review_ref` da aprovação. O 4lotus pode compor somente entradas deste
catálogo. A promoção é manual: copiar resultados do laboratório não cria uma
entrada aprovada.

O serviço de leitura responde em socket local `gold-lotus-promoted.sock` e é
exposto no painel `/promovidas`. Ele oferece Estratégias, Comparar estratégias
e Simulador de crescimento. As telas usam apenas registros aprovados; gráficos
e simulações aguardam snapshots revisados. O builder valida todos os registros e
gera um ZIP com manifesto e perfis individuais:

```bash
python3 -m uvicorn promoted_app:app --uds "$XDG_RUNTIME_DIR/gold-lotus-promoted.sock"
python3 scripts/build_bundle.py --output dist/5lotus-strategies.zip
```

O catálogo inicia vazio. As estratégias ZigZag hoje presentes no 4lotus não
foram promovidas automaticamente: faltam registros de revisão individual no
novo contrato. O ZIP não altera a seleção ativa do runner.
