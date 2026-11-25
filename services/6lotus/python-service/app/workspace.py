"""Unified local navigation for independent Gold Lotus panels."""

from html import escape

from fastapi.responses import HTMLResponse


PANELS = (
    ("Histórico", 7771, "/"),
    ("Operation Core", 7772, "/workspace"),
    ("Runner", 7773, "/"),
    ("Estratégias", 7774, "/workspace"),
    ("Pesquisa", 7775, "/workspace"),
    ("Documentação", 7777, "/"),
)

PANEL_ICONS = {
    7771: '<svg viewBox="0 0 24 24" aria-hidden="true"><ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v6c0 1.7 3.6 3 8 3s8-1.3 8-3V5M4 11v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"/></svg>',
    7772: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 20 6v5c0 5-3.4 8-8 10-4.6-2-8-5-8-10V6l8-3Z"/><path d="m9 12 2 2 4-4"/></svg>',
    7773: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m8 5 11 7-11 7V5Z"/></svg>',
    7774: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m12 3 9 5-9 5-9-5 9-5Z"/><path d="m3 12 9 5 9-5M3 16l9 5 9-5"/></svg>',
    7775: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></svg>',
    7777: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v17H6.5A2.5 2.5 0 0 0 4 22V5.5ZM4 18a2.5 2.5 0 0 1 2.5-2.5H20"/></svg>',
}



