(() => {
  const body = document.body;
  const panels = [
    ['Histórico', 7771, '/'], ['Operation Core', 7772, '/workspace'],
    ['Runner', 7773, '/'], ['Estratégias', 7774, '/workspace'],
    ['Pesquisa', 7775, '/workspace'],
    ['Documentação', 7777, '/'],
  ];
  const icons = {
    7771: '<svg viewBox="0 0 24 24" aria-hidden="true"><ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v6c0 1.7 3.6 3 8 3s8-1.3 8-3V5M4 11v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"/></svg>',
    7772: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 20 6v5c0 5-3.4 8-8 10-4.6-2-8-5-8-10V6l8-3Z"/><path d="m9 12 2 2 4-4"/></svg>',
    7773: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m8 5 11 7-11 7V5Z"/></svg>',
    7774: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m12 3 9 5-9 5-9-5 9-5Z"/><path d="m3 12 9 5 9-5M3 16l9 5 9-5"/></svg>',
    7775: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></svg>',
    7777: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3H20v17H6.5A2.5 2.5 0 0 0 4 22V5.5ZM4 18a2.5 2.5 0 0 1 2.5-2.5H20"/></svg>',
  };
  const nav = document.querySelector('.app-nav');
  if (nav) {
    nav.replaceChildren(...panels.map(([label, port, path]) => {
      const link = document.createElement('a');
      link.className = 'app-nav-link' + (port === 7771 ? ' active' : '');
      link.href = `${location.protocol}//${location.hostname}:${port}${path}`;
      link.innerHTML = `${icons[port]}<span>${label}</span>`;
      if (port === 7771) link.setAttribute('aria-current', 'page');
      return link;
    }));
  }
  const opener = document.querySelector('[data-sidebar-open]');
  const closers = document.querySelectorAll('[data-sidebar-close]');
  if (!opener) return;

  const setOpen = open => {
    body.classList.toggle('sidebar-open', open);
    opener.setAttribute('aria-expanded', String(open));
    if (open) document.querySelector('.app-sidebar-close')?.focus();
    else opener.focus();
  };

  opener.addEventListener('click', () => setOpen(true));
  closers.forEach(control => control.addEventListener('click', () => setOpen(false)));
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && body.classList.contains('sidebar-open')) setOpen(false);
  });
  document.querySelectorAll('.app-nav-link').forEach(link => {
    link.addEventListener('click', () => body.classList.remove('sidebar-open'));
  });
})();
