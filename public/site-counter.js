export async function loadSiteCounter(root = document, fetchImpl = globalThis.fetch) {
  const output = root.getElementById('siteVisitCount');
  if (!output) return;
  output.textContent = '累计访问：暂时未知';
  if (typeof fetchImpl !== 'function') return;
  const url = new URL(root.location.href);
  const preview = url.hostname.endsWith('.miao-beat.pages.dev');
  const readOnly = preview || url.searchParams.get('analytics') === 'internal';
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 5000);
  output.textContent = '累计访问：读取中…';
  try {
    const response = await fetchImpl('/api/site-counter', {
      method: readOnly ? 'GET' : 'POST', credentials: 'same-origin',
      headers: {Accept: 'application/json'}, cache: 'no-store',
      referrerPolicy: 'no-referrer', signal: controller.signal,
    });
    if (!response.ok) throw new Error('Counter unavailable');
    const data = await response.json();
    if (!Number.isSafeInteger(data.count) || data.count < 0 || data.period !== 'since-enabled' || data.dedupeWindowHours !== 24) throw new Error('Invalid counter response');
    output.textContent = `累计访问 ${data.count.toLocaleString('zh-CN')} 次`;
  } catch {
    output.textContent = '累计访问：暂时未知';
  } finally {
    clearTimeout(timer);
  }
}
