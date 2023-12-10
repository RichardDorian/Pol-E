import ustruct


def SensorsPacket(temperature: float, humidity: float, pressure: float, ambient_light: float, battery_level: int):
    return (0x02, ustruct.pack(
        '<ffffB',
        temperature,
        humidity,
        pressure,
        ambient_light,
        battery_level
    ))
