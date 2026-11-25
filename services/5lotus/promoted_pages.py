"""Read-only presentation of approved independent strategies."""

from __future__ import annotations

import html
from fastapi.responses import HTMLResponse


def escape(value: object) -> str:
    return html.escape(str(value), quote=True)


STYLE = """
:root{color-scheme:dark;--bg:#07090d;--surface:#0f141c;--raised:#151c26;--line:#283242;--text:#edf2f7;--muted:#9ba9ba;--green:#43d398;--gold:#48d7a0;--panel:var(--surface);--panel2:var(--raised);--border:var(--line);--yellow:var(--gold);--lotus-content-max:1360px;--lotus-font-family:Inter,ui-sans-serif,system-ui,sans-serif}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 Inter,ui-sans-serif,system-ui,sans-serif}
a{color:var(--green);text-decoration:none}a:hover{text-decoration:underline}a:focus-visible{outline:2px solid var(--green);outline-offset:3px}
main{max-width:1360px;margin:auto;padding:28px}h1,h2,h3,p{margin-top:0}.muted{color:var(--muted)}.eyebrow{color:var(--gold);font-size:11px;font-weight:800;letter-spacing:.1em;text-transform:uppercase}
.header{display:flex;justify-content:space-between;align-items:start;gap:18px;margin-bottom:24px}.header h1{font-size:32px;line-height:1.15;margin:4px 0 8px}.header p{max-width:670px;margin:0}.header-links{display:flex;flex-wrap:wrap;gap:10px}
.header-actions{display:flex;gap:16px;align-items:center;flex-wrap:wrap}.header-actions a{color:var(--text)}
.button{display:inline-flex;align-items:center;min-height:40px;padding:9px 14px;border:1px solid var(--line);border-radius:8px;background:var(--raised);color:var(--text);font-weight:700}.button:hover{border-color:var(--green);text-decoration:none}.button.primary{background:var(--green);border-color:var(--green);color:#072218}
.stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin-bottom:20px}.stat,.panel,.strategy-card{background:var(--surface);border:1px solid var(--line);border-radius:10px}.card{background:var(--raised);border:1px solid var(--line);border-radius:8px}.stat{padding:18px}.stat span,.stat strong{display:block}.stat span{color:var(--muted);font-size:12px}.stat strong{font-size:28px;margin-top:8px}
.layout{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(290px,.8fr);gap:18px}.panel{padding:22px;margin-bottom:18px}.panel h2{font-size:20px}.chart-placeholder{min-height:210px;display:grid;place-items:center;border:1px dashed #334153;border-radius:8px;background:linear-gradient(180deg,#111b23,#0d131b);color:var(--muted);text-align:center;padding:22px}.chart-placeholder strong{display:block;color:var(--text);font-size:17px;margin-bottom:6px}
.section-head{display:flex;justify-content:space-between;align-items:end;gap:12px;margin:28px 0 14px}.section-head h2{margin:0}.cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.strategy-card{padding:20px}.card-top{display:flex;align-items:start;justify-content:space-between;gap:12px}.strategy-card h3{font-size:19px;margin:4px 0 8px}.badge{display:inline-flex;border-radius:999px;border:1px solid #2c654f;background:#112d24;color:#86e0b4;padding:4px 9px;font-size:11px;font-weight:800}.meta{display:flex;flex-wrap:wrap;gap:7px;margin:15px 0}.meta span{border:1px solid var(--line);border-radius:6px;color:var(--muted);padding:4px 7px;font-size:12px}.validation-note{padding:10px 12px;border:1px solid #2c6b55;border-radius:7px;background:#153128;color:#c8ffe7;font-size:12px}.details{display:grid;grid-template-columns:100px 1fr;gap:6px 12px;font-size:13px}.details dt{color:var(--muted)}.details dd{margin:0;overflow-wrap:anywhere}
.equity-panel{padding:20px;margin-bottom:28px;overflow:hidden}.equity-heading{display:flex;align-items:flex-start;justify-content:space-between;gap:18px}.equity-heading h2{margin-bottom:6px}.equity-heading p{margin-bottom:0}.history-actions{display:flex;flex-direction:column;align-items:flex-end;gap:8px}.history-actions p{margin:0;text-align:right}.history-actions button{padding:9px 13px;border:1px solid var(--green);border-radius:7px;color:var(--green);background:transparent;font-weight:800}.chart-toolbar{display:flex;align-items:center;flex-wrap:wrap;gap:10px;margin-top:16px}.chart-toolbar button,.chart-toolbar select{min-height:36px;padding:7px 9px;color:var(--text);background:#080b10;border:1px solid #303744;border-radius:7px;font:inherit}.chart-toolbar button{font-weight:750}.chart-toolbar button.selected{background:#29244a;border-color:#51468b}.chart-toolbar label{display:grid;gap:4px;color:var(--muted);font-size:12px}.chart-toolbar :disabled{opacity:.55}.chart-options{display:flex;align-items:center;gap:4px;padding:4px;border:1px solid #303744;border-radius:7px;background:#080b10}.chart-options button{min-height:32px;padding:5px 9px;border:0;background:transparent;color:var(--muted);font-weight:700}.chart-options button.selected{background:#29244a;border-radius:5px;color:var(--text)}.chart-toolbar .fit-button{margin-left:auto;color:var(--muted);background:transparent}.promotion-chart-placeholder{height:540px;margin-top:10px;display:grid;place-items:center;border:1px solid rgba(148,163,184,.12);border-radius:8px;background:#0b0f16;color:var(--muted);text-align:center;padding:24px}.promotion-chart-placeholder strong{display:block;color:var(--text);font-size:17px;margin-bottom:6px}.chart-help{margin:8px 0 0;font-size:11px}
.family-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px;align-items:start}.strategy-family{min-width:0}.family-heading{min-height:220px;padding:18px;border:1px solid var(--line);border-bottom:0;border-radius:10px 10px 0 0;background:var(--raised)}.family-heading h2{margin:0 0 9px;font-size:20px}.family-heading>p:last-of-type{margin-bottom:0;font-size:13px;line-height:1.45}.family-chart-actions{display:flex;flex-wrap:nowrap;gap:6px;margin-top:13px}.family-chart-actions button{flex:0 0 108px;width:108px;height:32px;padding:0 6px;border:1px solid rgba(148,163,184,.35);border-radius:6px;color:var(--muted);background:#090c12;font-size:11px;font-weight:700;white-space:nowrap}.family-chart-actions button:disabled{cursor:not-allowed;opacity:.35}.variant-stack{display:flex;flex-direction:column;gap:12px;padding:12px;border:1px solid var(--line);border-radius:0 0 10px 10px;background:rgba(255,255,255,.025)}.strategy-card-row{display:flex;flex-direction:column;overflow:hidden}.bot{height:286px;min-height:286px;display:flex;flex-direction:column;align-items:stretch;padding:18px 18px 12px;color:var(--text);text-decoration:none}.bot h3,.bot p{margin-bottom:0}.card-meta{width:100%;display:flex;justify-content:space-between;gap:8px;align-items:center}.variant-label{color:var(--gold);font-size:11px;font-weight:800;letter-spacing:.04em;text-transform:uppercase}.status-badge{padding:4px 8px;border:1px solid #555;border-radius:999px;color:var(--muted);font-size:11px;font-weight:800;text-transform:uppercase;letter-spacing:.05em}.status-badge.active{color:var(--green);border-color:rgba(65,211,146,.45)}.market{margin:11px 0 8px;font-size:12px}.strategy-title-block{min-height:45px;margin-bottom:10px}.bot h3{margin:0;font-size:17px;line-height:1.25}.strategy-subtitle{margin:3px 0 0;color:var(--gold);font-size:12px;font-weight:800;line-height:1.25;letter-spacing:.025em}.strategy-summary{display:-webkit-box;overflow:hidden;margin:0;font-size:13px;line-height:1.45;-webkit-box-orient:vertical;-webkit-line-clamp:4}.results-link{display:block;width:100%;margin-top:auto;padding-top:12px;border-top:1px solid rgba(148,163,184,.16);color:var(--green)}.strategy-card-toggle{display:flex;align-items:center;justify-content:center;gap:8px;margin:0 12px 12px;padding:9px 12px;border:1px solid rgba(148,163,184,.28);border-radius:7px;color:var(--muted);background:#0c1017;font-size:11px;font-weight:700}.strategy-card-toggle-label{line-height:1.2}.strategy-card-swatch{width:11px;height:11px;border-radius:50%;background:var(--green)}.family-empty{min-height:112px;display:grid;place-items:center;padding:18px;border:1px dashed rgba(166,166,166,.35);border-radius:8px;text-align:center}.family-empty p{margin:0}.promotion-details{margin:0 12px 12px}.promotion-details[hidden]{display:none}
.chart-options{display:flex;align-items:center;gap:4px;padding:4px;border:1px solid #303744;border-radius:7px;background:#080b10}.chart-options button{min-height:32px;padding:5px 9px;border:0;background:transparent;color:var(--muted);font-weight:700}.chart-options button.selected{background:#29244a;border-radius:5px;color:var(--text)}.chart-toolbar .fit-button{margin-left:auto;color:var(--muted);background:transparent}.chart-help{margin:8px 0 0;font-size:11px}.strategy-card-row .bot{flex:0 0 286px;min-height:286px;padding:17px 16px 10px}.bot:hover{text-decoration:none}.strategy-card-toggle:focus-visible{outline:2px solid var(--green);outline-offset:2px}
.comparison-toolbar{display:flex;justify-content:space-between;align-items:center;gap:18px;padding:18px;margin-bottom:18px}.comparison-toolbar p{margin:0}.period-buttons,.family-actions{display:flex;flex-wrap:wrap;gap:7px}.period-buttons button,.family-actions button,.simulator-controls button{padding:8px 12px;border:1px solid #2a3547;border-radius:7px;color:var(--muted);background:#0b1017;font-weight:700}.period-buttons button.selected{color:#07110d;border-color:var(--green);background:var(--green)}.summary-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin-bottom:18px}.summary-grid .panel{padding:18px;margin:0}.summary-grid strong{display:block;font-size:24px}.table-panel{padding:0;overflow:hidden}.table-panel table{min-width:980px}.table-panel td a{color:var(--text);font-weight:700}.table-panel td small{display:block;margin-top:5px;color:var(--muted)}.comparison-note{margin:18px 2px 0}.simulator-controls,.simulator-selector,.simulator-chart,.simulator-warning{padding:20px;margin-bottom:18px}.simulator-controls form{display:flex;flex-wrap:wrap;gap:14px;align-items:end}.simulator-controls label{display:grid;gap:6px;color:var(--muted);font-size:12px}.simulator-controls input,.simulator-controls select{padding:10px;min-height:40px;color:var(--text);background:var(--bg);border:1px solid var(--line);border-radius:7px}.simulator-controls button.primary{color:var(--green);background:#112d24;border-color:#2c654f}.strategy-choice-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin-top:14px}.strategy-choice{display:flex;align-items:center;gap:8px;padding:10px;border:1px solid var(--line);border-radius:7px;background:#10151d;color:var(--muted);font-size:12px}.strategy-choice input{accent-color:var(--green)}.simulator-chart-heading{display:flex;justify-content:space-between;gap:12px}.simulator-chart svg{display:block;width:100%;min-height:360px;margin-top:14px;border:1px solid rgba(148,163,184,.12);border-radius:8px;background:#0b0f16}.simulator-warning{border-left:3px solid var(--gold)}@media(max-width:760px){.strategy-choice-grid,.summary-grid{grid-template-columns:1fr}.comparison-toolbar,.simulator-chart-heading{align-items:flex-start;flex-direction:column}}
.promotion-equity-chart{height:540px;margin-top:10px;border:1px solid rgba(148,163,184,.12);border-radius:8px;overflow:hidden;background:#0b0f16}.promotion-equity-legend{min-height:42px;display:flex;align-items:center;flex-wrap:wrap;gap:9px 16px;padding:10px 2px 0;border-top:1px solid rgba(255,255,255,.14)}.promotion-equity-legend .legend-item{display:inline-flex;align-items:center;gap:7px;color:var(--muted);font-size:12px}.promotion-equity-legend .legend-item i{width:18px;height:3px;border-radius:999px}.promotion-equity-legend .ohlc,.promotion-equity-legend time{color:var(--text);font-size:12px}.promotion-equity-legend strong{color:var(--text)}.promotion-chart-status{max-width:430px;font-size:11px;line-height:1.35;text-align:right}@media(max-width:720px){.promotion-equity-chart{height:460px}}
.empty{padding:36px;text-align:center}.empty h2{margin-bottom:8px}.table-wrap{overflow:auto}table{border-collapse:collapse;width:100%;min-width:680px}th,td{text-align:left;padding:14px;border-bottom:1px solid var(--line);vertical-align:top}th{color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.07em}td code{color:#a8debb}input{background:var(--raised);border:1px solid var(--line);border-radius:7px;color:var(--text);min-height:40px;padding:8px 10px}input:disabled{opacity:.55}.form-row{display:flex;flex-wrap:wrap;gap:12px;margin:20px 0}.form-row label{display:grid;gap:6px;color:var(--muted);font-size:12px}
@media(max-width:1040px){.family-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:900px){.layout{grid-template-columns:1fr}.cards{grid-template-columns:1fr}}@media(max-width:720px){.family-grid{grid-template-columns:1fr}.family-heading{min-height:auto}.equity-heading{flex-direction:column}.history-actions{align-items:flex-start}.history-actions p{text-align:left}}@media(max-width:640px){main{padding:22px 16px}.header{display:block}.header h1{font-size:26px}.header-links{margin-top:16px}.stats{grid-template-columns:1fr}.stat strong{font-size:23px}}
"""


