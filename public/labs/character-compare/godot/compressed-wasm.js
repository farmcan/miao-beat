/* Godot 4.7.2's genuine WASM, gzip-decoded in this iframe to fit static hosting.
 * Only index.wasm fetches are intercepted; all other network requests are native.
 * The decoded bytes are checked against the exported SHA in build evidence.
 */
(() => {
  'use strict';
  const nativeFetch = window.fetch.bind(window);
  const engineURL = new URL('index.wasm', document.baseURI);
  window.fetch = async (input, init) => {
    const target = new URL(typeof input === 'string' || input instanceof URL ? input : input.url, document.baseURI);
    if (target.origin !== engineURL.origin || target.pathname !== engineURL.pathname) return nativeFetch(input, init);
    const packedURL = new URL('index.wasm.gz', document.baseURI);
    const response = await nativeFetch(packedURL, init);
    if (!response.ok) throw new Error(`Godot WASM download: ${response.status}`);
    const packed = new Uint8Array(await response.arrayBuffer());
    let binary;
    if (packed[0] === 0 && packed[1] === 97 && packed[2] === 115 && packed[3] === 109) {
      // A host may already have decoded a Content-Encoding response.
      binary = packed;
    } else {
      if (typeof DecompressionStream !== 'function') throw new Error('This browser needs gzip DecompressionStream for the Godot comparison.');
      const stream = new Blob([packed]).stream().pipeThrough(new DecompressionStream('gzip'));
      binary = new Uint8Array(await new Response(stream).arrayBuffer());
    }
    if (binary[0] !== 0 || binary[1] !== 97 || binary[2] !== 115 || binary[3] !== 109) throw new Error('Decoded Godot engine is not a WASM module.');
    return new Response(binary, {status: 200, headers: {'Content-Type': 'application/wasm', 'Content-Length': String(binary.length)}});
  };
})();
