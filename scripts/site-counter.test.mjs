import test from 'node:test';
import assert from 'node:assert/strict';
import {JSDOM} from 'jsdom';
import worker from '../public/_worker.js';
import {loadSiteCounter} from '../public/site-counter.js';

const KEY = 'miao-beat:site-visits';
function database() {
  const counts = new Map([['site-visits', 1402]]);
  return {counts, prepare(sql) {return {bind(key) {
    assert.equal(key, KEY, 'Beat can only access its fixed counter key');
    return {async first() {
      if (sql.startsWith('INSERT')) counts.set(key, (counts.get(key) || 0) + 1);
      return counts.has(key) ? {count: counts.get(key)} : null;
    }};
  }}}};
}
const request = (options = {}, host = 'miao-beat.pages.dev') => new Request(`https://${host}/api/site-counter`, options);

test('counter is separate from MiaoTI and honors the 24-hour cookie', async () => {
  const db = database(), env = {MIAOBEAT_DB: db};
  const before = await worker.fetch(request(), env);
  assert.equal((await before.json()).count, 0);
  const first = await worker.fetch(request({method: 'POST'}), env);
  assert.match(first.headers.get('set-cookie'), /miao_beat_visit=1; Max-Age=86400; Path=\/; HttpOnly; Secure; SameSite=Lax/);
  assert.equal(first.headers.get('cache-control'), 'private, no-store');
  assert.equal((await first.json()).count, 1);
  const repeated = await worker.fetch(request({method: 'POST', headers: {cookie: 'unrelated=ok; miao_beat_visit=1'}}), env);
  assert.deepEqual(await repeated.json(), {count: 1, counted: false, period: 'since-enabled', dedupeWindowHours: 24});
  assert.equal(repeated.headers.get('set-cookie'), null);
  assert.equal(db.counts.get('site-visits'), 1402, 'MiaoTI aggregate remains unchanged');
});

test('read requests, bots and preview deployments do not increment', async () => {
  const db = database(), env = {MIAOBEAT_DB: db};
  for (const req of [request(), request({method: 'POST', headers: {'user-agent': 'ExampleBot'}}), request({method: 'POST'}, 'qa.miao-beat.pages.dev')]) {
    const response = await worker.fetch(req, env);
    assert.equal(response.status, 200);
    assert.equal((await response.json()).counted, false);
    assert.equal(response.headers.get('set-cookie'), null);
  }
  assert.equal(db.counts.has(KEY), false);
});

test('a zero-byte POST stream is allowed, matching browser requests in workerd', async () => {
  const db = database();
  const body = new ReadableStream({start(controller) {controller.close();}});
  const response = await worker.fetch(request({method: 'POST', body, duplex: 'half', headers: {'content-length': '0'}}), {MIAOBEAT_DB: db});
  assert.equal(response.status, 200);
  assert.equal((await response.json()).count, 1);
});

test('rejects cross-site, payload and unsupported-method requests without a write', async () => {
  const db = database(), env = {MIAOBEAT_DB: db};
  for (const [options, status] of [
    [{method: 'POST', headers: {'sec-fetch-site': 'cross-site'}}, 403],
    [{method: 'POST', headers: {origin: 'https://other.example'}}, 403],
    [{method: 'POST', body: '{}'}, 400],
    [{method: 'PUT'}, 405],
  ]) assert.equal((await worker.fetch(request(options), env)).status, status);
  assert.equal(db.counts.has(KEY), false);
});

test('missing database and invalid data fail explicitly; static assets are forwarded', async () => {
  assert.equal((await worker.fetch(request(), {})).status, 503);
  for (const value of [null, -1, '12', Number.MAX_SAFE_INTEGER + 1]) {
    const env = {MIAOBEAT_DB: {prepare() {return {bind() {return {async first() {return {count: value};}};}};}}};
    assert.equal((await worker.fetch(request(), env)).status, 503);
  }
  let forwarded;
  const staticRequest = new Request('https://miao-beat.pages.dev/character/keyboard-poses-v1.jpg');
  const response = await worker.fetch(staticRequest, {ASSETS: {fetch(req) {forwarded = req; return new Response('asset');}}});
  assert.equal(forwarded, staticRequest);
  assert.equal(await response.text(), 'asset');
});

function page(url = 'https://miao-beat.pages.dev/') {
  return new JSDOM('<p id="siteVisitCount">累计访问：暂时未知</p>', {url});
}
const payload = count => ({count, period: 'since-enabled', dedupeWindowHours: 24});

test('frontend sends no payload and displays the validated cumulative total', async t => {
  const dom = page(); t.after(() => dom.window.close());
  let sent;
  await loadSiteCounter(dom.window.document, async (url, options) => {
    sent = {url, options}; return Response.json(payload(1234));
  });
  assert.equal(sent.url, '/api/site-counter');
  assert.equal(sent.options.method, 'POST');
  assert.equal(sent.options.body, undefined);
  assert.equal(sent.options.credentials, 'same-origin');
  assert.equal(sent.options.referrerPolicy, 'no-referrer');
  assert.equal(dom.window.document.getElementById('siteVisitCount').textContent, '累计访问 1,234 次');
});

test('internal QA and preview pages only read the counter', async () => {
  for (const url of ['https://miao-beat.pages.dev/?analytics=internal', 'https://qa.miao-beat.pages.dev/']) {
    const dom = page(url);
    await loadSiteCounter(dom.window.document, async (_, options) => {
      assert.equal(options.method, 'GET'); return Response.json(payload(3));
    });
    dom.window.close();
  }
});

test('frontend shows unknown for failures and malformed data, never a fabricated zero', async () => {
  for (const fetcher of [
    async () => {throw new Error('offline');},
    async () => new Response('unavailable', {status: 503}),
    ...[null, -1, '12', Number.MAX_SAFE_INTEGER + 1].map(count => async () => Response.json(payload(count))),
  ]) {
    const dom = page();
    await loadSiteCounter(dom.window.document, fetcher);
    assert.equal(dom.window.document.getElementById('siteVisitCount').textContent, '累计访问：暂时未知');
    dom.window.close();
  }
});