def page(title: str, body: str) -> HTMLResponse:
    return HTMLResponse(
        '<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>{escape(title)} · 5lotus</title><style>{STYLE}</style></head><body>'
        f'<main>{body}</main></body></html>'
    )


def header(title: str, description: str) -> str:
    return (
        '<header class="header"><div><p class="eyebrow">5lotus · catálogo aprovado</p>'
        f'<h1>{escape(title)}</h1><p class="muted">{escape(description)}</p></div>'
        '<div class="header-links"><a class="button" href="/strategies">Estratégias</a>'
        '<a class="button" href="/compare">Comparar</a>'
        '<a class="button" href="/growth-simulator">Simulador</a></div></header>'
    )


def catalog_page(items: list[tuple[dict, dict]]) -> HTMLResponse:
    families = (
        ("zigzag", "Scalp", "Operações rápidas de rompimento, confirmação de regime e contexto de ticks."),
        ("stochastic", "Sell", "Operações de venda baseadas em pullback, sobrecompra e confirmação baixista."),
        ("multitimeframe", "Buy", "Operações de compra alinhadas entre H1, M15 e M5."),
        ("combined", "Combined", "Portfólios que combinam famílias, pesos e regras de conflito."),
    )
    grouped = {family_id: [] for family_id, _, _ in families}
    family_by_profile = {
        "zigzag-scalper": "zigzag",
        "stochastic-sell": "stochastic",
        "breakout-short": "stochastic",
        "mean-reversion-sell": "stochastic",
        "multitimeframe-trend": "multitimeframe",
        "buy-trend-pullback-breakout": "multitimeframe",
        "buy-trend-dip-stochastic": "multitimeframe",
        "combined-portfolio": "combined",
    }
    for record, profile in items:
        family_id = family_by_profile.get(profile.get("family"), "combined")
        grouped[family_id].append((record, profile))

    columns = []
    for family_id, title, description in families:
        entries = grouped[family_id]
        cards = "".join(_strategy_card(record, profile) for record, profile in entries)
        if not cards:
            cards = '<div class="family-empty"><p class="muted">Nenhuma estratégia promovida.</p></div>'
        columns.append(
            f'<article class="strategy-family" data-family="{family_id}"><header class="family-heading">'
            f'<p class="eyebrow">{len(entries)} {"estratégia" if len(entries) == 1 else "estratégias"}</p>'
            f'<h2>{escape(title)}</h2><p class="muted">{escape(description)}</p>'
            f'<div class="family-chart-actions"><button type="button" data-family-toggle="{family_id}" disabled>Ativar categoria</button>'
            f'<button type="button" data-family-only="{family_id}" disabled>Somente esta</button></div></header>'
            f'<div class="variant-stack">{cards}</div></article>'
        )
    family_grid = "".join(columns)
    body = (
        '<section class="panel equity-panel"><div class="equity-heading"><div><p class="eyebrow">Mercado e backtest</p>'
        '<h2>XAU/USD com desempenho das estratégias</h2><p class="muted">Candles no painel superior · PnL acumulado no painel inferior</p></div>'
        '<div class="history-actions"><button id="promotion-refresh" type="button">Recarregar histórico</button>'
        '<p id="promotion-chart-status" class="muted promotion-chart-status" aria-live="polite">Carregando gráfico...</p></div></div>'
        '<div class="chart-toolbar"><button type="button" class="selected" disabled>1% Risk/Trade</button>'
        '<label>Fonte <select disabled><option>Fusion MT5</option></select></label>'
        '<div class="chart-options" aria-label="Duração dos candles"><button data-promotion-resolution="1m">1m</button><button data-promotion-resolution="5m">5m</button><button data-promotion-resolution="1h">1h</button><button data-promotion-resolution="1d" class="selected">1d</button></div>'
        '<div class="chart-options" aria-label="Período exibido"><button data-promotion-days="7">7D</button><button data-promotion-days="30">30D</button><button data-promotion-days="90">90D</button><button data-promotion-days="365" class="selected">1A</button><button data-promotion-days="1095">3A</button></div>'
        '<button id="promotion-fit" class="fit-button" type="button">Ajustar</button></div>'
        '<div id="promotion-equity-chart" class="promotion-equity-chart" role="img" aria-label="Histórico do XAU/USD e backtest de pesquisa"></div>'
        '<div id="promotion-equity-legend" class="promotion-equity-legend"></div>'
        '<p class="chart-help muted">Candles Fusion MT5 acima; replay de pesquisa abaixo, ainda pendente de revisão independente.</p></section>'
        f'<section class="family-grid" aria-label="Famílias de estratégias promovidas">{family_grid}</section>'
        '<script src="../research/static/security.js"></script>'
        '<script src="../research/static/vendor/lightweight-charts/lightweight-charts.standalone.production.js"></script>'
        '<script src="../research/static/equity-chart.js?v=8"></script>'
        '<script>const promotionChart=LotusEquityChart.create(document.getElementById("promotion-equity-chart"),document.getElementById("promotion-equity-legend"));'
        'const promotedIds=new Set([...document.querySelectorAll(".strategy-card-row")].map(card=>card.id.replace(/^promotion-/,"")));'
        'let promotionDays=365,promotionResolution="1d";async function loadPromotionChart(){const status=document.getElementById("promotion-chart-status");status.textContent="Carregando gráfico...";'
        'try{const url=new URL("../research/api/backtest-market-chart",location.href);url.search=new URLSearchParams({symbol:"XAUUSD",source:"fusion",resolution:promotionResolution,days:String(promotionDays),mode:"normalized"});'
        'const response=await fetch(url);if(!response.ok)throw Error("Não foi possível carregar o histórico e os backtests.");const data=await response.json();data.series=(data.series||[]).filter(item=>promotedIds.has(item.bot_id));'
        'promotionChart.setData(data,{visibleBotIds:promotedIds});status.textContent=data.candles.length+" candles Fusion · "+(data.series.length?data.series.length+" curvas de pesquisa":"sem replay para as promovidas neste período")+" · período "+promotionDays+" dias";'
        '}catch(error){status.textContent=error.message;}}'
        'document.querySelectorAll("[data-promotion-days]").forEach(button=>button.onclick=()=>{document.querySelectorAll("[data-promotion-days]").forEach(item=>item.classList.remove("selected"));button.classList.add("selected");promotionDays=Number(button.dataset.promotionDays);loadPromotionChart();});'
        'document.querySelectorAll("[data-promotion-resolution]").forEach(button=>button.onclick=()=>{document.querySelectorAll("[data-promotion-resolution]").forEach(item=>item.classList.remove("selected"));button.classList.add("selected");promotionResolution=button.dataset.promotionResolution;loadPromotionChart();});'
        'document.getElementById("promotion-refresh").onclick=loadPromotionChart;document.getElementById("promotion-fit").onclick=()=>promotionChart.fitContent();loadPromotionChart();</script>'
        '<script>document.addEventListener("click",event=>{const button=event.target.closest("[data-promotion-toggle]");if(!button)return;const details=document.getElementById(button.dataset.promotionToggle);const expanded=button.getAttribute("aria-expanded")==="true";button.setAttribute("aria-expanded",String(!expanded));button.querySelector(".strategy-card-toggle-label").textContent=expanded?"Ver validação":"Ocultar validação";details.hidden=expanded;});</script>'
    )
    return page("Estratégias promovidas", body)


