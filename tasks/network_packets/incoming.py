import ustruct


def ResetPacket(bytes: bytes) -> None:
    return


def StartStopPacket(bytes: bytes) -> None:
    return


def SetSpeedDeltaPacket(bytes: bytes) -> int:
    return ustruct.unpack('<B', bytes)[0]


IncomingPackets = {
    0x00: ResetPacket,
    0x01: StartStopPacket,
    0x03: SetSpeedDeltaPacket
}
