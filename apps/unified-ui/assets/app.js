(() => {
  const panels = {
    history: {route:'/historico', title:'Histórico', description:'Acompanhe os dados históricos do ouro.', sections:[['overview','Visão geral','/p/history/'],['dukascopy','Dukascopy','/p/history/?source=dukascopy'],['fusion','Fusion','/p/history/?source=fusion']]},
    operations: {route:'/operacao', title:'Operation Core', description:'Conta, operações e telemetria do ambiente local.', sections:[['overview','Visão geral','/p/operations/overview?workspace=1'],['account','Conta','/p/operations/account?workspace=1'],['server','Servidor','/p/operations/server?workspace=1'],['bots','Estratégias ativas','/p/operations/bots?workspace=1'],['trades','Operações','/p/operations/trades?workspace=1'],['health','Saúde','/p/operations/operations?workspace=1'],['security','Segurança','/p/operations/security?workspace=1']]},
    runner: {route:'/runner', title:'Runner', description:'Estado do runner, decisões e métricas.', sections:[['overview','Visão geral','/p/runner/']]},
    strategies: {route:'/estrategias', title:'Estratégias', description:'Catálogo, comparação e simulação das estratégias.', sections:[['catalog','Catálogo e replay','/p/strategies/strategies'],['comparison','Comparar estratégias','/p/strategies/compare'],['simulator','Simulador de crescimento','/p/strategies/growth-simulator']]},
    research: {route:'/pesquisa', title:'Pesquisa', description:'Explore estratégias, dados e resultados da pesquisa.', sections:[['strategies','Estratégias','/p/research/bots?workspace=1'],['account','Conta','/p/research/account?workspace=1'],['comparison','Comparar estratégias','/p/research/compare?workspace=1'],['simulator','Simulador de crescimento','/p/research/growth-simulator?workspace=1'],['health','Saúde','/p/research/operations?workspace=1']]},
    docs: {route:'/documentacao', title:'Documentação', description:'Arquitetura, operação e decisões do projeto.', sections:[['docs','Documentação','/p/docs/']]},
  };
  const routeToPanel = Object.entries(panels).find(([, value]) => value.route === location.pathname)?.[0] || 'history';
  const panel = panels[routeToPanel];
  const params = new URLSearchParams(location.search);
  const selected = panel.sections.find(([key]) => key === params.get('section')) || panel.sections[0];
  const frame = document.getElementById('content-frame');
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
  document.title = `${panel.title} · Gold Lotus`;
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
    } catch (_) { setState('Conteúdo carregado'); }
  });
  window.addEventListener('popstate', () => {
    const key = new URLSearchParams(location.search).get('section');
    show(key, false);
  });
  show(selected[0], false);
})();