def _strategy_card(record: dict, profile: dict) -> str:
    validation = profile.get("validation", {})
    card_id = f"promotion-{record['id']}"
    return (
        f'<div class="strategy-card-row card" id="{escape(card_id)}">'
        f'<a class="bot" href="results/{escape(record["id"])}">'
        f'<div class="card-meta"><span class="variant-label">Estratégia</span>'
        '<span class="status-badge active">Promovida</span></div>'
        f'<p class="market muted">{escape(profile.get("parameters", {}).get("symbol", "XAUUSD"))} · '
        f'{escape(profile.get("parameters", {}).get("timeframe", "M5"))}</p>'
        f'<div class="strategy-title-block"><h3>{escape(profile.get("name", record["id"]))}</h3>'
        f'<p class="strategy-subtitle">{escape(profile.get("subtitle", "Versão promovida"))}</p></div>'
        f'<p class="strategy-summary muted">{escape(profile.get("description", "Estratégia individual promovida no 5lotus."))}</p>'
        '<strong class="results-link">Ver resultados →</strong></a>'
        f'<button class="strategy-card-toggle" type="button" data-promotion-toggle="{escape(card_id)}-details" aria-expanded="false">'
        '<span class="strategy-card-swatch" aria-hidden="true"></span><span class="strategy-card-toggle-label">Ver validação</span></button>'
        f'<div class="promotion-details" id="{escape(card_id)}-details" hidden>'
        f'<p class="validation-note">{escape(validation.get("note", "Validação pendente."))}</p>'
        f'<dl class="details"><dt>Origem</dt><dd>{escape(record["source_ref"])}</dd>'
        f'<dt>Revisão</dt><dd>{escape(record["review_ref"])}</dd>'
        f'<dt>Elegível no 4lotus</dt><dd>{"Sim" if record.get("composition_eligible", True) else "Não, validação pendente"}</dd></dl></div></div>'
    )


