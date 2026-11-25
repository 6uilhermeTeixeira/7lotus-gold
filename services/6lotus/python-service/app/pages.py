from html import escape

from fastapi.responses import HTMLResponse

from .schemas import BotCatalogItem
from .strategies.registry import strategy_definition, strategy_presentation_order


STRATEGY_FAMILIES = (
    ("zigzag", "Scalp", "Operações rápidas de rompimento, confirmação de regime e contexto de ticks."),
    ("stochastic", "Sell", "Operações de venda baseadas em pullback, sobrecompra e confirmação baixista."),
    ("multitimeframe", "Buy", "Operações de compra alinhadas entre H1, M15 e M5."),
    ("combined", "Combined", "Portfólios que combinam famílias, pesos e regras de conflito."),
)


def _strategy_family(bot: BotCatalogItem) -> str:
    profile = bot.strategy_profile.lower()
    definition = strategy_definition(profile)
    if definition is not None:
        return {
            "scalp": "zigzag",
            "sell": "stochastic",
            "buy": "multitimeframe",
            "combined": "combined",
        }[definition.family]
    if profile in {"happy_gold_portfolio_100_100", "portfolio_6_7", "portfolio_6_7_100_100"} or "portfolio" in profile:
        return "combined"
    if "zigzag" in profile:
        return "zigzag"
    if "stochastic" in profile or "breakout_short" in profile or "mean_reversion_sell" in profile:
        return "stochastic"
    if "breakout_short" in profile:
        return "stochastic"
    if "mean_reversion_sell" in profile:
        return "stochastic"
    if "buy_trend_pullback" in profile or "buy_trend_dip" in profile:
        return "multitimeframe"
    if "multitimeframe" in profile:
        return "multitimeframe"
    return "combined"


def _variant_label(bot: BotCatalogItem, family: str, position: int) -> str:
    if family == "combined":
        if bot.strategy_profile == "happy_gold_portfolio_100_100":
            return "Composição completa"
        if "portfolio_6_7" in bot.strategy_profile:
            return "Baseline parcial · 2 de 3"
    return "Estratégia-base" if position == 0 else f"Variação {position}"


def _family_order(bot: BotCatalogItem) -> tuple[int, str]:
    definition = strategy_definition(bot.strategy_profile)
    if definition is not None:
        return definition.order, bot.name.casefold()
    return 100, bot.name.casefold()


def _subtitle_html(bot: BotCatalogItem, class_name: str = "strategy-subtitle") -> str:
    return f'<p class="{class_name}">{escape(bot.subtitle)}</p>' if bot.subtitle else ""


NAVIGATION = (
    ("account", "/account", "Conta", "user"),
    ("strategies", "/bots", "Estratégias", "grid"),
    ("simulator", "/growth-simulator", "Simulador de crescimento", "trend"),
    ("comparison", "/compare", "Comparar estratégias", "compare"),
    ("operations", "/operations", "Saúde operacional", "pulse"),
    ("history", "/history", "Histórico do ouro", "database"),
)


