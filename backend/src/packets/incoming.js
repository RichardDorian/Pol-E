function SensorsPacket(data) {
  const temperature = data.readFloatLE(0);
  const humidity = data.readFloatLE(4);
  const pressure = data.readFloatLE(8);
  const ambientLight = data.readFloatLE(12);
  const batteryLevel = data.readUInt8(16);

  return {
    temperature,
    pressure,
    humidity,
    ambientLight,
    batteryLevel,
  };
}

module.exports = {
  0x02: SensorsPacket,
};
