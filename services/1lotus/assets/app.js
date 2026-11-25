(() => {
  const panels = {
    history: {route:'/historico', title:'Histórico', description:'Acompanhe os dados históricos do ouro.', sections:[['history','Histórico','/p/history/']]},
    operations: {route:'/operacao', title:'Operation Core', description:'Conta, operações e telemetria do ambiente local.', sections:[['overview','Visão geral','/p/operations/overview?workspace=1'],['account','Conta','/p/operations/account?workspace=1'],['server','Servidor','/p/operations/server?workspace=1'],['bots','Estratégias ativas','/p/operations/bots?workspace=1'],['trades','Operações','/p/operations/trades?workspace=1'],['health','Saúde','/p/operations/operations?workspace=1'],['security','Segurança','/p/operations/security?workspace=1']]},
    runner: {route:'/runner', title:'Runner', description:'Estado do runner, decisões e métricas.', sections:[['overview','Visão geral','/p/runner/']]},
    strategies: {route:'/estrategias', title:'Unificação', description:'Roteadores e composição das estratégias promovidas.', sections:[['catalog','Composição','/p/strategies/strategies']]},
    promoted: {route:'/promovidas', title:'Estratégias promovidas', description:'Explore estratégias individuais aprovadas, compare versões e consulte simulações disponíveis.', sections:[['strategies','Estratégias','/p/promoted/strategies'],['comparison','Comparar estratégias','/p/promoted/compare'],['simulator','Simulador de crescimento','/p/promoted/growth-simulator']]},
    research: {route:'/pesquisa', title:'Estratégias', description:'Pesquise estratégias, compare resultados e explore novas candidatas.', sections:[['strategies','Estratégias','/p/research/bots?workspace=1'],['comparison','Comparar estratégias','/p/research/compare?workspace=1'],['simulator','Simulador de crescimento','/p/research/growth-simulator?workspace=1']]},
    docs: {route:'/documentacao', title:'Documentação', description:'Arquitetura, operação e decisões do projeto.', sections:[['docs','Documentação','/p/docs/']]},
  };
  const routeToPanel = Object.entries(panels).find(([, value]) => value.route === location.pathname)?.[0] || 'history';
  const panel = panels[routeToPanel];
  const params = new URLSearchParams(location.search);
  const selected = panel.sections.find(([key]) => key === params.get('section')) || panel.sections[0];
  const frame = document.getElementById('content-frame');
  frame.classList.add('auto-height-frame');
  const sectionNav = document.getElementById('section-nav');
  const sectionSelect = document.getElementById('section-select');
  const state = document.getElementById('service-state');
  const sidebar = document.getElementById('sidebar');
  const scrim = document.getElementById('scrim');
  const menuButton = document.getElementById('menu-button');
  const setState = (message, error = false) => {
    state.classList.toggle('error', error);
    state.lastElementChild.textContent = message;
  };
  const setMenu = open => {
    sidebar.classList.toggle('open', open);
    scrim.classList.toggle('open', open);
    menuButton.setAttribute('aria-expanded', String(open));
    menuButton.setAttribute('aria-label', open ? 'Fechar menu' : 'Abrir menu');
  };
  menuButton.addEventListener('click', () => setMenu(!sidebar.classList.contains('open')));
  scrim.addEventListener('click', () => setMenu(false));
  document.addEventListener('keydown', event => { if (event.key === 'Escape') setMenu(false); });
  document.querySelectorAll('.main-nav a').forEach(link => {
    if (link.dataset.panel === routeToPanel) link.setAttribute('aria-current', 'page');
  });
  document.getElementById('page-title').textContent = panel.title;
  document.getElementById('breadcrumb-title').textContent = panel.title;
  document.getElementById('page-description').textContent = panel.description;
  document.title = `${panel.title} · 7lotus`;
  for (const [key, label] of panel.sections) {
    const button = document.createElement('button');
    button.type = 'button';
    button.dataset.section = key;
    button.textContent = label;
    button.addEventListener('click', () => show(key));
    sectionNav.append(button);
    const option = document.createElement('option');
    option.value = key;
    option.textContent = label;
    sectionSelect.append(option);
  }
  if (routeToPanel === 'history' || routeToPanel === 'strategies') {
    document.querySelector('.section-bar').hidden = true;
    document.querySelector('.page-heading').hidden = true;
  }
  sectionSelect.addEventListener('change', () => show(sectionSelect.value));
  function show(key, updateUrl = true) {
    const section = panel.sections.find(([id]) => id === key) || panel.sections[0];
    sectionNav.querySelectorAll('button').forEach(button => {
      if (button.dataset.section === section[0]) button.setAttribute('aria-current', 'page');
      else button.removeAttribute('aria-current');
    });
    sectionSelect.value = section[0];
    frame.title = `${panel.title}: ${section[1]}`;
    setState('Carregando');
    if (frame.getAttribute('src') !== section[2]) frame.setAttribute('src', section[2]);
    if (updateUrl) {
      const url = new URL(location.href);
      if (section[0] === panel.sections[0][0]) url.searchParams.delete('section');
      else url.searchParams.set('section', section[0]);
      history.pushState({section: section[0]}, '', url);
    }
  }
  frame.addEventListener('load', () => {
    try {
      const path = frame.contentWindow.location.pathname;
      const text = frame.contentDocument.body?.textContent || '';
      if (path.endsWith('/login')) setState('Acesso necessário');
      else if (text.startsWith('O serviço ') && text.includes('indisponível')) setState('Serviço indisponível', true);
      else setState('Conectado');
      fitFrameContent();
    } catch (_) { setState('Conteúdo carregado'); }
  });
  let frameResizeObserver;
  let frameMutationObserver;
  function fitFrameContent() {
    try {
      const doc = frame.contentDocument;
      if (!doc?.body) return;
      frameResizeObserver?.disconnect();
      frameMutationObserver?.disconnect();
      const style = doc.createElement('style');
      style.textContent = 'html,body{height:auto!important;min-height:0!important;overflow-y:hidden!important}.app-shell,.app-workspace,.app-content{height:auto!important;min-height:0!important;max-height:none!important;overflow-y:visible!important}';
      doc.head.append(style);
      const fit = () => requestAnimationFrame(() => {
        const height = Math.max(500, doc.documentElement.scrollHeight, doc.body.scrollHeight);
        if (Math.abs(frame.getBoundingClientRect().height - height) > 8) frame.style.height = `${height}px`;
      });
      frameResizeObserver = new ResizeObserver(fit);
      frameResizeObserver.observe(doc.body);
      frameMutationObserver = new MutationObserver(fit);
      frameMutationObserver.observe(doc.body, {subtree:true, childList:true, attributes:true, characterData:true});
      frame.contentWindow.addEventListener('resize', fit);
      [100, 500, 1500, 3500].forEach(delay => frame.contentWindow.setTimeout(fit, delay));
      fit();
    } catch (_) { /* A failed/redirected frame keeps its default height. */ }
  }
  window.addEventListener('popstate', () => {
    const key = new URLSearchParams(location.search).get('section');
    show(key, false);
  });
  show(selected[0], false);
})();
