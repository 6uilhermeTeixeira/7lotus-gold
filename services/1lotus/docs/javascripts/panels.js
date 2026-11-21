(() => {
  if (!['127.0.0.1', 'localhost', '::1'].includes(location.hostname)) return;

  const panels = [
    ['Histórico', 7771, '/', '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v6c0 1.7 3.6 3 8 3s8-1.3 8-3V5M4 11v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"/>'],
    ['Operation Core', 7772, '/workspace', '<path d="M12 3 20 6v5c0 5-3.4 8-8 10-4.6-2-8-5-8-10V6l8-3Z"/><path d="m9 12 2 2 4-4"/>'],
    ['Runner', 7773, '/', '<path d="m8 5 11 7-11 7V5Z"/>'],
    ['Estratégias', 7774, '/workspace', '<path d="m12 3 9 5-9 5-9-5 9-5Z"/><path d="m3 12 9 5 9-5M3 16l9 5 9-5"/>'],
    ['Pesquisa', 7775, '/workspace', '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>'],
    ['Documentação', 7777, '/', '<path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v17H6.5A2.5 2.5 0 0 0 4 22V5.5ZM4 18a2.5 2.5 0 0 1 2.5-2.5H20"/>'],
  ];
  const sidebar = document.createElement('aside');
  sidebar.className = 'app-sidebar';
  sidebar.id = 'app-sidebar';
  sidebar.setAttribute('aria-label', 'Navegação principal');
  sidebar.innerHTML = '<div class="app-sidebar-brand"><a href="/" aria-label="Gold Lotus"><img src="assets/lotus-icon.png" alt=""><span>LOTUS</span></a><button class="app-sidebar-close" type="button" aria-label="Fechar menu">×</button></div><div class="app-workspace-label"><span>Painéis locais</span><strong>Gold Lotus</strong></div><nav class="app-nav" aria-label="Painéis locais"></nav>';
  const nav = sidebar.querySelector('.app-nav');
  for (const [label, port, path, icon] of panels) {
    const link = document.createElement('a');
    link.className = `app-nav-link${port === 7777 ? ' active' : ''}`;
    link.href = `${location.protocol}//${location.hostname}:${port}${path}`;
    link.innerHTML = `<svg viewBox="0 0 24 24" aria-hidden="true">${icon}</svg><span>${label}</span>`;
    if (port === 7777) link.setAttribute('aria-current', 'page');
    nav.append(link);
  }

  const overlay = document.createElement('div');
  overlay.className = 'app-sidebar-overlay';
  const topbar = document.createElement('header');
  topbar.className = 'app-topbar';
  topbar.innerHTML = '<button class="app-menu-button" type="button" aria-controls="app-sidebar" aria-expanded="false" aria-label="Abrir menu"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg></button><div><span>Gold Lotus</span><strong>Documentação</strong></div><span class="app-topbar-mode">Local</span>';

  const main = document.querySelector('body > .container [role="main"]');
  if (!main) return;
  const host = document.querySelector('.navbar.bg-primary');
  if (host) host.remove();
  const sectionLinks = document.querySelector('.nav.navbar-nav:not(.ms-md-auto)');
  if (sectionLinks) {
    const sectionNav = document.createElement('nav');
    sectionNav.className = 'documentation-nav';
    sectionNav.setAttribute('aria-label', 'Seções da documentação');
    const title = document.createElement('strong');
    title.textContent = 'Documentação';
    sectionNav.append(title, ...sectionLinks.querySelectorAll('.nav-link'));
    main.before(sectionNav);
  }
  document.body.prepend(topbar, overlay, sidebar);

  const opener = topbar.querySelector('.app-menu-button');
  const close = sidebar.querySelector('.app-sidebar-close');
  const setOpen = (open) => {
    document.body.classList.toggle('sidebar-open', open);
    opener.setAttribute('aria-expanded', String(open));
  };
  opener.addEventListener('click', () => setOpen(!document.body.classList.contains('sidebar-open')));
  close.addEventListener('click', () => setOpen(false));
  overlay.addEventListener('click', () => setOpen(false));
  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') setOpen(false);
  });
})();