def results_page(record: dict, profile: dict) -> HTMLResponse:
    validation = profile.get("validation", {})
    body = (
        f'<header class="header"><div><p class="eyebrow">Estratégia promovida</p>'
        f'<h1>{escape(profile.get("name", record["id"]))}</h1>'
        f'<p class="muted">{escape(profile.get("subtitle", ""))}</p></div>'
        '<a href="../strategies">Voltar às promovidas</a></header>'
        '<section class="summary-grid"><article class="panel"><p class="muted">Mercado</p>'
        f'<strong>{escape(profile.get("parameters", {}).get("symbol", "—"))} · '
        f'{escape(profile.get("parameters", {}).get("timeframe", "—"))}</strong></article>'
        f'<article class="panel"><p class="muted">Versão</p><strong>{escape(record["version"])}</strong></article>'
        '<article class="panel"><p class="muted">Resultados revisados</p><strong>Indisponíveis</strong></article></section>'
        '<section class="panel"><p class="eyebrow">Resultados</p><h2>Replay independente pendente</h2>'
        '<p class="muted">Métricas, operações e curva de desempenho aparecerão após a revisão do histórico desta estratégia.</p>'
        f'<p class="validation-note">{escape(validation.get("note", "Validação pendente."))}</p></section>'
    )
    return page(f'{profile.get("name", record["id"])} · Resultados', body)


