const { createConnection } = require('node:net');

const ip = process.argv[process.argv.indexOf('--ip') + 1];

const socket = createConnection({
  host: ip,
  port: 7596,
  noDelay: true,
});

socket.on('connect', () => console.log('Connected'));

socket.on('data', (data) => {
  console.log(`Received ${data.length} bytes of data`);
  console.log(data.toString('hex'));
});

// set speed delta

const { createInterface } = require('node:readline');

const rl = createInterface({
  input: process.stdin,
  output: process.stdout,
});

rl.on('line', (line) => {
  if (line === 'reset') {
    socket.write(Buffer.from([0x02, 0x00]));
    return;
  }

  speedDelta = parseInt(line);
  socket.write(Buffer.from([0x03, 0x04, speedDelta]));
});
