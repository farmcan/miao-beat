// Fixed anonymous buckets only: never send the raw referrer or arbitrary UTM text.
export function visitSource(location,referrer=''){
  const url=new URL(location),tag=(url.searchParams.get('utm_source')||'').toLowerCase();
  const tags={miaoti:'miaoti',miaotarot:'miaotarot',xiaohongshu:'xiaohongshu',xhs:'xiaohongshu',douyin:'douyin','other-project':'other-project'};
  if(tag)return tags[tag]||'other';
  if(!referrer)return 'direct-unknown';
  try{const host=new URL(referrer).hostname;
    if(['miaoti-dmv.pages.dev','miaoti.pages.dev'].includes(host))return 'miaoti';
    if(host==='tarot-31o.pages.dev')return 'miaotarot';
    if(host==='xiaohongshu.com'||host.endsWith('.xiaohongshu.com'))return 'xiaohongshu';
    if(host==='douyin.com'||host.endsWith('.douyin.com'))return 'douyin';
    if(host===url.hostname)return 'direct-unknown';
  }catch{return 'direct-unknown';}
  return 'other';
}
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
    const response = await fetchImpl(readOnly?'/api/site-counter':'/api/site-counter?source='+visitSource(url.href,root.referrer), {
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
