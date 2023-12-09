class WLAN:
    STA: int
    AP: int
    STA_AP: int

    INT_ANT: int
    EXT_ANT: int
    MAN_ANT: int

    HT20: int
    HT40: int

    WEP: int
    WPA: int
    WPA2: int
    WPA2_ENT: int

    SCAN_ACTIVE: int
    SCAN_PASSIVE: int

    def __init__(self, id: int = 0) -> None: ...

    def init(self, mode: int, ssid: str | None = None, auth: tuple[int | None, str] | None = None, channel: int = 1,
             antenna: int = MAN_ANT, power_save: bool = False, hidden: bool = False, bandwith: int = HT40, *, max_tx_pwr, country, protocol) -> None: ...

    def deinit(self) -> None: ...

    def connect(ssid: str, auth: tuple[int | None, str] | None = None,
                bssid: bytes | None = None, timeout: int | None = None, ca_certs: str | None = None, keyfile: str | None = None, identify: str | None = None, hostname: str | None = None) -> None: ...

    def scan(self, ssid: str | None = None, bssid: bytes | None = None, channel: int = 0,
             show_hidden: bool = False, type: int = SCAN_ACTIVE, scantime: int = 120) -> None: ...

    def disconnect(self) -> None: ...

    def isconnected(self) -> bool: ...

    def ifconfig(id: int = 0, config: str | (
        str, str, str, str) = 'dhcp') -> tuple[str, str, str, str]: ...

    def mode(mode: int | None = None) -> int: ...

    # more methods @ https://docs.pycom.io/firmwareapi/pycom/network/wlan/
