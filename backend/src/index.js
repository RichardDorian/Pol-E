const { registerPacketHandler } = require('./tcp');
const { onData, sendData } = require('./web');

registerPacketHandler(0x02, (packet) => {
  sendData({ type: 'sensors-data', time: Date.now(), data: packet });
});
