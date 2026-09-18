/**
 * 本地静态预览服务 —— 用于滚动驱动主页的验收截图。
 *
 * 为什么要用 HTTP 而不是 file:// ：部分场景下 file:// 页面会被浏览器判为
 * 不可访问导致截图空白；HTTP 更稳定。
 *
 * 关键点：必须带 Content-Length。缺失时二进制图片可能读取异常（实测表现为
 * 浏览器内 naturalWidth 为 0）。
 *
 * 用法：
 *   node serve.js [rootDir] [port]
 *   默认 rootDir 为当前工作目录，port 8899
 */
const http = require('http');
const fs = require('fs');
const path = require('path');

const root = path.resolve(process.argv[2] || process.cwd());
const port = Number(process.argv[3] || 8899);

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.webp': 'image/webp',
  '.gif': 'image/gif',
  '.mp4': 'video/mp4',
  '.woff2': 'font/woff2'
};

http.createServer((req, res) => {
  let rel = decodeURIComponent(req.url.split('?')[0]);
  if (rel === '/') rel = '/index.html';

  // 目录穿越防护
  const file = path.join(root, path.normalize(rel).replace(/^(\.\.[\\/])+/, ''));
  if (!file.startsWith(root)) {
    res.writeHead(403);
    return res.end('403');
  }

  fs.readFile(file, (err, data) => {
    if (err) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      return res.end('404 Not Found: ' + rel);
    }
    const type = MIME[path.extname(file).toLowerCase()] || 'application/octet-stream';
    // Content-Length 必须显式给出，否则二进制资源可能读取异常
    res.writeHead(200, {
      'Content-Type': type,
      'Content-Length': data.length,
      'Cache-Control': 'no-store'
    });
    res.end(data);
  });
}).listen(port, '127.0.0.1', () => {
  console.log(`preview serving ${root}`);
  console.log(`  -> http://127.0.0.1:${port}/`);
});
