/** Loopback-only preview, buffering synchronized files before their transmission.
 * Usage: node scripts/frontend/serve_preview.cjs [port]
 */
const http = require('node:http');
const fs = require('node:fs/promises');
const path = require('node:path');
const root = path.resolve(__dirname, '../..');
const types = { '.html': 'text/html; charset=utf-8', '.js': 'application/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8', '.json': 'application/json; charset=utf-8', '.geojson': 'application/geo+json', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.ico': 'image/x-icon' };
function createPreview() {
  return http.createServer(async (request, response) => {
    try {
      const relative = decodeURIComponent(new URL(request.url, 'http://localhost').pathname).replace(/^\/+/, '') || 'index.html';
      const file = path.resolve(root, relative);
      if (!file.startsWith(root + path.sep) || !['GET', 'HEAD'].includes(request.method)) {
        response.writeHead(403).end(); return;
      }
      const content = await fs.readFile(file);
      response.writeHead(200, { 'Content-Type': types[path.extname(file)] || 'application/octet-stream', 'Content-Length': content.length, 'Cache-Control': 'no-store' });
      response.end(request.method === 'HEAD' ? undefined : content);
    } catch {
      if (!response.headersSent) response.writeHead(404).end('File not available');
      else response.destroy();
    }
  });
}
module.exports = { createPreview };
if (require.main === module) {
  const port = Number(process.argv[2] || 8000);
  if (!Number.isInteger(port) || port < 0 || port > 65535) throw new Error('Invalid port');
  const server = createPreview();
  server.on('error', error => { console.error(error.message); process.exitCode = 1; });
  server.listen(port, '127.0.0.1', () => console.log(`Local preview: http://127.0.0.1:${server.address().port}`));
  process.on('SIGINT', () => { server.close(); server.closeAllConnections(); });
}