def _navigation_icon(name: str) -> str:
    paths = {
        "grid": '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>',
        "database": '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v6c0 1.7 3.6 3 8 3s8-1.3 8-3V5M4 11v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"/>',
        "pulse": '<path d="M3 12h4l2.5-6 4.5 12 2.5-6H21"/>',
        "trend": '<path d="M4 18V6M4 18h16M7 14l4-4 3 2 5-6"/>',
        "compare": '<path d="M7 3v18M17 3v18M3 7l4-4 4 4M13 17l4 4 4-4"/>',
        "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    }
    return f'<svg viewBox="0 0 24 24" aria-hidden="true">{paths[name]}</svg>'


def _page(title: str, body: str, *, active_nav: str | None = "auto") -> HTMLResponse:
    shell_open = shell_close = shell_class = shell_assets = ""
    if active_nav == "auto":
        active_nav = (
            "history" if "Histórico" in title else
            "account" if "Conta" in title else
            "operations" if "Saúde" in title else
            "simulator" if "Simulador" in title else
            "comparison" if "Comparação" in title else
            "strategies"
        )
    if active_nav is not None:
        links = "".join(
            f'<a class="app-nav-link{" active" if item_id == active_nav else ""}" href="{href}"'
            f'{" aria-current=\"page\"" if item_id == active_nav else ""}>'
            f'{_navigation_icon(icon)}<span>{escape(label)}</span></a>'
            for item_id, href, label, icon in NAVIGATION
        )
        current_label = next(label for item_id, _, label, _ in NAVIGATION if item_id == active_nav)
        shell_class = ' class="has-app-shell"'
        shell_assets = '<link rel="stylesheet" href="/static/admin-shell.css?v=7"><script src="/static/admin-shell.js?v=1" defer></script>'
        shell_open = f'''<div class="app-shell"><aside class="app-sidebar" id="app-sidebar" aria-label="Navegação principal"><div class="app-sidebar-brand"><a href="/bots" aria-label="2Lotus — Estratégias"><img src="/static/brand/lotus-icon.png" alt="2Lotus"></a><button class="app-sidebar-close" type="button" data-sidebar-close aria-label="Fechar menu">×</button></div><div class="app-workspace-label"><span>Research workspace</span><strong>Shadow operations</strong></div><nav class="app-nav">{links}</nav><div class="app-sidebar-footer"><span class="app-status-dot" aria-hidden="true"></span><div><strong>Ambiente protegido</strong><small>Execução real desativada</small></div><form method="post" action="/logout"><button class="app-logout" type="submit">Sair</button></form></div></aside><div class="app-sidebar-overlay" data-sidebar-close></div><section class="app-workspace"><div class="app-topbar"><button class="app-menu-button" type="button" data-sidebar-open aria-controls="app-sidebar" aria-expanded="false" aria-label="Abrir menu">{_navigation_icon("grid")}</button><div><span>2Lotus</span><strong>{escape(current_label)}</strong></div><span class="app-topbar-mode">Shadow</span></div><div class="app-content">'''
        shell_close = "</div></section></div>"
    return HTMLResponse(f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><link rel="icon" type="image/png" href="/static/brand/lotus-icon.png"><link rel="apple-touch-icon" href="/static/brand/lotus-icon.png"><title>{escape(title)}</title>{shell_assets}<style>
    :root {{ color-scheme:dark; --lotus-bg:#07090d; --lotus-sidebar:#0a0e14; --lotus-surface:#0f141c; --lotus-surface-raised:#151c26; --lotus-border:#283242; --lotus-text:#edf2f7; --lotus-muted:#9ba9ba; --lotus-accent:#43d398; --lotus-accent-surface:#1b2634; --lotus-warning:#f6c667; --lotus-danger:#ff6b81; --lotus-info:#64b5ff;--lotus-space-1:4px;--lotus-space-2:8px;--lotus-space-3:12px;--lotus-space-4:16px;--lotus-space-6:24px;--lotus-space-8:32px;--lotus-radius-control:6px;--lotus-radius-card:8px;--lotus-radius-surface:12px;--lotus-sidebar-width:248px;--lotus-topbar-height:64px;--lotus-content-max:1360px;--lotus-control-target:40px;--lotus-navigation-target:44px;--lotus-font-family:Inter,ui-sans-serif,system-ui,sans-serif; --bg:var(--lotus-bg); --panel:var(--lotus-surface); --panel2:var(--lotus-surface-raised); --border:var(--lotus-border); --text:var(--lotus-text); --muted:var(--lotus-muted); --green:var(--lotus-accent); --red:var(--lotus-danger); --yellow:var(--lotus-warning); }}
    * {{ box-sizing:border-box; }} :where(a,button,input,select,textarea,[tabindex]):focus-visible {{ outline:2px solid var(--lotus-accent); outline-offset:2px; }} :where(time,output,[data-numeric]) {{ font-variant-numeric:tabular-nums; }} body {{ margin:0; font-family:var(--lotus-font-family); color:var(--text); background:var(--bg); }} main {{ max-width:var(--lotus-content-max); margin:auto; padding:28px; }} h1,h2,p {{ margin-top:0; }} .muted {{ color:var(--muted); }} .page-subtitle {{ margin:-6px 0 10px; color:var(--yellow); font-size:13px; font-weight:800; letter-spacing:.04em; }} .header {{ display:flex; align-items:flex-start; justify-content:space-between; gap:16px; margin-bottom:28px; }} button {{ font:inherit; cursor:pointer; }} .link-button {{ color:var(--muted); background:transparent; border:0; padding:0; }} .panel,.card {{ background:var(--panel); border:1px solid var(--border); border-radius:var(--lotus-radius-card); }} .brand {{ display:inline-flex; width:max-content; }} .brand img {{ display:block; width:118px; height:auto; }} .brand-compact img {{ width:72px; }}
    @media(max-width:640px) {{ main {{ padding:24px 16px; }} .header {{ flex-direction:column; }} }}
    </style><script src="/static/security.js"></script></head><body{shell_class}>{shell_open}{body}{shell_close}</body></html>""")


def render_login_page(error: str | None = None, status_code: int = 200) -> HTMLResponse:
    error_html = f'<p class="error">{escape(error)}</p>' if error else ""
    response = _page("2Lotus | Estratégias", f"""<main class="login"><section class="panel"><img class="login-logo" src="/static/brand/lotus-icon.png" alt="2Lotus"><h1>Estratégias</h1><p class="muted">Acesse os testes e indicadores de performance.</p>{error_html}<form method="post" action="/login"><label>Senha<input type="password" name="password" autocomplete="current-password" required autofocus></label><button type="submit">Entrar</button></form></section></main><style>
    .login {{ min-height:100vh; display:grid; place-items:center; padding:20px; }} .login .panel {{ width:min(100%,400px); padding:30px; border-radius:12px; }} .login-logo {{ display:block; width:185px; height:auto; margin:0 auto 26px; }} .login label {{ display:grid; gap:8px; margin:24px 0 14px; font-size:14px; }} .login input {{ min-height:44px; border:1px solid var(--border); border-radius:6px; background:#090d13; color:var(--text); padding:10px 12px; font:inherit; }} .login button {{ width:100%; min-height:44px; border:0; border-radius:6px; background:var(--green); color:#062218; padding:10px 14px; font-weight:800; }} .error {{ color:var(--red); font-size:14px; }}
    </style>""", active_nav=None)
    response.status_code = status_code
    return response


def render_catalog_page(active_bots: list[BotCatalogItem], archived_bots: list[BotCatalogItem] | None = None) -> HTMLResponse:
    grouped = {family_id: [] for family_id, _, _ in STRATEGY_FAMILIES}
    for bot in active_bots:
        grouped[_strategy_family(bot)].append(bot)

    columns = []
    for family_id, title, description in STRATEGY_FAMILIES:
        bots = sorted(grouped[family_id], key=_family_order)
        cards = "".join(
            f'''<div class="strategy-card-row card"><div class="bot"><div class="card-meta"><span class="variant-label">{escape(_variant_label(bot, family_id, position))}</span><span class="status-badge active">Ativa</span></div><p class="market muted">{escape(bot.symbol)} · {escape(bot.timeframe)}</p><div class="strategy-title-block"><h3>{escape(bot.name)}</h3>{_subtitle_html(bot)}</div><p class="strategy-summary muted">{escape(bot.description)}</p></div><button class="strategy-card-toggle" type="button" data-chart-bot="{escape(bot.id)}" data-chart-family="{family_id}" aria-pressed="false" aria-label="Exibir {escape(bot.name)} no gráfico"><span class="strategy-card-swatch" aria-hidden="true"></span><span class="strategy-card-toggle-label">Exibir no gráfico</span></button></div>'''
            for position, bot in enumerate(bots)
        )
        if not cards:
            cards = '<div class="family-empty"><p class="muted">Nenhuma variante ativa.</p></div>'
        columns.append(
            f'''<article class="strategy-family" data-family="{family_id}"><header class="family-heading"><p class="eyebrow">{len(bots)} {"variante" if len(bots) == 1 else "variantes"}</p><h2>{escape(title)}</h2><p class="muted">{escape(description)}</p><div class="family-chart-actions"><button type="button" data-chart-family-toggle="{family_id}" aria-pressed="false">Ativar categoria</button><button type="button" data-chart-family-only="{family_id}">Somente esta</button></div></header><div class="variant-stack">{cards}</div></article>'''
        )
    family_columns = "".join(columns)
    return _page("2Lotus | Estratégias", f"""<main>
    <section>
      <section class="panel equity-panel"><div class="equity-heading"><div><p class="eyebrow">Mercado e backtest</p><h2>XAU/USD com desempenho das estratégias</h2><p class="muted">Candles no painel superior · PnL acumulado no painel inferior</p></div><div class="history-actions"><button id="refresh-history" type="button">Recarregar histórico</button><p class="muted" id="equity-status" aria-live="polite">Carregando gráfico...</p><p class="muted" id="fusion-source-status" aria-live="polite"></p></div></div><div class="chart-toolbar"><div class="chart-options" aria-label="Modo de risco"><button data-risk-mode="normalized" class="selected">1% Risk/Trade</button></div><label>Fonte <select id="chart-source"><option value="dukascopy">Dukascopy</option><option value="fusion">Fusion MT5</option></select></label><label id="chart-end-label" hidden>Até (servidor Fusion) <input id="chart-end" type="date"></label><label id="research-year-label" hidden>Estudo ZigZag M1 <select id="research-year"><option>2026</option><option>2025</option><option>2024</option><option>2023</option><option>2022</option><option>2021</option></select></label><div class="chart-options" aria-label="Duração dos candles"><button data-resolution="1m">1m</button><button data-resolution="5m">5m</button><button data-resolution="1h">1h</button><button data-resolution="1d" class="selected">1d</button></div><div class="chart-options" aria-label="Período exibido"><button data-days="7">7D</button><button data-days="30">30D</button><button data-days="90">90D</button><button data-days="365" class="selected">1A</button><button data-days="1095">3A</button></div><button id="chart-fit" type="button">Ajustar</button></div><p id="strategy-filter-hint" class="strategy-filter-hint" role="status" aria-live="polite"></p><div id="equity-empty" class="muted" hidden></div><div id="equity-chart" role="img" aria-label="Candles XAUUSD e desempenho acumulado das estratégias"></div><div id="equity-legend" class="equity-legend" aria-live="polite"></div><p class="chart-help muted">Cada período reinicia em US$ 10.000 e simula risco de 1% por entrada somente dentro da janela selecionada.</p></section>
      <div class="section-heading"><div><p class="eyebrow">Em acompanhamento</p><h2>Famílias de estratégias</h2><p class="muted">Estratégias organizadas por família e versão.</p></div><p class="muted">{len(active_bots)} variantes ativas</p></div><section class="family-grid">{family_columns}</section>
    </section></main><style>
    .header-actions {{ display:flex; gap:16px; align-items:center; }} .header-actions a {{ color:var(--text); }} .catalog-tabs {{ display:inline-flex; gap:4px; padding:4px; margin-bottom:22px; border:1px solid var(--border); border-radius:10px; background:var(--panel); }} .catalog-tabs button {{ display:flex; align-items:center; gap:9px; border:0; border-radius:7px; padding:10px 16px; background:transparent; color:var(--muted); font-weight:700; }} .catalog-tabs button[aria-selected="true"] {{ background:var(--lotus-accent-surface); color:var(--lotus-accent); }} .catalog-tabs span {{ min-width:22px; padding:2px 6px; border-radius:999px; background:rgba(127,127,127,.2); font-size:12px; text-align:center; }}
    .equity-panel {{ padding:20px; margin-bottom:28px; overflow:hidden; }} .equity-heading,.section-heading {{ display:flex; align-items:flex-start; justify-content:space-between; gap:18px; }} .equity-heading h2 {{ margin-bottom:6px; }} .history-actions {{ display:flex; flex-direction:column; align-items:flex-end; gap:8px; }} .history-actions p {{ margin:0; text-align:right; }} #refresh-history {{ padding:9px 13px; border:1px solid var(--green); border-radius:7px; color:var(--green); background:transparent; font-weight:800; }} #refresh-history:disabled {{ cursor:not-allowed; opacity:.55; }} #refresh-history[data-loading="true"] {{ cursor:wait; }} .chart-toolbar {{ display:flex; align-items:center; flex-wrap:wrap; gap:10px; margin-top:16px; }} .chart-toolbar label {{ display:grid; gap:4px; color:var(--muted); font-size:12px; }} .chart-toolbar select,.chart-toolbar input {{ padding:7px 9px; color:var(--text); background:#080b10; border:1px solid rgba(148,163,184,.25); border-radius:7px; }} .chart-toolbar label[hidden] {{ display:none; }} .chart-options {{ display:flex; padding:3px; border:1px solid rgba(148,163,184,.18); border-radius:8px; background:#080b10; }} .chart-options button,#chart-fit {{ padding:7px 10px; border:0; border-radius:6px; color:var(--muted); background:transparent; font-weight:700; }} .chart-options button.selected {{ color:#fff; background:rgba(139,124,255,.28); }} #chart-fit {{ margin-left:auto; border:1px solid rgba(148,163,184,.18); }} .strategy-filter {{ margin-top:14px; padding:14px; border:1px solid rgba(148,163,184,.18); border-radius:9px; background:#080b10; }} .strategy-filter-heading {{ display:flex; justify-content:space-between; gap:16px; }} .strategy-filter-heading h3 {{ margin:0 0 4px; font-size:15px; }} .strategy-filter-heading p {{ margin:0; font-size:12px; }} .strategy-filter-groups {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; margin-top:12px; }} .strategy-filter-group {{ min-width:0; }} .strategy-filter-group h4 {{ margin:0 0 6px; color:var(--muted); font-size:11px; letter-spacing:.06em; text-transform:uppercase; }} .strategy-toggle-row {{ display:grid; grid-template-columns:minmax(0,1fr) auto; gap:5px; margin-top:5px; }} .strategy-toggle,.strategy-isolate {{ min-height:34px; border:1px solid rgba(148,163,184,.24); border-radius:7px; color:var(--muted); background:#10151e; }} .strategy-toggle {{ display:flex; align-items:center; min-width:0; gap:8px; padding:7px 9px; text-align:left; }} .strategy-toggle span:last-child {{ overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }} .strategy-toggle[aria-pressed="true"] {{ border-color:var(--strategy-color); color:#fff; background:color-mix(in srgb,var(--strategy-color) 16%,#10151e); }} .strategy-swatch {{ flex:0 0 auto; width:10px; height:10px; border-radius:50%; background:var(--strategy-color); }} .strategy-isolate {{ padding:6px 8px; font-size:11px; }} .strategy-toggle:focus-visible,.strategy-isolate:focus-visible {{ outline:2px solid #fff; outline-offset:2px; }} .strategy-filter-hint {{ min-height:16px; margin:8px 0 0; color:var(--yellow); font-size:11px; }} .eyebrow {{ margin-bottom:6px; color:var(--green); font-size:12px; font-weight:800; letter-spacing:.08em; text-transform:uppercase; }} #equity-chart {{ width:100%; height:540px; margin-top:10px; border:1px solid rgba(148,163,184,.12); border-radius:8px; overflow:hidden; background:#0b0f16; }} .equity-legend {{ min-height:42px; display:flex; align-items:center; flex-wrap:wrap; gap:9px 16px; padding:10px 2px 0; border-top:1px solid rgba(255,255,255,.14); }} .equity-legend time,.equity-legend .ohlc {{ color:#dce4f1; font-size:12px; }} .legend-item {{ display:inline-flex; align-items:center; gap:7px; color:var(--muted); font-size:12px; }} .legend-item strong,.ohlc strong {{ color:var(--text); }} .legend-item i {{ width:18px; height:3px; border-radius:999px; }} .chart-help {{ margin:8px 0 0; font-size:11px; }} .section-heading {{ margin-bottom:14px; }} .section-heading h2 {{ margin-bottom:0; }}
    .family-grid {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:16px; align-items:start; }} .strategy-family {{ min-width:0; }} .family-heading {{ min-height:156px; padding:18px; border:1px solid var(--border); border-bottom:0; border-radius:10px 10px 0 0; background:var(--panel2); }} .family-heading h2 {{ margin-bottom:9px; font-size:20px; }} .family-heading p:last-child {{ margin-bottom:0; font-size:13px; line-height:1.45; }} .variant-stack {{ display:flex; flex-direction:column; gap:12px; padding:12px; border:1px solid var(--border); border-radius:0 0 10px 10px; background:rgba(255,255,255,.025); }} .bot {{ height:286px; min-height:286px; display:flex; flex-direction:column; align-items:stretch; padding:18px; color:var(--text); text-decoration:none; }} .bot h3,.bot p {{ margin-bottom:0; }} .strategy-title-block {{ min-height:45px; margin-bottom:10px; }} .bot h3 {{ margin:0; font-size:17px; line-height:1.25; }} .bot .strategy-subtitle {{ margin:3px 0 0; color:var(--yellow); font-size:12px; font-weight:800; line-height:1.25; letter-spacing:.025em; }} .bot .strategy-summary {{ display:-webkit-box; overflow:hidden; margin:0; font-size:13px; line-height:1.45; -webkit-box-orient:vertical; -webkit-line-clamp:4; }} .bot .results-link {{ display:block; width:100%; margin-top:auto; padding-top:12px; border-top:1px solid rgba(148,163,184,.16); color:var(--green); }} .bot .market {{ margin:11px 0 8px; font-size:12px; }} .card-meta {{ width:100%; display:flex; justify-content:space-between; gap:8px; align-items:center; }} .variant-label {{ color:var(--yellow); font-size:11px; font-weight:800; letter-spacing:.04em; text-transform:uppercase; }} .status-badge {{ padding:4px 8px; border:1px solid #555; border-radius:999px; color:var(--muted); font-size:11px; font-weight:800; text-transform:uppercase; letter-spacing:.05em; }} .status-badge.active {{ color:var(--green); border-color:rgba(65,211,146,.45); }} .family-empty {{ min-height:112px; display:grid; place-items:center; padding:18px; border:1px dashed rgba(166,166,166,.35); border-radius:8px; text-align:center; }} .family-empty p {{ margin:0; }}
    .family-heading {{ min-height:220px; }} .family-heading>p:last-of-type {{ margin-bottom:0; }} .family-chart-actions {{ display:flex; flex-wrap:wrap; gap:6px; margin-top:13px; }} .family-chart-actions button {{ padding:7px 8px; border:1px solid rgba(148,163,184,.35); border-radius:6px; color:var(--muted); background:#090c12; font-size:11px; font-weight:700; }} .family-chart-actions button[aria-pressed="true"] {{ color:#000; border-color:var(--green); background:var(--green); }} .strategy-card-row {{ display:flex; flex-direction:column; overflow:hidden; }} .strategy-card-row .bot {{ flex:0 0 auto; height:auto; min-height:0; padding-bottom:12px; }} .strategy-card-toggle {{ display:flex; align-items:center; justify-content:center; gap:8px; margin:0 12px 12px; padding:9px 12px; border:1px solid rgba(148,163,184,.28); border-radius:7px; color:var(--muted); background:#0c1017; font-size:11px; font-weight:700; }} .strategy-card-toggle[aria-pressed="true"] {{ color:#fff; border-color:var(--strategy-color); background:#15221d; }} .strategy-card-swatch {{ width:11px; height:11px; border-radius:50%; background:var(--strategy-color,#555); }} .strategy-card-toggle-label {{ line-height:1.2; }} .strategy-card-toggle:disabled,.family-chart-actions button:disabled {{ cursor:not-allowed; opacity:.35; }} .strategy-card-toggle:focus-visible,.family-chart-actions button:focus-visible {{ outline:2px solid #fff; outline-offset:2px; }}
    .history-actions {{ gap:5px; min-width:0; }}
    #equity-status,#fusion-source-status {{ max-width:430px; font-size:11px; line-height:1.35; font-variant-numeric:tabular-nums; overflow-wrap:anywhere; }}
    #fusion-source-status {{ font-size:10px; }}
    .family-chart-actions {{ flex-wrap:nowrap; }} .family-chart-actions button {{ flex:0 0 108px; width:108px; height:32px; padding:0 6px; white-space:nowrap; }}
    @media(max-width:1040px) {{ .strategy-filter-groups,.family-grid {{ grid-template-columns:repeat(2,minmax(0,1fr)); }} }} @media(max-width:720px) {{ .equity-heading,.section-heading,.strategy-filter-heading {{ flex-direction:column; }} .history-actions {{ align-items:flex-start; }} .history-actions p {{ text-align:left; }} #chart-fit {{ margin-left:0; }} .strategy-filter-groups {{ grid-template-columns:1fr; }} #equity-chart {{ height:460px; }} .family-grid {{ grid-template-columns:1fr; }} .family-heading {{ min-height:auto; }} }}
    </style><script src="/static/vendor/lightweight-charts/lightweight-charts.standalone.production.js"></script><script src="/static/equity-chart.js?v=8"></script><script>
    const equityChart=LotusEquityChart.create(document.getElementById('equity-chart'),document.getElementById('equity-legend'));
    const strategyStorageKey='2lotus:equity-visible-strategies:v2';
    let chartSource='dukascopy',chartResolution='1d',chartDays=365,currentEquityData=null,selectedBotIds=null,selectionWasSaved=false,hintTimer=null;
    function strategyFamily(profile) {{
      const value=(profile||'').toLowerCase();
      if(value.includes('portfolio')) return 'combined';
      if(value.includes('zigzag')) return 'zigzag';
      if(value.includes('multitimeframe')||value.includes('buy_trend_pullback')||value.includes('buy_trend_dip')) return 'multitimeframe';
      if(value.includes('stochastic')||value.includes('breakout_short')||value.includes('mean_reversion_sell')) return 'stochastic';
      return 'combined';
    }}
    function loadStrategySelection() {{
      try {{
        const raw=localStorage.getItem(strategyStorageKey);
        selectionWasSaved=raw!==null;
        const parsed=raw===null?null:JSON.parse(raw);
        return Array.isArray(parsed)?new Set(parsed.filter(id=>typeof id==='string')):null;
      }} catch(error) {{ selectionWasSaved=false; return null; }}
    }}
    function saveStrategySelection() {{
      try {{ localStorage.setItem(strategyStorageKey,JSON.stringify([...selectedBotIds])); selectionWasSaved=true; }} catch(error) {{ /* Storage can be unavailable in private contexts. */ }}
    }}
    function reconcileStrategySelection(series) {{
      const available=new Set(series.map(item=>item.bot_id));
      if(selectedBotIds===null) selectedBotIds=loadStrategySelection();
      const valid=new Set([...(selectedBotIds||[])].filter(id=>available.has(id)));
      if(!valid.size&&series.length) {{
        series.filter(item=>strategyFamily(item.strategy_profile)==='combined').forEach(item=>valid.add(item.bot_id));
        if(!valid.size) valid.add(series[0].bot_id);
      }}
      selectedBotIds=valid;
      if(selectionWasSaved||valid.size) saveStrategySelection();
    }}
    function showStrategyHint(message) {{
      const hint=document.getElementById('strategy-filter-hint');
      hint.textContent=message;
      clearTimeout(hintTimer);
      hintTimer=setTimeout(()=>{{hint.textContent='';}},2400);
    }}
    function syncStrategyControls() {{
      const state=equityChart.getSeriesState(),byId=new Map(state.map(item=>[item.botId,item]));
      document.querySelectorAll('[data-chart-bot]').forEach(button=>{{
        const item=byId.get(button.dataset.chartBot),visible=Boolean(item&&item.visible);
        button.disabled=!item; button.setAttribute('aria-pressed',String(visible));
        button.setAttribute('aria-label',(visible?'Ocultar ':'Exibir ')+(item?item.name:'estratégia indisponível')+' no gráfico');
        button.querySelector('.strategy-card-toggle-label').textContent=visible?'No gráfico':'Exibir no gráfico';
        if(item) button.style.setProperty('--strategy-color',item.color);
      }});
      document.querySelectorAll('[data-chart-family-toggle]').forEach(button=>{{
        const ids=state.filter(item=>strategyFamily(item.strategyProfile)===button.dataset.chartFamilyToggle).map(item=>item.botId);
        const allActive=ids.length>0&&ids.every(id=>selectedBotIds.has(id));
        button.disabled=!ids.length; button.setAttribute('aria-pressed',String(allActive)); button.textContent=allActive?'Desativar':'Ativar categoria';
      }});
      document.querySelectorAll('[data-chart-family-only]').forEach(button=>{{
        button.disabled=!state.some(item=>strategyFamily(item.strategyProfile)===button.dataset.chartFamilyOnly);
      }});
    }}
    function applyStrategySelection() {{
      equityChart.setVisibleBotIds(selectedBotIds);
      syncStrategyControls();
      updateEquityStatus();
      saveStrategySelection();
    }}
    function toggleStrategy(botId) {{
      if(selectedBotIds.has(botId)&&selectedBotIds.size===1) {{ showStrategyHint('Pelo menos uma estratégia deve permanecer visível.'); return; }}
      if(selectedBotIds.has(botId)) selectedBotIds.delete(botId); else selectedBotIds.add(botId);
      applyStrategySelection();
    }}
    function toggleFamily(familyId) {{
      const ids=equityChart.getSeriesState().filter(item=>strategyFamily(item.strategyProfile)===familyId).map(item=>item.botId);
      const allActive=ids.length&&ids.every(id=>selectedBotIds.has(id));
      if(allActive&&selectedBotIds.size===ids.filter(id=>selectedBotIds.has(id)).length) {{ showStrategyHint('Pelo menos uma categoria deve permanecer visível.'); return; }}
      ids.forEach(id=>allActive?selectedBotIds.delete(id):selectedBotIds.add(id)); applyStrategySelection();
    }}
    function isolateFamily(familyId) {{
      selectedBotIds=new Set(equityChart.getSeriesState().filter(item=>strategyFamily(item.strategyProfile)===familyId).map(item=>item.botId));
      if(selectedBotIds.size) applyStrategySelection();
    }}
    function updateEquityStatus() {{
      if(!currentEquityData) return;
      const visibleSeries=(currentEquityData.series||[]).filter(item=>selectedBotIds&&selectedBotIds.has(item.bot_id));
      const trades=visibleSeries.reduce((total,item)=>total+Number(item.summary&&item.summary.trades_count||0),0);
      document.getElementById('equity-status').textContent=currentEquityData.source==='fusion'
        ? 'Fusion '+currentEquityData.resolution+' · hora do servidor · release '+currentEquityData.dataset_version+' · '+(currentEquityData.candles||[]).length+' candles · '+visibleSeries.length+' curvas de backtest de pesquisa'+((currentEquityData.candles||[]).length===5000?' (limite de exibição: 5.000; ajuste a data para navegar)':'')
        : (currentEquityData.candles||[]).length+' candles · '+visibleSeries.length+' de '+(currentEquityData.series||[]).length+' curvas'+(trades?' · '+trades+' trades':' · nenhum trade no período')+((currentEquityData.missing_bot_ids||[]).length?' · '+currentEquityData.missing_bot_ids.length+' pendentes':'');
    }}
    function renderEquity(data) {{
      const host=document.getElementById('equity-chart'), empty=document.getElementById('equity-empty'), legend=document.getElementById('equity-legend');
      const hasCandles=(data.candles||[]).length>0, hasCurves=(data.series||[]).some(item=>item.points&&item.points.length);
      const drawableSeries=(data.series||[]).filter(item=>item.points&&item.points.length);
      reconcileStrategySelection(drawableSeries);
      if(!hasCandles&&!hasCurves) {{ host.hidden=true; empty.hidden=false; empty.textContent='O histórico de mercado e o backtest ainda não foram carregados para este ativo.'; legend.innerHTML=''; syncStrategyControls(); return; }}
      host.hidden=false; empty.hidden=true; equityChart.setData(data,{{visibleBotIds:selectedBotIds}}); syncStrategyControls();
    }}
    async function loadActiveEquity() {{
      try {{ const response=await fetch('/api/backtest-market-chart?symbol=XAUUSD&source='+chartSource+'&resolution='+chartResolution+'&days='+chartDays+'&mode=normalized'+(chartSource==='fusion'&&document.getElementById('chart-end').value?'&end='+document.getElementById('chart-end').value:'')); if(!response.ok) throw new Error('Não foi possível carregar o mercado e os backtests.'); const data=await response.json(); currentEquityData=data; renderEquity(data); updateEquityStatus();
        const fusionStatus=document.getElementById('fusion-source-status');
        if(chartSource==='fusion') {{
          const status=await fetch('/api/research/fusion/status').then(result=>result.json());
          const m1=status.M1, m5=status.M5;
          fusionStatus.textContent=(m1.available?'M1: '+Number(m1.rows).toLocaleString('pt-BR')+' candles ('+m1.first_server_time.slice(0,10)+' a '+m1.last_server_time.slice(0,10)+')':'M1 indisponível')+' · '+(m5.available?'M5: '+Number(m5.rows).toLocaleString('pt-BR')+' candles':'M5 indisponível')+' · hora do servidor Fusion.';
          if(chartResolution==='1m') {{
            const study=await fetch('/api/research/fusion-m1/zigzag?year='+document.getElementById('research-year').value);
            if(study.ok) {{ const result=await study.json(); fusionStatus.textContent+=' ZigZag M1 shadow '+result.year+': '+result.trades_count+' operações; PnL '+Number(result.net_pnl).toLocaleString('pt-BR',{{style:'currency',currency:'USD'}})+'.'; }}
          }}
        }} else fusionStatus.textContent='';
        return true;
      }} catch(error) {{ document.getElementById('equity-status').textContent='Erro ao carregar o gráfico: '+error.message; return false; }}
    }}
    async function refreshHistory() {{
      const button=document.getElementById('refresh-history'),status=document.getElementById('equity-status');
      button.disabled=true; button.dataset.loading='true'; button.textContent='Atualizando...';
      try {{
        if(chartSource==='fusion') {{
          status.textContent='Recarregando candles Fusion do release publicado...';
          if(!await loadActiveEquity()) return;
          status.textContent='Histórico Fusion recarregado do release '+(currentEquityData&&currentEquityData.dataset_version||'atual')+'.';
          return;
        }}
        status.textContent='Publicando downloads, importando candles e recalculando backtests...';
        const response=await fetch('/api/history/refresh?symbol=XAUUSD&days='+chartDays,{{method:'POST'}});
        const payload=await response.json().catch(()=>({{}}));
        if(!response.ok) throw new Error(payload.detail||'Não foi possível atualizar o histórico.');
        await loadActiveEquity();
        showStrategyHint(payload.snapshots_updated+' backtests atualizados · '+payload.candles_imported+' candles importados.');
      }} catch(error) {{ status.textContent=error.message; }} finally {{ button.disabled=false; delete button.dataset.loading; button.textContent='Recarregar histórico'; }}
    }}
    document.getElementById('refresh-history').onclick=refreshHistory;
    document.getElementById('chart-source').onchange=event=>{{chartSource=event.target.value;chartResolution='1d';document.querySelectorAll('[data-resolution]').forEach(item=>item.classList.toggle('selected',item.dataset.resolution===chartResolution));document.getElementById('chart-end-label').hidden=chartSource!=='fusion';document.getElementById('research-year-label').hidden=chartSource!=='fusion';loadActiveEquity();}};
    document.querySelectorAll('[data-chart-bot]').forEach(button=>button.onclick=()=>toggleStrategy(button.dataset.chartBot));
    document.querySelectorAll('[data-chart-family-toggle]').forEach(button=>button.onclick=()=>toggleFamily(button.dataset.chartFamilyToggle));
    document.querySelectorAll('[data-chart-family-only]').forEach(button=>button.onclick=()=>isolateFamily(button.dataset.chartFamilyOnly));
    document.querySelectorAll('[data-resolution]').forEach(button=>button.onclick=()=>{{document.querySelectorAll('[data-resolution]').forEach(item=>item.classList.remove('selected'));button.classList.add('selected');chartResolution=button.dataset.resolution;loadActiveEquity();}});
    document.querySelectorAll('[data-days]').forEach(button=>button.onclick=()=>{{document.querySelectorAll('[data-days]').forEach(item=>item.classList.remove('selected'));button.classList.add('selected');chartDays=Number(button.dataset.days);loadActiveEquity();}});
    document.getElementById('chart-end').onchange=loadActiveEquity;
    document.getElementById('research-year').onchange=event=>{{document.getElementById('chart-end').value=event.target.value==='2026'?'':event.target.value+'-12-31';loadActiveEquity();}};
    document.getElementById('chart-fit').onclick=()=>equityChart.fitContent();
    document.getElementById('chart-source').value=new URLSearchParams(location.search).get('source')==='dukascopy'?'dukascopy':'fusion';
    document.getElementById('chart-source').dispatchEvent(new Event('change'));
    </script>""")


def _render_growth_simulator_page_legacy() -> HTMLResponse:
    return _page("2Lotus | Simulador de crescimento", """<main><header class="header"><div><a class="brand brand-compact" href="/bots" aria-label="2Lotus"><img src="/static/brand/lotus-icon.png" alt="2Lotus"></a><p class="eyebrow">Portfólio Combinado V1</p><h1>Simulador de crescimento</h1><p class="muted">Reaplique as 802 operações do replay anual com capital e risco personalizados.</p></div><div class="actions"><a href="/bots/core-portfolio">Ver estratégia</a><a href="/bots">Estratégias</a><form method="post" action="/logout"><button class="link-button" type="submit">Sair</button></form></div></header>
    <section class="panel controls"><form id="simulation-form"><label>Capital inicial (USD)<input id="initial-balance" name="initial_balance" type="number" min="100" max="100000000" step="100" value="10000" required></label><label>Risco-base por operação (%)<input id="risk" name="risk_per_trade_pct" type="number" min="0.01" max="10" step="0.01" value="0.25" required></label><button type="submit">Simular curva</button></form><p class="muted">O risco é recalculado sobre o saldo antes de cada operação. A sequência de entradas e os resultados em R permanecem iguais ao backtest.</p></section>
    <section class="cards"><article class="card"><p class="muted">Saldo final</p><strong id="final-balance">-</strong><span id="initial-label">-</span></article><article class="card"><p class="muted">PnL projetado</p><strong id="net-pnl">-</strong><span id="return-pct">-</span></article><article class="card"><p class="muted">Drawdown máximo</p><strong id="drawdown">-</strong><span id="drawdown-pct">-</span></article><article class="card"><p class="muted">Operações simuladas</p><strong id="trades">-</strong><span id="period">-</span></article></section>
    <section class="panel chart-panel"><div class="chart-heading"><div><h2>Curva de saldo</h2><p class="muted">Referência: US$ 10.000 e risco de 0,25% · Simulação: valores personalizados</p></div><p class="muted" id="status">Carregando...</p></div><div id="chart-empty" class="muted" hidden></div><svg id="growth-chart" viewBox="0 0 1100 440" role="img" aria-label="Curva simulada de crescimento"></svg><div class="legend"><span><i class="reference"></i>Referência</span><span><i class="simulation"></i>Simulação personalizada</span></div></section>
    <section class="panel warning"><strong>Importante</strong><p class="muted">Esta é uma projeção matemática sobre o histórico já observado. Ela não prevê resultados futuros e não considera mudanças de liquidez, slippage ou capacidade operacional causadas por volumes maiores.</p></section></main><style>
    .eyebrow { margin:0 0 7px; color:var(--green); font-size:12px; font-weight:800; letter-spacing:.08em; text-transform:uppercase; } .actions { display:flex; gap:14px; align-items:flex-start; flex-wrap:wrap; } .actions a { color:var(--text); } .controls { padding:20px; margin-bottom:18px; } .controls form { display:grid; grid-template-columns:repeat(2,minmax(180px,260px)) auto; gap:14px; align-items:end; } label { display:grid; gap:7px; color:var(--muted); font-size:13px; font-weight:700; } input { width:100%; padding:11px 12px; color:var(--text); background:var(--lotus-bg); border:1px solid var(--border); border-radius:7px; font:inherit; } input:focus { outline:2px solid rgba(65,211,146,.35); border-color:var(--green); } .controls button { padding:11px 18px; border:0; border-radius:var(--lotus-radius-control); color:#062218; background:var(--lotus-accent); font-weight:800; } .controls p { margin:14px 0 0; line-height:1.5; } .cards { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:14px; margin-bottom:18px; } .card { padding:18px; } .card strong { display:block; margin-bottom:8px; font-size:26px; } .card span { color:var(--muted); font-size:13px; } .green { color:var(--green); } .red { color:var(--red); } .chart-panel { padding:20px; margin-bottom:18px; } .chart-heading { display:flex; justify-content:space-between; gap:18px; } .chart-heading h2 { margin-bottom:6px; } #growth-chart { width:100%; min-height:330px; margin-top:8px; } .legend { display:flex; gap:20px; padding-top:12px; border-top:1px solid rgba(255,255,255,.14); color:var(--muted); font-size:13px; } .legend span { display:flex; align-items:center; gap:8px; } .legend i { display:block; width:22px; height:3px; border-radius:999px; } .legend .reference { background:#777; } .legend .simulation { background:var(--green); } .warning { padding:18px; border-left:3px solid var(--yellow); } .warning p { margin:7px 0 0; line-height:1.55; } @media(max-width:850px) { .cards { grid-template-columns:repeat(2,1fr); } .controls form { grid-template-columns:1fr 1fr; } .controls button { grid-column:1/-1; } } @media(max-width:560px) { .cards,.controls form { grid-template-columns:1fr; } .controls button { grid-column:auto; } .chart-heading,.actions { flex-direction:column; } #growth-chart { min-height:260px; } }
    </style><script>
    const money=value=>new Intl.NumberFormat('pt-BR',{style:'currency',currency:'USD'}).format(value||0); const pct=value=>new Intl.NumberFormat('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2}).format(value||0)+'%';
    function renderChart(data) { const svg=document.getElementById('growth-chart'), empty=document.getElementById('chart-empty'), series=[{...data.reference,color:'#777'},{...data.simulation,color:'#41d392'}].filter(item=>item.points.length); if(!series.length){svg.hidden=true;empty.hidden=false;empty.textContent='Não há operações para simular.';return;} svg.hidden=false;empty.hidden=true; const W=1100,H=440,L=86,R=22,T=22,B=48; const times=series.flatMap(item=>item.points.map(p=>+new Date(p.day+'T00:00:00Z'))), balances=series.flatMap(item=>item.points.map(p=>+p.balance)); const minX=Math.min(...times),maxX=Math.max(...times),rawMin=Math.min(...balances),rawMax=Math.max(...balances),pad=Math.max((rawMax-rawMin)*.12,100),minY=Math.max(0,rawMin-pad),maxY=rawMax+pad; const x=v=>L+(v-minX)*(W-L-R)/Math.max(maxX-minX,1),y=v=>T+(maxY-v)*(H-T-B)/Math.max(maxY-minY,1); const grid=[0,.25,.5,.75,1].map(r=>{const value=maxY-(maxY-minY)*r,yy=y(value);return `<line x1="${L}" x2="${W-R}" y1="${yy}" y2="${yy}" stroke="#292929"/><text x="${L-9}" y="${yy+4}" text-anchor="end" fill="#999" font-size="11">${money(value)}</text>`}).join(''); const paths=series.map(item=>{const d=item.points.map((p,i)=>`${i?'L':'M'} ${x(+new Date(p.day+'T00:00:00Z')).toFixed(1)} ${y(+p.balance).toFixed(1)}`).join(' '); const last=item.points.at(-1); return `<path d="${d}" fill="none" stroke="${item.color}" stroke-width="${item.label==='Simulação'?4:2}" stroke-linejoin="round"/><circle cx="${x(+new Date(last.day+'T00:00:00Z'))}" cy="${y(+last.balance)}" r="5" fill="${item.color}"><title>${item.label}: ${money(last.balance)}</title></circle>`}).join(''); const labels=`<text x="${L}" y="${H-12}" fill="#999" font-size="11">${new Date(minX).toLocaleDateString('pt-BR')}</text><text x="${W-R}" y="${H-12}" text-anchor="end" fill="#999" font-size="11">${new Date(maxX).toLocaleDateString('pt-BR')}</text>`; svg.innerHTML=grid+paths+labels; }
    function render(data) { const s=data.simulation; document.getElementById('final-balance').textContent=money(s.final_balance); document.getElementById('initial-label').textContent='Capital inicial '+money(s.initial_balance)+' · risco '+pct(s.risk_per_trade_pct); const pnl=document.getElementById('net-pnl'); pnl.textContent=money(s.net_pnl); pnl.className=s.net_pnl>=0?'green':'red'; document.getElementById('return-pct').textContent='Retorno '+pct(s.return_pct); document.getElementById('drawdown').textContent=money(s.max_drawdown); document.getElementById('drawdown-pct').textContent=pct(s.max_drawdown_pct)+' sobre o pico'; document.getElementById('trades').textContent=s.trades_simulated; document.getElementById('period').textContent=new Date(data.period_start_utc).toLocaleDateString('pt-BR')+' a '+new Date(data.period_end_utc).toLocaleDateString('pt-BR'); document.getElementById('status').textContent='Curva atualizada'; renderChart(data); }
    async function simulate(event) { if(event)event.preventDefault(); const form=document.getElementById('simulation-form'),params=new URLSearchParams(new FormData(form)); document.getElementById('status').textContent='Simulando...'; const response=await fetch('/api/growth-simulation?'+params); if(!response.ok){const payload=await response.json().catch(()=>({}));throw new Error(payload.detail||'Não foi possível executar a simulação.');} render(await response.json()); }
    document.getElementById('simulation-form').onsubmit=event=>simulate(event).catch(error=>document.getElementById('status').textContent=error.message); simulate().catch(error=>document.getElementById('status').textContent=error.message);
    </script>""")


def _render_growth_simulator_page_v2_legacy() -> HTMLResponse:
    return _page("2Lotus | Simulador", """<main><header class="header"><div><a class="brand brand-compact" href="/bots"><img src="/static/brand/lotus-icon.png" alt="2Lotus"></a><p class="eyebrow">Portfólio Combinado V1</p><h1>Simulador de crescimento</h1><p class="muted">Reaplique as operações anuais com risco composto e reduções permanentes por saldo.</p></div><div class="actions"><a href="/operations">Saúde</a><a href="/bots">Estratégias</a></div></header>
    <section class="panel controls"><form id="simulation-form"><label>Capital inicial (USD)<input id="initial-balance" type="number" min="1" max="100000000" step="1" value="10000" required></label><label>Risco por operação (%)<input id="base-risk" type="number" min="0.01" max="10" step="0.01" value="0.25" required></label><button class="primary" type="submit">Simular curva</button><div class="optional-tiers"><div class="tier-heading"><div><strong>Faixas de redução de risco</strong><small class="muted">Opcional</small></div><button id="add-tier" type="button">+ Adicionar faixa</button></div><div id="tiers"></div></div></form><p class="muted">Se adicionar faixas, o risco menor fica travado ao atingir o capital definido, mesmo que o saldo recue.</p></section>
    <section class="cards"><article class="card"><p class="muted">Saldo final</p><strong id="final-balance">-</strong><span id="minimum-balance">-</span></article><article class="card"><p class="muted">PnL / retorno</p><strong id="net-pnl">-</strong><span id="return-pct">-</span></article><article class="card"><p class="muted">Drawdown máximo</p><strong id="drawdown">-</strong><span id="drawdown-pct">-</span></article><article class="card"><p class="muted">Operações</p><strong id="trades">-</strong><span id="period">-</span></article></section>
    <section class="panel chart-panel"><div class="chart-heading"><div><h2>Curva de saldo</h2><p class="muted">Cenário calculado com o capital e o risco informados.</p></div><p class="muted" id="status">Carregando...</p></div><svg id="growth-chart" viewBox="0 0 1100 440" role="img"></svg><div id="milestones" class="milestones"></div></section>
    <section class="panel warning"><strong>Projeção histórica</strong><p class="muted">Não prevê resultados futuros e não modela lote mínimo, margem ou mudança de execução em volumes maiores.</p></section></main><style>
    .eyebrow{color:var(--green);font-size:12px;font-weight:800;text-transform:uppercase}.actions{display:flex;gap:14px}.actions a{color:var(--text)}.controls,.chart-panel,.warning{padding:20px;margin-bottom:18px}.controls form{display:grid;grid-template-columns:220px 220px auto;gap:18px;align-items:end}label{display:grid;gap:7px;color:var(--muted);font-size:13px}input{padding:10px;color:#fff;background:var(--lotus-bg);border:1px solid var(--border);border-radius:7px;font:inherit}.optional-tiers{grid-column:1/-1;padding-top:4px}.tier-heading,.tier-row{display:flex;gap:10px;align-items:center}.tier-heading{justify-content:space-between;margin-bottom:8px}.tier-heading strong,.tier-heading small{display:block}.tier-heading small{margin-top:3px}.tier-row{margin-top:7px}.tier-row input{width:150px}.tier-row button,.tier-heading button{color:var(--muted);background:var(--lotus-bg);border:1px solid var(--border);border-radius:6px;padding:8px}.primary{min-height:44px;padding:11px 18px;background:var(--lotus-accent);color:#062218;border:0;border-radius:var(--lotus-radius-control);font-weight:800}.cards{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:18px}.card{padding:18px}.card strong{display:block;font-size:25px;margin-bottom:7px}.card span{color:var(--muted);font-size:13px}.chart-heading{display:flex;justify-content:space-between;gap:16px}#growth-chart{width:100%;min-height:330px}.milestones{display:flex;flex-wrap:wrap;gap:8px;border-top:1px solid #333;padding-top:12px}.milestones span{padding:7px 9px;background:#151515;border-radius:6px;color:var(--muted);font-size:12px}.milestones:empty{display:none}.warning{border-left:3px solid var(--yellow)}.warning p{margin:7px 0 0}.green{color:var(--green)}.red{color:var(--red)}@media(max-width:800px){.controls form,.cards{grid-template-columns:1fr 1fr}.primary{grid-column:1/-1}}@media(max-width:560px){.controls form,.cards{grid-template-columns:1fr}.primary{grid-column:auto}.tier-row{flex-wrap:wrap}.chart-heading,.actions{flex-direction:column}}
    </style><script>
    const money=v=>new Intl.NumberFormat('pt-BR',{style:'currency',currency:'USD'}).format(v||0),pct=v=>Number(v||0).toLocaleString('pt-BR',{minimumFractionDigits:2,maximumFractionDigits:2})+'%';
    function addTier(threshold='',risk=''){const row=document.createElement('div');row.className='tier-row';row.innerHTML=`<input data-field="threshold" type="number" min="0" step="1" value="${threshold}" placeholder="Capital da faixa" aria-label="Saldo da faixa" required><span>USD →</span><input data-field="risk" type="number" min="0.01" max="10" step="0.01" value="${risk}" placeholder="Novo risco" aria-label="Risco da faixa" required><span>%</span><button type="button">Remover</button>`;row.querySelector('button').onclick=()=>row.remove();document.getElementById('tiers').append(row)} document.getElementById('add-tier').onclick=()=>addTier();
    function chart(data){const svg=document.getElementById('growth-chart'),series=data.simulation,W=1100,H=440,L=86,R=20,T=20,B=45,times=series.points.map(p=>+new Date(p.day+'T00:00:00Z')),vals=series.points.map(p=>+p.balance),minX=Math.min(...times),maxX=Math.max(...times),lo=Math.min(...vals),hi=Math.max(...vals),pad=Math.max((hi-lo)*.1,1),minY=Math.max(0,lo-pad),maxY=hi+pad,x=v=>L+(v-minX)*(W-L-R)/Math.max(maxX-minX,1),y=v=>T+(maxY-v)*(H-T-B)/Math.max(maxY-minY,1);const grid=[0,.25,.5,.75,1].map(r=>{const v=maxY-(maxY-minY)*r,yy=y(v);return `<line x1="${L}" x2="${W-R}" y1="${yy}" y2="${yy}" stroke="#292929"/><text x="${L-8}" y="${yy+4}" text-anchor="end" fill="#999" font-size="11">${money(v)}</text>`}).join(''),path=`<path d="${series.points.map((p,i)=>`${i?'L':'M'} ${x(+new Date(p.day+'T00:00:00Z'))} ${y(+p.balance)}`).join(' ')}" fill="none" stroke="#41d392" stroke-width="4"/>`;svg.innerHTML=grid+path}
    function render(data){const s=data.simulation;document.getElementById('final-balance').textContent=money(s.final_balance);document.getElementById('minimum-balance').textContent='Mínimo '+money(s.minimum_balance);const pnl=document.getElementById('net-pnl');pnl.textContent=money(s.net_pnl);pnl.className=s.net_pnl>=0?'green':'red';document.getElementById('return-pct').textContent=pct(s.return_pct);document.getElementById('drawdown').textContent=money(s.max_drawdown);document.getElementById('drawdown-pct').textContent=pct(s.max_drawdown_pct);document.getElementById('trades').textContent=s.trades_simulated;document.getElementById('period').textContent=new Date(data.period_start_utc).toLocaleDateString('pt-BR')+' a '+new Date(data.period_end_utc).toLocaleDateString('pt-BR');document.getElementById('milestones').innerHTML=s.milestones.map(m=>`<span>${money(m.balance_threshold)} · ${pct(m.risk_per_trade_pct)} · ${m.reached_at_utc?new Date(m.reached_at_utc).toLocaleDateString('pt-BR'):'não atingido'}</span>`).join('');document.getElementById('status').textContent='Curva atualizada';chart(data)}
    async function simulate(event){if(event)event.preventDefault();const tiers=[{balance_threshold:0,risk_per_trade_pct:+document.getElementById('base-risk').value},...[...document.querySelectorAll('.tier-row')].map(row=>({balance_threshold:+row.querySelector('[data-field="threshold"]').value,risk_per_trade_pct:+row.querySelector('[data-field="risk"]').value}))];document.getElementById('status').textContent='Simulando...';const response=await fetch('/api/growth-simulation',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({initial_balance:+document.getElementById('initial-balance').value,risk_tiers:tiers})});if(!response.ok){const p=await response.json().catch(()=>({}));throw new Error(p.detail||'Falha na simulação.')}render(await response.json())}document.getElementById('simulation-form').onsubmit=e=>simulate(e).catch(err=>document.getElementById('status').textContent=err.message);simulate().catch(err=>document.getElementById('status').textContent=err.message);
    </script>""")


def render_growth_simulator_page(bots: list[BotCatalogItem] | None = None) -> HTMLResponse:
    active = sorted(bots or [], key=lambda bot: (_strategy_family(bot), _family_order(bot)))
    controls = "".join(
        f'<label class="strategy-choice" data-family="{_strategy_family(bot)}"><input type="checkbox" value="{escape(bot.id)}" '
        f'{"checked" if bot.id == "core-combined-v3" else ""}><span>{escape(bot.name)}</span></label>'
        for bot in active
    )
    return _page("2Lotus | Simulador", f"""<main>
    <section class="panel controls"><form id="form"><label>Capital inicial (USD)<input id="capital" type="number" min="1" max="100000000" value="10000"></label><label>Risco por operação (%)<input id="risk" type="number" min="0.01" max="10" step="0.01" value="1"></label><label>Período<select id="days"><option value="30">30 dias</option><option value="90">90 dias</option><option value="365" selected>1 ano</option></select></label><button class="primary" type="submit">Simular</button></form></section>
    <section class="panel selector"><div class="family-actions"><button data-family-button="zigzag">Scalp</button><button data-family-button="stochastic">Sell</button><button data-family-button="multitimeframe">Buy</button><button data-family-button="combined">Combined</button><button id="clear" type="button">Limpar</button></div><div class="strategy-grid">{controls}</div></section>
    <section class="panel chart-panel"><div class="chart-heading"><div><h2>Curvas de crescimento</h2><p class="muted">Cada linha reaplica a sequência real de resultados em R.</p></div><p id="status" class="muted">Carregando...</p></div><svg id="chart" viewBox="0 0 1100 460" role="img"></svg><div id="legend" class="legend"></div></section>
    <section id="summaries" class="summaries"></section><section class="panel warning"><strong>Simulação histórica</strong><p class="muted">Não prevê resultados futuros. Riscos maiores amplificam drawdown, exposição e efeito composto.</p></section></main><style>
    a{{color:var(--text)}}.eyebrow{{color:var(--green);font-size:12px;font-weight:800;text-transform:uppercase}}.controls,.selector,.chart-panel,.warning{{padding:20px;margin-bottom:18px}}form{{display:flex;flex-wrap:wrap;gap:14px;align-items:end}}label{{display:grid;gap:6px;color:var(--muted);font-size:12px}}input,select{{padding:10px;color:#fff;background:var(--lotus-bg);border:1px solid var(--border);border-radius:7px}}.mode,.family-actions{{display:flex;flex-wrap:wrap;gap:6px}}button{{padding:9px 12px;border:1px solid var(--border);border-radius:7px;color:var(--muted);background:#090909}}button.selected,.primary{{color:var(--lotus-accent);background:var(--lotus-accent-surface)}}.strategy-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:14px}}.strategy-choice{{display:flex;align-items:center;gap:8px;padding:10px;border:1px solid #333;border-radius:7px;background:#101010}}.strategy-choice input{{accent-color:#fff}}.chart-heading{{display:flex;justify-content:space-between;gap:12px}}#chart{{width:100%;min-height:360px}}.legend{{display:flex;flex-wrap:wrap;gap:12px}}.legend span{{font-size:12px;color:var(--muted)}}.legend i{{display:inline-block;width:18px;height:3px;margin-right:6px}}.summaries{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:18px}}.summary{{padding:16px}}.summary strong{{display:block;font-size:21px;margin:7px 0}}.summary small{{color:var(--muted)}}.warning{{border-left:3px solid var(--yellow)}}@media(max-width:760px){{.strategy-grid,.summaries{{grid-template-columns:1fr}}}}
    </style><script>
    const palette={{zigzag:'#a855f7',stochastic:'#3b82f6',multitimeframe:'#67e8f9',combined:'#ef4444'}};const mode='normalized';
    const family=p=>p.includes('portfolio')?'combined':p.includes('zigzag')?'zigzag':p.includes('stochastic')?'stochastic':'multitimeframe';
    document.querySelectorAll('[data-family-button]').forEach(b=>b.onclick=()=>{{document.querySelectorAll(`.strategy-choice[data-family="${{b.dataset.familyButton}}"] input`).forEach(x=>x.checked=true);simulate()}});document.getElementById('clear').onclick=()=>{{document.querySelectorAll('.strategy-choice input').forEach(x=>x.checked=false);draw({{series:[]}})}};
    const money=v=>new Intl.NumberFormat('pt-BR',{{style:'currency',currency:'USD'}}).format(v||0);
    function draw(data){{const svg=document.getElementById('chart'),all=data.series.flatMap(s=>s.simulation.points.map(p=>+p.balance));if(!all.length){{svg.innerHTML='<text x="550" y="220" text-anchor="middle" fill="#999">Selecione uma estratégia</text>';document.getElementById('legend').innerHTML='';document.getElementById('summaries').innerHTML='';return}}const W=1100,H=460,L=92,R=22,T=20,B=42,lo=Math.min(...all),hi=Math.max(...all),days=data.series.flatMap(s=>s.simulation.points.map(p=>+new Date(p.day+'T00:00:00Z'))),a=Math.min(...days),z=Math.max(...days),x=v=>L+(v-a)*(W-L-R)/Math.max(z-a,1),y=v=>T+(hi-v)*(H-T-B)/Math.max(hi-lo,1),grid=[0,.25,.5,.75,1].map(q=>{{const v=hi-(hi-lo)*q,yy=y(v);return `<line x1="${{L}}" x2="${{W-R}}" y1="${{yy}}" y2="${{yy}}" stroke="#292929"/><text x="${{L-8}}" y="${{yy+4}}" text-anchor="end" fill="#999" font-size="11">${{money(v)}}</text>`}}).join('');svg.innerHTML=grid+data.series.map((s,i)=>{{const c=palette[family(s.strategy_profile)],dash=[null,'10 6','3 5','14 5 3 5'][i%4];return `<path d="${{s.simulation.points.map((p,j)=>`${{j?'L':'M'}} ${{x(+new Date(p.day+'T00:00:00Z'))}} ${{y(+p.balance)}}`).join(' ')}}" fill="none" stroke="${{c}}" stroke-width="3" ${{dash?`stroke-dasharray="${{dash}}"`:''}}/>`}}).join('');document.getElementById('legend').innerHTML=data.series.map(s=>`<span><i style="background:${{palette[family(s.strategy_profile)]}}"></i>${{s.bot_name}}</span>`).join('');document.getElementById('summaries').innerHTML=data.series.map(s=>`<article class="card summary"><small>${{s.bot_name}}</small><strong>${{money(s.simulation.final_balance)}}</strong><small>Lucro ${{money(s.simulation.net_pnl)}} · DD ${{s.simulation.max_drawdown_pct.toFixed(2)}}% · ${{s.simulation.trades_simulated}} trades</small></article>`).join('')}}
    async function simulate(e){{if(e)e.preventDefault();const ids=[...document.querySelectorAll('.strategy-choice input:checked')].map(x=>x.value);if(!ids.length)return draw({{series:[]}});document.getElementById('status').textContent='Simulando...';const body={{bot_ids:ids,mode,days:+document.getElementById('days').value,initial_balance:+document.getElementById('capital').value,risk_tiers:[{{balance_threshold:0,risk_per_trade_pct:+document.getElementById('risk').value}}]}};const response=await fetch('/api/growth-comparison',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(body)}});const data=await response.json();if(!response.ok)throw Error(data.detail||'Falha na simulação');draw(data);document.getElementById('status').textContent=data.series.length+' estratégias · '+(mode==='normalized'?'normalizado':'operacional')}}document.getElementById('form').onsubmit=e=>simulate(e).catch(err=>document.getElementById('status').textContent=err.message);simulate().catch(err=>document.getElementById('status').textContent=err.message);
    </script>""")


def render_history_page(source: str = "dukascopy") -> HTMLResponse:
    source_name = "Dukascopy" if source == "dukascopy" else "Fusion Markets · MT5"
    source_status = "Histórico baixado" if source == "dukascopy" else "Candles M1/M5 publicados"
    page = """<main><header class="header"><div><a class="brand brand-compact" href="/bots" aria-label="2Lotus"><img src="/static/brand/lotus-icon.png" alt="2Lotus"></a><h1>Histórico do ouro</h1><p class="muted">__SOURCE_NAME__: acompanhamento anual dos ticks XAUUSD.</p></div><div class="live-state"><span class="state-dot" id="state-dot"></span><div><strong id="state-label">Verificando tarefa...</strong><small id="updated-label">Aguardando dados</small></div></div></header>
    <section class="source-panel panel" aria-labelledby="tick-sources-title"><div class="source-heading"><div><p class="eyebrow">Proveniência</p><h2 id="tick-sources-title">Fontes de ticks</h2><p class="muted">Escolha uma fonte para abrir seu histórico por ano. preço e spread não são intercambiáveis entre corretoras.</p></div><span class="source-badge">XAUUSD · Bid/Ask</span></div><div class="source-grid"><a class="source-card dukascopy-source __DUKASCOPY_SELECTED__" href="/history?source=dukascopy"><div class="source-card-heading"><div><strong>Dukascopy</strong><span class="source-status ready">Histórico baixado</span></div><span class="source-role">Pesquisa histórica</span></div><p>Base histórica ampla em UTC, usada para cobertura de mercado, replays e comparação de hipóteses.</p><dl><div><dt>Origem</dt><dd>Download Dukascopy</dd></div><div><dt>Uso</dt><dd>Pesquisa e baseline</dd></div><div><dt>Execução Fusion</dt><dd>Não representa</dd></div></dl><small class="source-open">Abrir histórico anual →</small></a><a class="source-card fusion-source __FUSION_SELECTED__" href="/history?source=fusion"><div class="source-card-heading"><div><strong>Fusion Markets · MT5</strong><span class="source-status waiting">Acompanhar exportação</span></div><span class="source-role">Validação de execução</span></div><p>Ticks da conta demo conectada ao MT5, com progresso do exportador apresentado por ano.</p><dl><div><dt>Origem</dt><dd>Servidor Fusion via MT5</dd></div><div><dt>Uso</dt><dd>Bid/Ask, spread e timing reais</dd></div><div><dt>Estado atual</dt><dd>__FUSION_STATUS__</dd></div></dl><small class="source-open">Abrir histórico anual →</small></a></div></section>
    <section class="metric-grid"><article class="panel metric"><span>Progresso total</span><strong id="total-progress">—</strong><small id="collection-range">—</small></article><article class="panel metric"><span>Anos equivalentes baixados</span><strong id="equivalent-years">—</strong><small id="hours-complete">—</small></article><article class="panel metric"><span>Anos 100% completos</span><strong id="complete-years">—</strong><small id="years-total">—</small></article><article class="panel metric"><span>Previsão de conclusão</span><strong id="eta">—</strong><small id="rate">—</small></article></section>
    <section class="panel overall"><div class="overall-heading"><div><p class="eyebrow">Cobertura total</p><h2 id="overall-label">Carregando manifesto...</h2></div><strong id="overall-percent">0%</strong></div><div class="track track-large"><span id="overall-bar"></span></div></section>
    <section class="panel years-panel"><div class="section-heading"><div><p class="eyebrow">Linha histórica</p><h2>Progresso por ano</h2></div><p class="muted">Cada barra representa as horas disponíveis daquele ano.</p></div><div class="year-list" id="year-list"><p class="muted">Lendo os dados da coleta...</p></div></section>
    <p class="muted footnote">A tela é somente leitura e atualiza automaticamente a cada 15 segundos. Horas sem negociação confirmadas pela fonte contam como processadas.</p></main><style>
    .live-state{display:flex;align-items:center;gap:11px;padding:11px 14px;border:1px solid #273244;border-radius:9px;background:#0d131c}.live-state div{display:grid;gap:3px}.live-state small{color:var(--muted)}.state-dot{width:10px;height:10px;border-radius:50%;background:#687386;box-shadow:0 0 0 5px rgba(104,115,134,.12)}.state-dot.running{background:var(--green);box-shadow:0 0 0 5px rgba(65,211,146,.12)}.source-panel{padding:20px;margin-bottom:18px}.source-heading,.source-card-heading{display:flex;align-items:flex-start;justify-content:space-between;gap:16px}.source-heading h2{margin:0}.source-heading p:last-child{margin:7px 0 0}.source-badge,.source-status,.source-role{font-size:11px;font-weight:800;letter-spacing:.04em;text-transform:uppercase}.source-badge{padding:6px 9px;border:1px solid #354255;border-radius:999px;color:var(--muted)}.source-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-top:17px}.source-card{padding:17px;border:1px solid #28354a;border-radius:9px;background:#0c121b;color:var(--text);text-decoration:none}.source-card:hover,.source-card:focus-visible,.source-card.selected{border-color:#71809a;outline:none}.source-card.selected{box-shadow:0 0 0 1px rgba(113,128,154,.45)}.source-card.dukascopy-source{border-left:3px solid #5c7cfa}.source-card.fusion-source{border-left:3px solid var(--yellow)}.source-card-heading strong{display:block;font-size:16px}.source-card-heading>div{display:grid;gap:7px}.source-card p{margin:14px 0;color:var(--muted);font-size:13px;line-height:1.45}.source-status{width:max-content;padding:4px 7px;border:1px solid #46536a;border-radius:999px}.source-status.ready{color:var(--green);border-color:rgba(65,211,146,.45);background:rgba(65,211,146,.08)}.source-status.waiting{color:var(--yellow);border-color:rgba(246,198,103,.4);background:rgba(246,198,103,.08)}.source-role{color:#aebbd0;text-align:right}.source-card dl{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:0}.source-card dl div{min-width:0}.source-card dt{margin-bottom:4px;color:var(--muted);font-size:10px;text-transform:uppercase}.source-card dd{margin:0;color:#dce4f1;font-size:12px;line-height:1.35}.source-open{display:block;margin-top:15px;color:#c5d1e7;font-size:12px;font-weight:800}.metric-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:13px;margin-bottom:18px}.metric{min-height:132px;padding:18px;display:flex;flex-direction:column}.metric span,.metric small{color:var(--muted);font-size:12px}.metric strong{margin:auto 0 7px;font-size:28px}.overall,.years-panel{padding:20px;margin-bottom:18px}.overall-heading,.section-heading{display:flex;align-items:flex-end;justify-content:space-between;gap:18px}.overall-heading h2,.section-heading h2{margin:0}.overall-heading>strong{font-size:30px;color:var(--green)}.eyebrow{margin-bottom:7px;color:var(--lotus-info);font-size:11px;font-weight:800;letter-spacing:.08em;text-transform:uppercase}.track{height:9px;overflow:hidden;border-radius:999px;background:#202938}.track span{display:block;width:0;height:100%;border-radius:inherit;background:linear-gradient(90deg,#5c7cfa,#41d392);transition:width .4s ease}.track-large{height:13px;margin-top:18px}.year-list{display:grid;gap:9px;margin-top:19px}.year-row{display:grid;grid-template-columns:58px minmax(180px,1fr) 76px 112px;gap:13px;align-items:center;padding:9px 11px;border:1px solid #202a39;border-radius:8px;background:#0c1118}.year-row.complete{border-color:rgba(65,211,146,.25)}.year-row strong{font-variant-numeric:tabular-nums}.year-row .percent{text-align:right;color:#d8deea}.year-row small{text-align:right;color:var(--muted)}.year-row.complete .percent{color:var(--green)}.footnote{font-size:12px}@media(max-width:980px){.metric-grid{grid-template-columns:repeat(2,1fr)}.source-card dl{grid-template-columns:1fr}}@media(max-width:680px){.metric-grid,.source-grid{grid-template-columns:1fr}.live-state{width:100%}.year-row{grid-template-columns:48px 1fr 62px}.year-row small{display:none}.section-heading,.source-heading,.source-card-heading{align-items:flex-start;flex-direction:column}.source-role{text-align:left}}
    </style><script>
    const source='__SOURCE__';const number=value=>new Intl.NumberFormat('pt-BR').format(value||0);const dateTime=value=>value?new Date(value).toLocaleString('pt-BR',{timeZone:'UTC'})+' UTC':'Sem atualização';
    const duration=seconds=>{if(seconds==null)return 'Calculando';const days=Math.floor(seconds/86400),hours=Math.floor(seconds%86400/3600);return days?days+'d '+hours+'h':hours+'h'};
    function renderProgress(data){const dot=document.getElementById('state-dot');dot.classList.toggle('running',data.running);if(!data.available){const fusion=source==='fusion';document.getElementById('state-label').textContent=fusion?'Aguardando exportação':'Manifesto indisponível';document.getElementById('updated-label').textContent=fusion?'Ainda não há arquivos desta fonte':'A coleta ainda não gravou o manifesto';document.getElementById('overall-label').textContent=fusion?'Aguardando primeira exportação':'Aguardando manifesto da coleta';document.getElementById('year-list').innerHTML='<p class="muted">'+(fusion?'O histórico anual aparecerá aqui assim que o exportador Fusion gravar o primeiro intervalo.':'O histórico anual aparecerá aqui assim que a coleta Dukascopy registrar o primeiro intervalo.')+'</p>';return}document.getElementById('total-progress').textContent=data.progress_pct.toFixed(2)+'%';document.getElementById('collection-range').textContent=data.requested_start+' até '+data.requested_end;document.getElementById('equivalent-years').textContent=data.equivalent_years.toFixed(2)+' anos';document.getElementById('hours-complete').textContent=number(data.completed_hours)+' horas processadas';document.getElementById('complete-years').textContent=data.complete_years;document.getElementById('years-total').textContent='de '+data.total_years+' anos no intervalo';document.getElementById('eta').textContent=duration(data.eta_seconds);document.getElementById('rate').textContent=data.rate_hours_per_minute?data.rate_hours_per_minute.toFixed(2)+' horas/min':'Taxa será calculada';document.getElementById('overall-percent').textContent=data.progress_pct.toFixed(2)+'%';document.getElementById('overall-label').textContent=number(data.completed_hours)+' de '+number(data.expected_hours)+' horas';document.getElementById('overall-bar').style.width=data.progress_pct+'%';document.getElementById('state-label').textContent=data.running?'Download em andamento':'Coleta sem atividade recente';document.getElementById('updated-label').textContent='Última gravação: '+dateTime(data.updated_at);document.getElementById('year-list').innerHTML=[...data.years].reverse().map(year=>`<div class="year-row ${year.complete?'complete':''}"><strong>${year.year}</strong><div class="track"><span style="width:${year.progress_pct}%"></span></div><span class="percent">${year.progress_pct.toFixed(1)}%</span><small>${number(year.completed_hours)} / ${number(year.expected_hours)} h</small></div>`).join('')}
    async function refreshProgress(){const response=await fetch('/api/history/progress?source=__SOURCE__');const data=await response.json();if(!response.ok)throw Error(data.detail||'Falha ao consultar o progresso.');renderProgress(data)}refreshProgress().catch(error=>document.getElementById('overall-label').textContent=error.message);setInterval(()=>refreshProgress().catch(()=>{}),15000);
    </script>"""
    if source == "fusion":
        page = page.replace(
            "__SOURCE_NAME__: acompanhamento anual dos ticks XAUUSD.",
            "Fusion Markets · MT5: candles XAUUSD M1/M5 publicados e progresso dos ticks.",
        )
        page = page.replace(
            '<section class="metric-grid">',
            '<section class="panel fusion-release" style="padding:20px;margin-bottom:18px">'
            '<p class="eyebrow">Candles publicados</p><h2>Fusion M1 e M5</h2>'
            '<p id="fusion-candles-status" class="muted" role="status">Consultando releases...</p>'
            '<a href="/bots?workspace=1&amp;source=fusion&amp;resolution=1m">Abrir gráfico e estudo ZigZag M1 →</a>'
            '</section><section class="metric-grid">',
        )
        page = page.replace(
            'refreshProgress().catch(error=>document.getElementById',
            "fetch('/api/research/fusion/status').then(response=>response.json()).then(data=>{const m1=data.M1,m5=data.M5;document.getElementById('fusion-candles-status').textContent='M1: '+(m1.available?number(m1.rows)+' candles · '+m1.first_server_time+' a '+m1.last_server_time:'indisponível')+' · M5: '+(m5.available?number(m5.rows)+' candles':'indisponível')+' · horários do servidor Fusion.'}).catch(()=>{document.getElementById('fusion-candles-status').textContent='Não foi possível consultar os releases Fusion.'});refreshProgress().catch(error=>document.getElementById",
        )
    return _page("2Lotus | Histórico do ouro", page.replace("__SOURCE_NAME__", source_name).replace("__DUKASCOPY_SELECTED__", "selected" if source == "dukascopy" else "").replace("__FUSION_SELECTED__", "selected" if source == "fusion" else "").replace("__FUSION_STATUS__", source_status if source == "fusion" else "Abrir acompanhamento").replace("__SOURCE__", source), active_nav="history")


def render_operations_page() -> HTMLResponse:
    return _page("2Lotus | Saúde operacional", """<main><header class="header"><div><a class="brand brand-compact" href="/bots"><img src="/static/brand/lotus-icon.png" alt="2Lotus"></a><h1>Saúde operacional</h1><p class="muted">Heartbeat, mercado e snapshots das estratégias shadow.</p></div><div class="actions"><a href="/bots">Estratégias</a></div></header><section class="panel table"><table><thead><tr><th>Estratégia</th><th>Status</th><th>Último sucesso</th><th>Candle</th><th>Resposta / erro</th><th>Latência</th><th>Snapshot</th></tr></thead><tbody id="rows"><tr><td colspan="7" class="muted">Carregando...</td></tr></tbody></table></section><p id="updated" class="muted"></p></main><style>.actions a{color:var(--text)}.table{padding:0;overflow:auto}table{width:100%;min-width:950px;border-collapse:collapse}th,td{padding:15px;text-align:left;border-bottom:1px solid #292929}th{color:var(--muted);font-size:12px;text-transform:uppercase}.badge{padding:5px 8px;border-radius:999px;background:#222;font-size:11px}.healthy{color:var(--green)}.delayed,.market_closed{color:var(--yellow)}.stale{color:var(--red)}</style><script>const date=v=>v?new Date(v).toLocaleString('pt-BR',{timeZone:'UTC'})+' UTC':'-';fetch('/api/operations').then(r=>{if(!r.ok)throw Error('Falha ao carregar saúde.');return r.json()}).then(data=>{document.getElementById('rows').innerHTML=data.bots.map(b=>`<tr><td><strong>${escapeHtml(b.name)}</strong><br><small class="muted">${escapeHtml(b.bot_id)}</small></td><td><span class="badge ${escapeHtml(b.status)}">${escapeHtml(b.status.replaceAll('_',' '))}</span><br><small class="muted">${b.consecutive_errors||0} erros</small></td><td>${date(b.last_success_at_utc||b.last_request_at_utc)}<br><small class="muted">tentativa ${date(b.last_attempt_at_utc)}</small></td><td>${date(b.last_candle_at_utc)}<br><small class="muted">atraso ${b.market_lag_seconds==null?'-':Math.round(b.market_lag_seconds/60)+' min'}</small></td><td>${escapeHtml(b.last_error_code||b.last_action||'-')}<br><small class="muted">${escapeHtml(b.last_error||b.last_reason||'')}</small></td><td>${b.last_latency_ms==null?'-':Number(b.last_latency_ms).toFixed(0)+' ms'}</td><td>${date(b.snapshot_updated_at_utc)}<br><small class="muted">dados até ${date(b.market_data_through_utc)}</small></td></tr>`).join('');document.getElementById('updated').textContent='Atualizado em '+date(data.updated_at_utc)}).catch(e=>document.getElementById('rows').textContent=e.message)</script>""")


def render_account_page(bots: list[BotCatalogItem] | None = None) -> HTMLResponse:
    strategies = "".join(
        f'<div class="strategy-row"><div><strong>{escape(bot.name)}</strong>{_subtitle_html(bot, "account-strategy-subtitle")}</div><span>{escape(bot.symbol)} · {escape(bot.timeframe)}</span><small>Ativa</small></div>'
        for bot in (bots or [])
    ) or '<p class="muted">Nenhuma estratégia ativa.</p>'
    return _page("2Lotus | Conta", f"""<main><header class="header"><div><a class="brand brand-compact" href="/bots"><img src="/static/brand/lotus-icon.png" alt="2Lotus"></a><p class="eyebrow">MetaTrader 5</p><h1>Conta</h1><p class="muted">Dados financeiros e identidade da conta conectada.</p></div><span id="connection" class="status waiting"><i></i>Aguardando conexão</span></header><section id="identity-warning" class="warning" hidden></section><section class="balance-grid"><article class="balance panel"><p class="muted">Saldo atual</p><strong id="balance">—</strong><small id="equity">Equity —</small></article><article class="balance panel"><p class="muted">Saldo inicial</p><strong id="initial-balance">—</strong><small>Capital configurado</small></article></section><section class="profit-grid"><article class="panel"><p class="muted">Lucro flutuante</p><strong id="floating">—</strong><small>Posições abertas agora</small></article><article class="panel"><p class="muted">Realizado hoje</p><strong id="realized">—</strong><small id="profit-day">Dia da corretora</small></article></section><section class="panel details"><h2>Identificação</h2><dl><div><dt>ID da conta</dt><dd id="account-id">—</dd></div><div><dt>Corretora</dt><dd id="broker">—</dd></div><div><dt>Servidor</dt><dd id="server">—</dd></div><div><dt>Tipo</dt><dd id="trade-mode">—</dd></div><div><dt>Alavancagem</dt><dd id="leverage">—</dd></div><div><dt>Margem livre</dt><dd id="margin-free">—</dd></div></dl></section><section class="panel strategies"><div class="section-heading"><div><p class="eyebrow">Operação</p><h2>Estratégias ativas</h2></div><span>{len(bots or [])} estratégias</span></div><div class="strategy-list">{strategies}</div></section><p id="updated" class="muted">Buscando dados do terminal…</p></main><style>
    .eyebrow{{margin-bottom:7px;color:var(--lotus-info);font-size:11px;font-weight:800;letter-spacing:.08em;text-transform:uppercase}}.status{{display:inline-flex;align-items:center;gap:9px;padding:9px 12px;border:1px solid #293342;border-radius:999px;color:var(--muted);font-size:12px;font-weight:800;text-transform:uppercase}}.status i{{width:9px;height:9px;border-radius:50%;background:#687386}}.status.online{{color:var(--green)}}.status.online i{{background:var(--green)}}.status.delayed{{color:var(--yellow)}}.status.delayed i{{background:var(--yellow)}}.status.offline{{color:var(--red)}}.status.offline i{{background:var(--red)}}.warning{{padding:14px 16px;margin-bottom:18px;border:1px solid rgba(246,198,103,.55);border-radius:9px;color:var(--yellow);background:rgba(246,198,103,.08)}}.balance-grid,.profit-grid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin-bottom:16px}}.balance{{padding:25px}}.balance p{{margin-bottom:10px}}.balance strong{{display:block;font-size:46px;line-height:1.05;font-variant-numeric:tabular-nums}}.balance small,.profit-grid small{{display:block;margin-top:9px;color:var(--muted)}}.profit-grid article{{padding:21px}}.profit-grid strong{{font-size:28px;font-variant-numeric:tabular-nums}}.positive{{color:var(--green)}}.negative{{color:var(--red)}}.neutral{{color:var(--yellow)}}.details,.strategies{{padding:22px;margin-bottom:16px}}.details h2{{margin-bottom:18px}}.details dl{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:1px;margin:0;background:#292929}}.details dl div{{padding:16px;background:var(--panel)}}dt{{margin-bottom:7px;color:var(--muted);font-size:11px;text-transform:uppercase}}dd{{margin:0;font-weight:750;overflow-wrap:anywhere}}.section-heading{{display:flex;align-items:flex-end;justify-content:space-between;gap:16px;margin-bottom:16px}}.section-heading h2{{margin:0}}.section-heading span{{color:var(--muted);font-size:12px}}.strategy-list{{display:grid;gap:8px}}.strategy-row{{display:grid;grid-template-columns:minmax(0,1fr) auto 58px;align-items:center;gap:14px;padding:13px 14px;border:1px solid #292929;border-radius:8px;color:var(--text);text-decoration:none;background:#0f0f0f}}.strategy-row:hover{{border-color:#59677a}}.strategy-row span,.strategy-row small,.account-strategy-subtitle{{color:var(--muted);font-size:12px}}.strategy-row small{{color:var(--green);text-align:right}}.account-strategy-subtitle{{margin:4px 0 0}}@media(max-width:720px){{.balance-grid,.profit-grid,.details dl{{grid-template-columns:1fr}}.balance strong{{font-size:36px}}.strategy-row{{grid-template-columns:1fr auto}}.strategy-row span{{display:none}}}}
    </style><script>
    const money=(value,currency)=>new Intl.NumberFormat('pt-BR',{{style:'currency',currency:currency||'USD'}}).format(Number(value||0));const tone=value=>Number(value)>0?'positive':Number(value)<0?'negative':'neutral';const put=(id,value)=>document.getElementById(id).textContent=value;function render(data){{const status=document.getElementById('connection');status.className='status '+data.status;status.innerHTML='<i></i>'+({{online:'Online',delayed:'Dados atrasados',offline:'Offline',waiting:'Aguardando conexão'}}[data.status]||data.status);put('initial-balance',money(data.initial_balance,'USD'));const warning=document.getElementById('identity-warning');if(!data.available){{warning.hidden=false;warning.textContent='Nenhum snapshot recebido do MT5. Conta esperada: '+(data.expected_account_id||'não configurada')+' · '+(data.expected_server||'servidor não configurado');return}}const a=data.account,currency=a.currency||'USD';put('initial-balance',money(data.initial_balance,currency));put('balance',money(a.balance,currency));put('equity','Equity '+money(a.equity,currency));for(const [id,value] of [['floating',a.floating_profit],['realized',a.realized_profit_today]]){{const el=document.getElementById(id);el.textContent=value==null?'Aguardando EA atualizado':money(value,currency);el.className=value==null?'':tone(value)}}put('profit-day',a.profit_day?'Dia da corretora · '+new Date(a.profit_day+'T12:00:00Z').toLocaleDateString('pt-BR'):'Dia da corretora');put('account-id',a.account_id||'Aguardando EA atualizado');put('broker',a.broker||'Aguardando EA atualizado');put('server',a.server||'—');put('trade-mode',({{demo:'Demo',contest:'Concurso',real:'Real',unknown:'Desconhecida'}}[a.trade_mode]||a.trade_mode));put('leverage',a.leverage?'1:'+a.leverage:'—');put('margin-free',money(a.margin_free,currency));warning.hidden=data.identity_matches!==false;if(!warning.hidden)warning.textContent='A conta conectada não corresponde ao ID ou servidor configurado no ambiente.';put('updated','Última leitura: '+new Date(data.observed_at_utc).toLocaleString('pt-BR',{{timeZone:'UTC'}})+' UTC · há '+Math.round(data.age_seconds)+' s')}}async function refresh(){{try{{const response=await fetch('/api/account');const data=await response.json();if(!response.ok)throw Error(data.detail||'Falha ao consultar a conta.');render(data)}}catch(error){{put('updated',error.message)}}}}refresh();setInterval(refresh,10000);
    </script>""", active_nav="account")


def render_comparison_page(bots: list[BotCatalogItem]) -> HTMLResponse:
    ordered_bots = sorted(bots, key=lambda bot: (strategy_presentation_order(bot.strategy_profile), bot.name.casefold()))
    rows = "".join(
        f'''<tr data-bot-id="{escape(bot.id)}"><td><strong>{escape(bot.name)}</strong>{f'<small>{escape(bot.subtitle)}</small>' if bot.subtitle else ''}</td><td>{escape(bot.symbol)} · {escape(bot.timeframe)}</td><td data-field="trades">-</td><td data-field="open">-</td><td data-field="win-rate">-</td><td data-field="profit-factor">-</td><td data-field="expectancy-r">-</td><td data-field="drawdown-r">-</td><td data-field="net-pnl">-</td><td data-field="latest">-</td></tr>'''
        for bot in ordered_bots
    ) or '<tr><td colspan="10" class="muted">Nenhum bot foi cadastrado.</td></tr>'
    return _page("2Lotus | Comparação", f"""<main>
    <section class="comparison-toolbar panel"><div><p class="eyebrow">Período analisado</p><div class="period-buttons" role="group" aria-label="Período da comparação"><button type="button" data-days="90">90 dias</button><button type="button" data-days="365" class="selected">1 ano</button><button type="button" data-days="1095">3 anos</button></div></div><div><p class="muted" id="comparison-status">Carregando resultados históricos...</p><p class="muted" id="updated-at">Carregando...</p></div></section>
    <section class="summary-grid"><article class="panel"><p class="muted">Estratégias ativas</p><strong>{len(bots)}</strong></article><article class="panel"><p class="muted">Mercado acompanhado</p><strong>XAUUSD · M5</strong></article><article class="panel"><p class="muted">Risco comparável</p><strong class="green">1% Risk/Trade</strong></article></section>
    <section class="panel table-panel"><div class="table-wrap"><table><thead><tr><th>Estratégia</th><th>Mercado</th><th>Fechados</th><th>Abertos</th><th>Win rate</th><th>Profit factor</th><th>Expectativa (R)</th><th>Drawdown (R)</th><th>PnL líquido</th><th>Último evento</th></tr></thead><tbody>{rows}</tbody></table></div></section>
    <p class="muted note">As posições são isoladas por bot e variante. Um sinal de uma estratégia não bloqueia nem encerra posições das demais.</p></main><style>
    .actions {{ display:flex; justify-content:flex-end; align-items:flex-start; gap:14px; flex-wrap:wrap; }} .actions a {{ color:var(--text); }} .actions p {{ width:100%; text-align:right; }} .comparison-toolbar {{ display:flex; justify-content:space-between; align-items:center; gap:18px; padding:18px; margin-bottom:18px; }} .comparison-toolbar p {{ margin:0; }} .eyebrow {{ margin-bottom:9px!important; color:var(--green); font-size:11px; font-weight:800; letter-spacing:.06em; text-transform:uppercase; }} .period-buttons {{ display:flex; gap:7px; }} .period-buttons button {{ padding:8px 12px; border:1px solid #2a3547; border-radius:7px; color:var(--muted); background:#0b1017; font-weight:700; }} .period-buttons button.selected {{ color:#07110d; border-color:var(--green); background:var(--green); }} .summary-grid {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:14px; margin-bottom:18px; }} .summary-grid .panel {{ padding:18px; }} .summary-grid strong {{ display:block; font-size:24px; }} .table-panel {{ padding:0; overflow:hidden; }} .table-wrap {{ overflow-x:auto; }} table {{ width:100%; border-collapse:collapse; min-width:980px; }} th,td {{ padding:16px; text-align:left; border-bottom:1px solid rgba(255,255,255,.16); }} th {{ color:var(--muted); font-size:12px; text-transform:uppercase; letter-spacing:.05em; }} td a {{ color:var(--text); font-weight:700; }} td small {{ display:block; margin-top:5px; color:var(--muted); }} .green {{ color:var(--green); }} .red {{ color:var(--red); }} .yellow {{ color:var(--yellow); }} .status-missing {{ color:var(--yellow); font-size:11px; font-weight:700; }} .comparison-missing td {{ color:var(--muted); }} .comparison-missing td:first-child a {{ color:var(--yellow); }} .note {{ margin:18px 2px 0; }} @media(max-width:720px) {{ .comparison-toolbar {{ align-items:flex-start; flex-direction:column; }} .summary-grid {{ grid-template-columns:1fr; }} }}
    </style><script>
    const money = value => new Intl.NumberFormat('pt-BR', {{style:'currency',currency:'USD'}}).format(value || 0);
    const date = value => value ? new Date(value).toLocaleString('pt-BR', {{timeZone:'UTC'}}) + ' UTC' : 'Sem eventos';
    const color = value => value > 0 ? 'green' : value < 0 ? 'red' : 'yellow';
    let comparisonDays = 365;
    async function loadComparison() {{
      document.getElementById('comparison-status').textContent = 'Carregando resultados históricos...';
      const response = await fetch(`/api/equity-comparison?symbol=XAUUSD&days=${{comparisonDays}}&mode=normalized`);
      if (!response.ok) throw new Error('Não foi possível carregar a comparação.');
      const data = await response.json();
      document.querySelectorAll('[data-bot-id]').forEach(row => row.querySelectorAll('[data-field]').forEach(cell => cell.textContent = '-'));
      const missingIds = new Set(data.missing_bot_ids);
      document.querySelectorAll('[data-bot-id]').forEach(row => {{
        const missing = missingIds.has(row.dataset.botId);
        row.classList.toggle('comparison-missing', missing);
        const label = row.querySelector('.status-missing');
        if (missing && !label) row.querySelector('td:first-child').insertAdjacentHTML('beforeend', '<small class="status-missing">Replay causal pendente</small>');
        row.querySelector('[data-field="latest"]').textContent = missing ? 'Replay pendente' : '-';
      }});
      for (const bot of data.series) {{
        const row = document.querySelector(`[data-bot-id="${{bot.bot_id}}"]`);
        if (!row) continue;
        const summary = bot.summary;
        row.querySelector('[data-field="trades"]').textContent = summary.trades_count;
        row.querySelector('[data-field="open"]').textContent = summary.open_positions;
        row.querySelector('[data-field="win-rate"]').textContent = summary.win_rate_pct.toFixed(2) + '%';
        row.querySelector('[data-field="profit-factor"]').textContent = summary.profit_factor.toFixed(2);
        row.querySelector('[data-field="expectancy-r"]').textContent = bot.expectancy_r.toFixed(3) + 'R';
        row.querySelector('[data-field="drawdown-r"]').textContent = bot.max_drawdown_r.toFixed(2) + 'R';
        const pnl = row.querySelector('[data-field="net-pnl"]'); pnl.textContent = money(summary.net_pnl); pnl.className = color(summary.net_pnl);
        const latest = bot.points.length ? bot.points[bot.points.length - 1].day + 'T00:00:00Z' : null;
        row.querySelector('[data-field="latest"]').textContent = date(latest);
      }}
      const missing = data.missing_bot_ids.length;
      document.getElementById('comparison-status').textContent = data.series.length + ' estratégias carregadas' + (missing ? ' · ' + missing + ' sem histórico neste período' : '');
      document.getElementById('updated-at').textContent = 'Atualizado em ' + date(data.updated_at_utc);
    }}
    document.querySelectorAll('[data-days]').forEach(button => button.addEventListener('click', () => {{
      document.querySelectorAll('[data-days]').forEach(item => item.classList.remove('selected'));
      button.classList.add('selected'); comparisonDays = Number(button.dataset.days);
      loadComparison().catch(showComparisonError);
    }}));
    function showComparisonError(error) {{ document.getElementById('comparison-status').textContent = error.message; document.getElementById('updated-at').textContent = 'Falha ao atualizar'; }}
    loadComparison().catch(showComparisonError);
    </script>""")