def comparison_page(items: list[tuple[dict, dict]]) -> HTMLResponse:
    rows = ''.join(
        f'<tr><td><strong>{escape(profile.get("name", record["id"]))}</strong>'
        f'<small>{escape(profile.get("subtitle", ""))}</small></td>'
        f'<td>{escape(profile.get("parameters", {}).get("symbol", "—"))} · '
        f'{escape(profile.get("parameters", {}).get("timeframe", "—"))}</td>'
        '<td>—</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td><td>—</td>'
        '<td>Replay pendente</td></tr>'
        for record, profile in items
    ) or '<tr><td colspan="10" class="muted">Nenhuma estratégia promovida para comparar.</td></tr>'
    body = (
        '<section class="comparison-toolbar panel"><div><p class="eyebrow">Período analisado</p>'
        '<div class="period-buttons" role="group" aria-label="Período da comparação">'
        '<button type="button" disabled>90 dias</button><button type="button" class="selected" disabled>1 ano</button>'
        '<button type="button" disabled>3 anos</button></div></div>'
        '<p class="muted">Aguardando snapshots revisados para comparação.</p></section>'
        f'<section class="summary-grid"><article class="panel"><p class="muted">Estratégias promovidas</p><strong>{len(items)}</strong></article>'
        '<article class="panel"><p class="muted">Mercado acompanhado</p><strong>XAUUSD · M5</strong></article>'
        '<article class="panel"><p class="muted">Risco comparável</p><strong class="muted">Aguardando replay</strong></article></section>'
        '<section class="panel table-panel"><div class="table-wrap"><table><thead><tr><th>Estratégia</th>'
        '<th>Mercado</th><th>Fechados</th><th>Abertos</th><th>Win rate</th><th>Profit factor</th>'
        '<th>Expectativa (R)</th><th>Drawdown (R)</th><th>PnL líquido</th><th>Último evento</th></tr></thead>'
        f'<tbody>{rows}</tbody></table></div></section>'
        '<p class="muted comparison-note">Os indicadores aparecerão após a revisão dos snapshots de cada estratégia promovida.</p>'
    )
    return page('Comparar estratégias', body)


