(() => {
  const panel = document.currentScript.dataset.panel;
  const prefixes = {7771:'history',7772:'operations',7773:'runner',7774:'strategies',7775:'research',7777:'docs'};
  const routes = {history:'/historico',operations:'/operacao',runner:'/runner',strategies:'/estrategias',promoted:'/promovidas',research:'/pesquisa',docs:'/documentacao'};
  function mapUrl(input) {
    const url = new URL(String(input), location.href);
    if (url.origin === location.origin && url.pathname.startsWith('/p/')) return url.href;
    const other = url.origin !== location.origin && ['localhost','127.0.0.1','::1'].includes(url.hostname) ? prefixes[url.port] : null;
    const target = url.origin === location.origin ? panel : other;
    if (!target) return url.href;
    url.protocol = location.protocol;
    url.host = location.host;
    url.pathname = `/p/${target}${url.pathname}`;
    return url.href;
  }
  const originalFetch = window.fetch;
  window.fetch = function(input, init) {
    if (input instanceof Request) return originalFetch.call(this, new Request(mapUrl(input.url), input), init);
    return originalFetch.call(this, mapUrl(input), init);
  };
  const originalOpen = XMLHttpRequest.prototype.open;
  XMLHttpRequest.prototype.open = function(method, url, ...rest) {
    return originalOpen.call(this, method, mapUrl(url), ...rest);
  };
  document.addEventListener('click', event => {
    const link = event.target.closest('a[href]');
    if (!link || link.hasAttribute('download') || event.defaultPrevented) return;
    const original = new URL(link.href, location.href);
    const target = original.origin !== location.origin && ['localhost','127.0.0.1','::1'].includes(original.hostname) ? prefixes[original.port] : null;
    if (target && target !== panel) {
      link.href = routes[target];
      if (!event.ctrlKey && !event.metaKey && !event.shiftKey && link.target !== '_blank') {
        event.preventDefault();
        top.location.href = routes[target];
      }
      return;
    }
    link.href = mapUrl(link.href);
  }, true);
  document.addEventListener('submit', event => {
    if (event.target instanceof HTMLFormElement) event.target.action = mapUrl(event.target.action);
  }, true);
})();
