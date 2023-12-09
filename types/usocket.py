from __future__ import annotations
from typing import Literal, Any

AF_INET: int
AF_LORA: int
AF_SIGFOX: int
SOCK_STREAM: int
SOCK_DGRAM: int
SOCK_RAW: int
IPPROTO_IP: int
IPPROTO_ICMP: int
IPPROTO_UDP: int
IPPROTO_TCP: int
IPPROTO_IPV6: int
IP_ADD_MEMBERSHIP: int
IPPROTO_RAW: int

SOL_SOCKET: int
SOL_LORA: int
SOL_SIGFOX: int

SO_REUSEADDR: int

SO_CONFIRMED: int
SO_DR: int

SO_RX: int
SO_TX_REPEAT: int
SO_OOB: int
SO_BIT: int

class __class__:
    def close(self) -> None: ...

    def bind(self, address: tuple[str, int]) -> None: ...

    def listen(self, backlog: int) -> None: ...

    def accept(self) -> tuple[__class__, str]: ...

    def connect(self, addrress: str) -> None: ...

    def send(self, bytes: bytes) -> None: ...

    def sendall(self, bytes: bytes) -> None: ...

    def recv(self, bufsize: int) -> bytes: ...

    def sendto(self, bytes: bytes, address: str) -> None: ...

    def recvfrom(self, bufsize: int) -> tuple[bytes, str]: ...

    def settimeout(self, value: float | None) -> None: ...

    def setblocking(self, flag: bool) -> None: ...

    def makefile(self, mode: Literal['rb, wb'] = 'rb') -> Any: ...

    def read(self, size: int = 999999) -> bytes: ...

    def readall(self) -> bytes: ...

    def readinto(self, buf: bytearray, nbytes: int | None = None) -> int: ...

    def readline(self) -> str: ...

    def write(buf: bytes) -> int: ...

    def do_handshake(self) -> Any: ...

    def dnsserver(self, dnsIndex: Any, id_addr: str) -> Any: ...

def socket(address_family: int = AF_INET, socket_type: int = SOCK_STREAM, protocol_number: int = IPPROTO_TCP) -> __class__: ...

def setsockopt(level: int, optname: int, value: int) -> None: ...

def getaddrinfo(host: str, port: int) -> tuple[str, str, str, str, str]: ...