def simulator_page(items: list[tuple[dict, dict]]) -> HTMLResponse:
    family_by_profile = {
        'zigzag-scalper': 'zigzag', 'stochastic-sell': 'stochastic',
        'breakout-short': 'stochastic', 'mean-reversion-sell': 'stochastic',
        'multitimeframe-trend': 'multitimeframe',
        'buy-trend-pullback-breakout': 'multitimeframe',
        'buy-trend-dip-stochastic': 'multitimeframe',
        'combined-portfolio': 'combined',
    }
    choices = ''.join(
        f'<label class="strategy-choice" data-family="{family_by_profile.get(profile.get("family"), "combined")}">'
        f'<input type="checkbox" disabled><span>{escape(profile.get("name", record["id"]))}</span></label>'
        for record, profile in items
    ) or '<p class="muted">Nenhuma estratégia promovida.</p>'
    body = (
        '<section class="panel simulator-controls"><form><label>Capital inicial (USD)'
        '<input type="number" value="10000" disabled></label><label>Risco por operação (%)'
        '<input type="number" value="1" disabled></label><label>Período<select disabled>'
        '<option>30 dias</option><option>90 dias</option><option selected>1 ano</option></select></label>'
        '<button class="primary" type="button" disabled>Simular</button></form></section>'
        '<section class="panel simulator-selector"><div class="family-actions">'
        '<button disabled>Scalp</button><button disabled>Sell</button><button disabled>Buy</button>'
        '<button disabled>Combined</button><button disabled>Limpar</button></div>'
        f'<div class="strategy-choice-grid">{choices}</div></section>'
        '<section class="panel simulator-chart"><div class="simulator-chart-heading">'
        '<div><h2>Curvas de crescimento</h2><p class="muted">Cada linha reaplica a sequência real de resultados em R.</p></div>'
        '<p class="muted">Aguardando snapshots revisados</p></div>'
        '<svg viewBox="0 0 1100 460" role="img" aria-label="Sem curva de crescimento disponível">'
        '<text x="550" y="230" text-anchor="middle" fill="#9ba9ba">Sem histórico revisado para simular</text></svg></section>'
        '<section class="panel simulator-warning"><strong>Simulação histórica</strong>'
        '<p class="muted">Não prevê resultados futuros. Riscos maiores amplificam drawdown, exposição e efeito composto.</p></section>'
    )
    return page('Simulador de crescimento', body)
