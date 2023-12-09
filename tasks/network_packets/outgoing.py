import ustruct


def SensorsPacket(temperature: float, humidity: float, pressure: float, battery_level: int):
    return (0x02, ustruct.pack(
        '<fffB',
        temperature,
        humidity,
        pressure,
        battery_level
    ))
