// Counter flow adapted from MiaoTI's functions/api/site-counter.js.
// Only this fixed aggregate key is read or written; no visitor records are stored.
const COUNTER_KEY = 'miao-beat:site-visits';
const COOKIE_NAME = 'miao_beat_visit';
const MAX_AGE = 24 * 60 * 60;
const CANONICAL_HOST = 'miao-beat.pages.dev';

function json(data, status = 200, extraHeaders = {}) {
  return new Response(JSON.stringify(data), {status, headers: {
    'Content-Type': 'application/json; charset=utf-8',
    'Cache-Control': 'private, no-store',
    'X-Content-Type-Options': 'nosniff',
    ...extraHeaders,
  }});
}

function hasVisitCookie(request) {
  return (request.headers.get('cookie') || '').split(';').some(part => part.trim() === `${COOKIE_NAME}=1`);
}

function validCount(row) {
  const count = row === null ? 0 : row?.count;
  if (!Number.isSafeInteger(count) || count < 0) throw new Error('Invalid aggregate count');
  return count;
}

async function counter(request, env, url) {
  if (!['GET', 'POST'].includes(request.method)) return json({error: 'method_not_allowed'}, 405, {Allow: 'GET, POST'});
  if (request.method === 'POST') {
    const origin = request.headers.get('origin');
    if (request.headers.get('sec-fetch-site') === 'cross-site' || (origin && origin !== url.origin)) return json({error: 'cross_site_request'}, 403);
    // The visit request has no payload. Never accept keys, recordings or profile data.
    const length = request.headers.get('content-length');
    if (length && length !== '0') return json({error: 'body_not_allowed'}, 400);
    // workerd can represent a zero-byte browser POST as a non-null stream.
    if (request.body) {
      const reader = request.body.getReader();
      try {
        const {done} = await reader.read();
        if (!done) {await reader.cancel(); return json({error: 'body_not_allowed'}, 400);}
      } finally {reader.releaseLock();}
    }
  }
  if (!env.MIAOBEAT_DB) return json({error: 'counter_unavailable'}, 503);
  const local = ['localhost', '127.0.0.1', '[::1]'].includes(url.hostname);
  const bot = /bot|crawler|spider|slurp|preview|facebookexternalhit|whatsapp/i.test(request.headers.get('user-agent') || '');
  // Preview deployments can read the total but must not increment production data.
  const counted = request.method === 'POST' && (url.hostname === CANONICAL_HOST || local) && !bot && !hasVisitCookie(request);
  try {
    const query = counted
      ? `INSERT INTO site_counters (counter_key, count, updated_at) VALUES (?, 1, CURRENT_TIMESTAMP)
         ON CONFLICT(counter_key) DO UPDATE SET count = count + 1, updated_at = CURRENT_TIMESTAMP RETURNING count`
      : 'SELECT count FROM site_counters WHERE counter_key = ?';
    const row = await env.MIAOBEAT_DB.prepare(query).bind(COUNTER_KEY).first();
    const count = validCount(row);
    return json({count, counted, period: 'since-enabled', dedupeWindowHours: 24}, 200, counted ? {
      'Set-Cookie': `${COOKIE_NAME}=1; Max-Age=${MAX_AGE}; Path=/; HttpOnly; Secure; SameSite=Lax`,
    } : {});
  } catch {
    return json({error: 'counter_unavailable'}, 503);
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === '/api/site-counter') return counter(request, env, url);
    return env.ASSETS.fetch(request);
  },
};
