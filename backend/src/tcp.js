const { createConnection } = require('node:net');
const IncomingPackets = require('./packets/incoming');

const PacketHandlers = {};

const socket = createConnection({
  host: process.argv[process.argv.indexOf('--ip') + 1],
  port: 7596,
  noDelay: true,
});

socket.on('connect', () => console.log('Connected'));

socket.on('data', (data) => {
  let packetLength = data.length;

  while (packetLength > 0) {
    packetLength = data.readUInt8(0);
    const packetId = data.readUInt8(1);
    const packetData = data.subarray(2, packetLength - 2 + 2);

    const packet = IncomingPackets[packetId]?.(packetData);

    if (packetId in PacketHandlers && !!packet) {
      PacketHandlers[packetId](packet);
    }

    data = data.subarray(packetLength);
    packetLength = data.length;
  }
});

require('readline')
  .createInterface({
    input: process.stdin,
    output: process.stdout,
  })
  .on('line', (input) => {
    if (input === 'reset') {
      socket.write(Buffer.from([0x02, 0x00]));
    }

    input = Number(input);
    socket.write(Buffer.from([0x03, 0x03, input]));
  });

module.exports = {
  registerPacketHandler(packetId, handler) {
    PacketHandlers[packetId] = handler;
  },
};
