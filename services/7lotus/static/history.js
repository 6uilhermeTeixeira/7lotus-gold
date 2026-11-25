(() => {
  const source = new URLSearchParams(location.search).get('source') === 'dukascopy' ? 'dukascopy' : 'fusion';
  const $ = id => document.getElementById(id);
  const number = value => new Intl.NumberFormat('pt-BR').format(value || 0);
  const utc = value => value ? new Date(value).toLocaleString('pt-BR', {timeZone: 'UTC'}) + ' UTC' : 'Sem atualização';
  const duration = seconds => {
    if (seconds == null) return 'Calculando';
    const days = Math.floor(seconds / 86400), hours = Math.floor(seconds % 86400 / 3600);
    return days ? days + 'd ' + hours + 'h' : hours + 'h';
  };
  let queryReady = false;

  function badge(available) {
    const element = document.querySelector(source === 'fusion' ? '.fusion-source .source-status' : '.dukascopy-source .source-status');
    element.textContent = available ? (source === 'fusion' ? 'Candles disponíveis' : 'Histórico baixado') : (source === 'fusion' ? 'Aguardando candles' : 'Aguardando dados');
    element.classList.toggle('ready', available);
    element.classList.toggle('waiting', !available);
  }

  function renderMissing(message) {
    badge(false);
    $('state-label').textContent = 'Histórico indisponível';
    $('updated-label').textContent = message;
    $('overall-label').textContent = message;
    $('overall-percent').textContent = '—';
    $('overall-bar').style.width = '0';
    $('year-list').replaceChildren();
    const empty = document.createElement('p');
    empty.className = 'muted';
    empty.textContent = 'Nenhum dado desta fonte está disponível neste armazenamento.';
    $('year-list').append(empty);
  }

  function renderDukascopy(data) {
    if (!data.available) { renderMissing('Manifesto de coleta Dukascopy não encontrado.'); return; }
    badge(true);
    $('state-dot').classList.toggle('running', data.running);
    $('state-label').textContent = data.running ? 'Download em andamento' : 'Coleta sem atividade recente';
    $('updated-label').textContent = 'Última gravação: ' + utc(data.updated_at);
    $('total-progress').textContent = data.progress_pct.toFixed(2) + '%';
    $('collection-range').textContent = data.requested_start + ' até ' + data.requested_end;
    $('equivalent-years').textContent = data.equivalent_years.toFixed(2) + ' anos';
    $('hours-complete').textContent = number(data.completed_hours) + ' horas processadas';
    $('complete-years').textContent = data.complete_years;
    $('years-total').textContent = 'de ' + data.total_years + ' anos no intervalo';
    $('eta').textContent = duration(data.eta_seconds);
    $('rate').textContent = data.rate_hours_per_minute ? data.rate_hours_per_minute.toFixed(2) + ' horas/min' : 'Taxa será calculada';
    $('overall-percent').textContent = data.progress_pct.toFixed(2) + '%';
    $('overall-label').textContent = number(data.completed_hours) + ' de ' + number(data.expected_hours) + ' horas';
    $('overall-bar').style.width = data.progress_pct + '%';
    $('year-list').replaceChildren();
    for (const year of [...data.years].reverse()) {
      const row = document.createElement('div'); row.className = 'year-row' + (year.complete ? ' complete' : '');
      const name = document.createElement('strong'); name.textContent = year.year;
      const track = document.createElement('div'); track.className = 'track';
      const fill = document.createElement('span'); fill.style.width = year.progress_pct + '%'; track.append(fill);
      const percent = document.createElement('span'); percent.className = 'percent'; percent.textContent = year.progress_pct.toFixed(1) + '%';
      const hours = document.createElement('small'); hours.textContent = number(year.completed_hours) + ' / ' + number(year.expected_hours) + ' h';
      row.append(name, track, percent, hours); $('year-list').append(row);
    }
  }

  function renderFusion(data, m1Data) {
    const labels = document.querySelectorAll('.metric-grid .metric > span');
    ['Candles M1 + M5', 'Primeiro candle', 'Último candle', 'Servidor MT5'].forEach((label, index) => { labels[index].textContent = label; });
    $('query-range-end').hidden = false;
    document.querySelector('.years-panel h2').textContent = 'Candles disponíveis por ano';
    document.querySelector('.years-panel .section-heading .muted').textContent = 'Barras relativas ao ano com mais candles; anos de início e fim cobrem apenas parte do calendário.';
    document.querySelector('.query-panel h2').textContent = 'Consultar candles';
    document.querySelector('.query-panel .section-heading .muted').textContent = 'Intervalo na hora do servidor Fusion · até 5.000 registros por consulta';
    $('query-day-label').firstChild.textContent = 'De ';
    $('query-ticks').textContent = 'Ticks futuramente'; $('query-ticks').disabled = true;
    if (!data.available) { renderMissing(data.reason || 'Nenhum candle Fusion importado.'); return; }
    badge(true);
    $('state-label').textContent = 'Candles importados';
    $('updated-label').textContent = 'Hora do servidor Fusion · não convertida para UTC';
    $('total-progress').textContent = number(data.rows);
    $('collection-range').textContent = 'XAUUSD · M1 + M5';
    $('total-progress').textContent = m1Data?.available
      ? `${number(m1Data.rows)} M1 · ${number(data.rows)} M5`
      : `${number(data.rows)} M5`;
    $('equivalent-years').textContent = (m1Data?.available ? m1Data.first_server_time : data.first_server_time).slice(0, 10);
    $('hours-complete').textContent = 'Hora do servidor';
    $('complete-years').textContent = (m1Data?.available ? m1Data.last_server_time : data.last_server_time).slice(0, 10);
    $('years-total').textContent = 'Hora do servidor';
    $('eta').textContent = data.server;
    $('rate').textContent = 'Release ' + data.version;
    $('overall-label').textContent = 'M1: ' + (m1Data?.available ? `${m1Data.first_server_time} → ${m1Data.last_server_time}` : 'indisponível')
      + ' · M5: ' + data.first_server_time + ' → ' + data.last_server_time;
    $('overall-percent').textContent = '';
    $('overall-bar').style.display = 'none';
    $('year-list').replaceChildren();
    for (const year of [...data.years].reverse()) {
      const row = document.createElement('div'); row.className = 'year-row';
      const name = document.createElement('strong'); name.textContent = year.year;
      const track = document.createElement('div'); track.className = 'track';
      const peak = Math.max(...data.years.map(item => item.candles));
      const fill = document.createElement('span'); fill.style.width = Math.min(100, year.candles / Math.max(1, peak) * 100) + '%'; track.append(fill);
      const count = document.createElement('span'); count.className = 'percent'; count.textContent = number(year.candles);
      const label = document.createElement('small'); label.textContent = 'candles disponíveis';
      row.append(name, track, count, label); $('year-list').append(row);
    }
  }

  async function refresh() {
    try {
      const url = source === 'fusion' ? '/api/fusion/candles/status' : '/api/history/progress?source=dukascopy';
      const [response, m1Response] = await Promise.all([
        fetch(url),
        source === 'fusion' ? fetch('/api/fusion/candles/status?timeframe=M1') : Promise.resolve(null),
      ]);
      const data = await response.json();
      const m1Data = m1Response ? await m1Response.json() : null;
      if (!response.ok) throw Error(data.detail || 'Falha ao consultar o histórico.');
      if (source === 'fusion') renderFusion(data, m1Data); else renderDukascopy(data);
      queryReady = data.available;
      $('query-candles').disabled = !queryReady;
      $('query-ticks').disabled = source === 'fusion' || !queryReady;
      if (source === 'fusion') {
        $('query-ticks').textContent = 'Ticks futuramente';
        const m1Available = Boolean(m1Data?.available);
        $('query-resolution').value = m1Available ? '1m' : '5m';
        $('query-status').textContent = data.available
          ? `${m1Available ? number(m1Data.rows) + ' candles M1 · ' : 'M1 indisponível · '}${number(data.rows)} candles M5 · horário do servidor Fusion.`
          : data.reason;
        if (data.available) {
          const first = m1Available ? m1Data.first_server_time : data.first_server_time;
          const last = m1Available && m1Data.last_server_time > data.last_server_time ? m1Data.last_server_time : data.last_server_time;
          $('query-day').min = first.slice(0, 10);
          $('query-day').max = last.slice(0, 10);
          $('query-end').min = $('query-day').min;
          $('query-end').max = $('query-day').max;
          if (!$('query-day').value) $('query-day').value = last.slice(0, 10);
          if (!$('query-end').value) $('query-end').value = $('query-day').value;
        }
      } else {
        const status = await fetch('/api/status').then(result => result.json());
        $('query-status').textContent = status.release.available ? 'Release ' + status.release.version + ' disponível.' : status.message;
        queryReady = status.release.available;
        $('query-candles').disabled = !queryReady;
        $('query-ticks').disabled = !queryReady;
        if (queryReady && !$('query-day').value) $('query-day').value = status.release.summary.coverage_end;
      }
    } catch (error) { renderMissing(error.message); $('query-status').textContent = error.message; }
  }

  function drawChart(items) {
    const svg = $('query-chart'); svg.replaceChildren(); svg.hidden = !items.length;
    if (!items.length) return;
    const prices = items.map(item => Number(item.close));
    const low = Math.min(...prices), high = Math.max(...prices), span = high - low || 1;
    const points = prices.map((value, index) => `${45 + index / Math.max(1, prices.length - 1) * 910},${235 - (value - low) / span * 210}`).join(' ');
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
    line.setAttribute('points', points); line.setAttribute('fill', 'none');
    line.setAttribute('stroke', '#41d392'); line.setAttribute('stroke-width', '2'); svg.append(line);
  }

  function showTable(items, kind) {
    const table = $('query-table'), head = table.querySelector('thead'), body = table.querySelector('tbody');
    head.replaceChildren(); body.replaceChildren(); table.hidden = !items.length;
    if (!items.length) return;
    const fields = source === 'fusion'
      ? [['Hora do servidor', 'server_time'], ['Abertura', 'open'], ['Máxima', 'high'], ['Mínima', 'low'], ['Fechamento', 'close'], ['Volume ticks', 'tick_volume'], ['Spread pontos', 'spread_points']]
      : kind === 'ticks'
        ? [['Hora UTC', 'timestamp_ms'], ['Bid', 'bid'], ['Ask', 'ask'], ['Spread', 'spread']]
        : [['Hora UTC', 'timestamp_ms'], ['Abertura', 'open'], ['Máxima', 'high'], ['Mínima', 'low'], ['Fechamento', 'close'], ['Volume', 'volume']];
    const header = document.createElement('tr');
    for (const [label] of fields) { const cell = document.createElement('th'); cell.textContent = label; header.append(cell); }
    head.append(header);
    for (const item of items.slice(0, 100)) {
      const row = document.createElement('tr');
      for (const [, key] of fields) {
        const cell = document.createElement('td');
        cell.textContent = key === 'server_time' ? item[key] : key === 'timestamp_ms'
          ? utc(item[key]) : Number(item[key]).toLocaleString('pt-BR', {maximumFractionDigits: 4});
        row.append(cell);
      }
      body.append(row);
    }
  }

  async function query(kind) {
    if (!queryReady || (source === 'fusion' && kind === 'ticks')) return;
    const day = $('query-day').value;
    if (!day) { $('query-status').textContent = 'Escolha a data inicial.'; return; }
    const params = new URLSearchParams({day});
    let endpoint = '/api/' + kind;
    if (source === 'fusion') {
      const end = $('query-end').value;
      if (!end || end < day) { $('query-status').textContent = 'Escolha uma data final igual ou posterior à inicial.'; return; }
      endpoint = '/api/fusion/candles/range';
      params.delete('day'); params.set('start', day); params.set('end', end);
      params.set('resolution', $('query-resolution').value);
    }
    else if (kind === 'candles') params.set('resolution', $('query-resolution').value);
    else params.set('limit', '100');
    $('query-status').textContent = 'Lendo dados publicados...';
    try {
      const response = await fetch(endpoint + '?' + params);
      const data = await response.json();
      if (!response.ok) throw Error(data.detail || 'Consulta indisponível.');
      $('query-status').textContent = data.items.length
        ? data.items.length + ' registros · release ' + data.version + (data.truncated ? ' · limite de 5.000 atingido; reduza o intervalo.' : '')
        : 'Não há dados publicados neste intervalo.';
      drawChart(kind === 'candles' ? data.items : []); showTable(data.items, kind);
    } catch (error) { $('query-status').textContent = error.message; drawChart([]); showTable([], kind); }
  }

  $('query-candles').addEventListener('click', () => query('candles'));
  $('query-ticks').addEventListener('click', () => query('ticks'));
  refresh(); setInterval(refresh, 15000);
})();
