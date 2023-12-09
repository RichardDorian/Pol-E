const { createServer } = require('node:http');
const { createReadStream } = require('fs');
const { join } = require('node:path');
const { WebSocketServer } = require('ws');

let socket;

const server = createServer();

const staticFiles = {
  '/': { file: 'index.html', contentType: 'text/html' },
  '/index.html': { file: 'index.html', contentType: 'text/html' },
  '/styles.css': { file: 'styles.css', contentType: 'text/css' },
  '/script.js': { file: 'script.js', contentType: 'text/javascript' },
  '/favicon.png': { file: 'favicon.png', contentType: 'image/png' },
};

server.on('request', (req, res) => {
  const parsedUrl = new URL(req.url, `http://${req.headers.host}`);

  if (parsedUrl.pathname in staticFiles) {
    const file = staticFiles[parsedUrl.pathname];
    res.writeHead(200, { 'Content-Type': file.contentType });
    const fileStream = createReadStream(
      join(__dirname, '..', 'public', file.file)
    );
    fileStream.pipe(res);
  }
});

const websocketServer = new WebSocketServer({ server });
websocketServer.on('connection', (_socket) => {
  socket = _socket;

  socket.on('message', (data) => {
    onDataHandler?.(JSON.parse(data));
  });

  for (const packet of packetQueue) {
    socket.send(JSON.stringify(packet));
  }
});
server.listen(80, () =>
  console.log('Web server listening on port 80\nAccessible @ http://localhost')
);

const packetQueue = [];
let onDataHandler = null;

module.exports = {
  sendData(data) {
    packetQueue.push(data);
    if (!!socket) {
      socket.send(JSON.stringify(data));
    } else {
    }
  },
  onData(handler) {
    onDataHandler = handler;
  },
};