def render_workspace(title: str, active_port: int, sections: tuple[tuple[str, str, str], ...]) -> HTMLResponse:
    """Show one internal section at a time while retaining its original API and scripts."""
    if not sections:
        raise ValueError("workspace requires at least one section")
    menu = "".join(
        f'<a class="panel-link{" active" if port == active_port else ""}" '
        f'data-port="{port}" data-path="{path}" href="{path if port == active_port else "#"}"'
        f'{" aria-current=\"page\"" if port == active_port else ""}>{PANEL_ICONS[port]}<span>{escape(label)}</span></a>'
        for label, port, path in PANELS
    )
    tabs = "".join(
        f'<button type="button" role="tab" id="tab-{escape(key)}" '
        f'aria-controls="section-frame" aria-selected="{"true" if index == 0 else "false"}" '
        f'class="section-tab{" active" if index == 0 else ""}" '
        f'data-section="{escape(key)}" data-src="{escape(path)}">{escape(label)}</button>'
        for index, (key, label, path) in enumerate(sections)
    )
    choices = "".join(
        f'<option value="{escape(key)}">{escape(label)}</option>'
        for key, label, _ in sections
    )
    logout = '<form method="post" action="/logout"><button type="submit">Sair</button></form>' if active_port in {7772, 7775} else ""
    html = """<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="dark"><title>__TITLE__ | Gold Lotus</title>
<style>
:root{color-scheme:dark;--lotus-bg:#07090d;--lotus-sidebar:#0a0e14;--lotus-surface:#0f141c;--lotus-surface-raised:#151c26;--lotus-border:#283242;--lotus-text:#edf2f7;--lotus-muted:#9ba9ba;--lotus-accent:#43d398;--lotus-accent-surface:#1b2634;--lotus-warning:#f6c667;--lotus-danger:#ff6b81;--lotus-info:#64b5ff;--lotus-space-1:4px;--lotus-space-2:8px;--lotus-space-3:12px;--lotus-space-4:16px;--lotus-space-6:24px;--lotus-space-8:32px;--lotus-radius-control:6px;--lotus-radius-card:8px;--lotus-radius-surface:12px;--lotus-sidebar-width:248px;--lotus-topbar-height:64px;--lotus-content-max:1360px;--lotus-control-target:40px;--lotus-navigation-target:44px;--lotus-font-family:Inter,ui-sans-serif,system-ui,sans-serif;--bg:var(--lotus-bg);--side:var(--lotus-sidebar);--surface:var(--lotus-surface);--line:var(--lotus-border);--text:var(--lotus-text);--muted:var(--lotus-muted);--accent:var(--lotus-accent)}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--text);font:14px var(--lotus-font-family)}
:where(a,button,input,select,textarea,[tabindex]):focus-visible{outline:2px solid var(--lotus-accent);outline-offset:2px}:where(time,output,[data-numeric]){font-variant-numeric:tabular-nums}
button{font:inherit;cursor:pointer}.shell{min-height:100vh;display:grid;grid-template-columns:var(--lotus-sidebar-width) minmax(0,1fr)}
.sidebar{position:sticky;top:0;z-index:20;display:flex;flex-direction:column;height:100vh;padding:var(--lotus-space-6) var(--lotus-space-4);background:var(--side);border-right:1px solid var(--line)}
.brand{display:flex;align-items:center;gap:11px;min-height:54px;padding:0 10px;font-size:13px;font-weight:800;letter-spacing:.13em}.brand-mark{display:block;width:38px;height:38px;object-fit:contain;filter:brightness(0) invert(1)}
.workspace-label{padding:14px 12px;margin:12px 0 14px;border-top:1px solid var(--line);color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.08em}.workspace-label strong{display:block;margin-top:6px;color:var(--text);font-size:13px;letter-spacing:0;text-transform:none}
.panel-nav{display:grid;gap:5px}.panel-link svg{width:19px;height:19px;flex:none;fill:none;stroke:currentColor;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}.panel-link span{min-width:0}.panel-link{display:flex;align-items:center;min-height:var(--lotus-navigation-target);padding:0 12px;border:1px solid transparent;border-radius:8px;color:var(--lotus-muted);font-size:13px;font-weight:650;text-decoration:none;transition:background .16s ease,border-color .16s ease,color .16s ease}.panel-link:hover,.panel-link:focus-visible{background:rgba(255,255,255,.045);color:#fff}.panel-link.active{background:var(--lotus-accent-surface);color:#fff;box-shadow:inset 3px 0 0 var(--lotus-accent)}
.sidebar form{margin-top:auto;padding:var(--lotus-space-4) 12px 0;border-top:1px solid var(--line)}.sidebar form button{padding:0;border:0;background:none;color:var(--muted)}.sidebar form button:hover{color:var(--text)}
.workspace{min-width:0}.topbar{position:sticky;top:0;z-index:10;display:flex;align-items:center;gap:14px;height:var(--lotus-topbar-height);padding:0 var(--lotus-space-6);border-bottom:1px solid var(--line);background:rgba(10,14,20,.94)}.topbar span{display:block;color:var(--muted);font-size:11px}.topbar strong{display:block;margin-top:2px;font-size:15px}.topbar .mode{margin-left:auto;padding:6px 9px;border:1px solid #27795b;border-radius:999px;color:var(--accent);font-size:10px;font-weight:800;letter-spacing:.08em}.menu-toggle{display:none;width:var(--lotus-control-target);height:var(--lotus-control-target);border:1px solid var(--line);border-radius:6px;background:var(--surface);color:var(--text);font-size:21px}
main{width:100%;max-width:var(--lotus-content-max);margin:auto;padding:var(--lotus-space-6)}.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
.section-select{display:none}.section-tabs{display:flex;gap:6px;flex-wrap:wrap;margin:0 0 18px;padding:0 0 8px;border-bottom:1px solid var(--line)}.section-tab{flex:none;padding:10px 13px;border:1px solid transparent;border-radius:var(--lotus-radius-control);background:transparent;color:var(--muted);font-size:13px;font-weight:650;white-space:nowrap}.section-tab:hover,.section-tab:focus-visible{color:var(--text);background:#121924}.section-tab.active{border-color:var(--lotus-accent);background:var(--lotus-accent-surface);color:var(--lotus-text)}
.section-surface{min-width:0;overflow:hidden;border:1px solid var(--line);border-radius:12px;background:var(--surface)}.section-frame{display:block;width:100%;height:calc(100vh - 145px);min-height:600px;border:0;background:var(--bg)}
.overlay{display:none}@media(max-width:860px){.shell{display:block}.sidebar{position:fixed;inset:0 auto 0 0;transform:translateX(-100%);width:min(280px,85vw);transition:transform .2s ease}.sidebar.open{transform:none}.overlay.open{display:block;position:fixed;inset:0;z-index:19;background:#000a}.menu-toggle{display:grid;place-items:center}.topbar{height:60px;padding:0 16px}main{padding:var(--lotus-space-4)}.section-frame{height:calc(100vh - 135px);min-height:500px}}@media(max-width:600px){.section-tabs{display:none}.section-select{display:grid;gap:6px;margin-bottom:16px;color:var(--muted);font-size:12px;font-weight:700}.section-select select{width:100%;padding:11px 12px;border:1px solid var(--line);border-radius:8px;background:var(--surface);color:var(--text);font:inherit}}@media(max-width:520px){.topbar .mode{display:none}.section-frame{height:calc(100vh - 130px);min-height:460px}}@media(prefers-reduced-motion:reduce){.sidebar{transition:none}}
</style></head><body><div class="shell"><aside class="sidebar" id="sidebar" aria-label="Navegação principal"><div class="brand"><img class="brand-mark" src="/static/brand/lotus-icon.png" alt=""><span>LOTUS</span></div><div class="workspace-label">Painéis locais<strong>Gold Lotus</strong></div><nav class="panel-nav" aria-label="Painéis">__MENU__</nav>__LOGOUT__</aside><div class="overlay" id="overlay"></div><div class="workspace"><header class="topbar"><button type="button" class="menu-toggle" id="menu-toggle" aria-label="Abrir menu" aria-expanded="false" aria-controls="sidebar">☰</button><div><span>Gold Lotus</span><strong>__TITLE__</strong></div><span class="mode">LOCAL</span></header><main><h1 class="sr-only">__TITLE__</h1><div class="section-tabs" role="tablist" aria-label="Seções de __TITLE__">__TABS__</div><label class="section-select">Seção<select id="section-select">__CHOICES__</select></label><section class="section-surface" aria-label="Conteúdo da seção"><span id="section-state" class="sr-only" role="status">Carregando seção…</span><iframe class="section-frame" id="section-frame" title="__FIRST_LABEL__" src="__FIRST_PATH__"></iframe></section></main></div></div>
<script>
const panels=document.querySelectorAll('[data-port]');panels.forEach(link=>{link.href=location.protocol+'//'+location.hostname+':'+link.dataset.port+link.dataset.path});
const sidebar=document.getElementById('sidebar'),overlay=document.getElementById('overlay'),toggle=document.getElementById('menu-toggle');function setMenu(open){sidebar.classList.toggle('open',open);overlay.classList.toggle('open',open);toggle.setAttribute('aria-expanded',String(open))}toggle.addEventListener('click',()=>setMenu(!sidebar.classList.contains('open')));overlay.addEventListener('click',()=>setMenu(false));document.addEventListener('keydown',event=>{if(event.key==='Escape')setMenu(false)});
const frame=document.getElementById('section-frame');let frameObserver=null;const sectionSelect=document.getElementById('section-select');const state=document.getElementById('section-state'),tabs=[...document.querySelectorAll('.section-tab')];
function select(tab,updateHash=true){tabs.forEach(item=>{const active=item===tab;item.classList.toggle('active',active);item.setAttribute('aria-selected',String(active))});frame.title=tab.textContent;sectionSelect.value=tab.dataset.section;state.textContent='Carregando seção…';if(frame.getAttribute('src')!==tab.dataset.src)frame.src=tab.dataset.src;else state.textContent='Seção pronta';if(updateHash)history.replaceState(null,'','#'+tab.dataset.section)}
tabs.forEach(tab=>tab.addEventListener('click',()=>select(tab)));sectionSelect.addEventListener('change',()=>select(tabs.find(tab=>tab.dataset.section===sectionSelect.value)));const initial=tabs.find(tab=>'#'+tab.dataset.section===location.hash);if(initial)select(initial,false);
frame.addEventListener('load',()=>{try{if(frameObserver){frameObserver.disconnect();frameObserver=null}const doc=frame.contentDocument;if(!doc){state.textContent='Conteúdo indisponível';return}const style=doc.createElement('style');style.textContent='html,body{margin:0!important;padding:0!important;overflow-x:hidden!important;min-width:0!important}.app-sidebar,.app-topbar,.app-sidebar-overlay,.sidebar,.topbar{display:none!important}.app-shell,.shell{display:block!important;min-height:0!important;grid-template-columns:none!important}.app-workspace,.workspace{margin-left:0!important;width:100%!important;min-width:0!important}.app-content{padding:0!important}.app-content>main,main{max-width:none!important;margin:0!important;padding:24px!important}@media(max-width:600px){.app-content>main,main{padding:var(--lotus-space-4)!important}.tabs{flex-wrap:wrap!important;overflow:visible!important}}.tabs{scrollbar-width:none}.tabs::-webkit-scrollbar{display:none}';doc.head.append(style);const target=doc.querySelector('main')||doc.body;const fit=()=>requestAnimationFrame(()=>{const height=Math.max(460,target.scrollHeight+48);if(Math.abs(frame.getBoundingClientRect().height-height)>8)frame.style.height=height+'px'});frameObserver=new ResizeObserver(fit);frameObserver.observe(target);fit();doc.querySelectorAll('form[action="/logout"]').forEach(form=>form.target='_top');doc.addEventListener('click',event=>{const link=event.target.closest('a[href]');if(!link)return;const url=new URL(link.href,doc.baseURI);if(url.origin!==location.origin){link.target='_blank';link.rel='noopener noreferrer';return}if(url.hash&&url.pathname===doc.location.pathname&&url.search===doc.location.search)return;url.searchParams.set('workspace','1');link.href=url.href});state.textContent='Seção pronta'}catch(error){state.textContent='Não foi possível carregar a seção'}});
</script></body></html>"""
    return HTMLResponse(
        html.replace("__TITLE__", escape(title))
        .replace("__MENU__", menu)
        .replace("__TABS__", tabs)
        .replace("__CHOICES__", choices)
        .replace("__LOGOUT__", logout)
        .replace("__FIRST_LABEL__", escape(sections[0][1]))
        .replace("__FIRST_PATH__", escape(sections[0][2]))
    )
