import ustruct
import usocket
from time import sleep
import _thread as thread

from network import WLAN

from tasks.network_packets.incoming import IncomingPackets


class NetworkData:
    is_connected = False
    PacketQueue = []
    PacketHandlers = {}


def register_packet_handler(packet_id: int, handler: callable) -> None:
    NetworkData.PacketHandlers[packet_id] = handler


def get_packet_from_queue() -> tuple[int, bytes]:
    return NetworkData.PacketQueue.pop(0) if len(NetworkData.PacketQueue) > 0 else None


def queue_packet(packet: tuple[int, bytes]) -> None:
    if not NetworkData.is_connected:
        return  # If we're not connected to a network we drop to save memory as it will never be sent
    NetworkData.PacketQueue.append(packet)


def ClientThread(socket: usocket.__class__, address: tuple[str, int]):
    print('Computer is connected (ip address: {})'.format(address[0]))

    socket.setblocking(False)

    while True:
        # send packet if any in queue
        packet_to_send = get_packet_from_queue()
        if packet_to_send is not None:
            (packet_id, data) = packet_to_send
            size = len(data) + 2
            packet = ustruct.pack('<BB', size, packet_id) + data
            # print("Sending {} bytes of data".format(len(packet)))
            socket.send(packet)

            # If you want to send all queued packets before processing incoming packets uncomment the following line
            continue

        # receive 1 byte (if there's no incoming packet r will be empty otherwise r will contain the length of the incoming packet)
        received = socket.recv(1)

        if len(received) == 0:
            sleep(0.05)  # wait 50ms to let other threads run
            continue

        else:
            (packet_size, *_) = ustruct.unpack('<B', received)
            if packet_size < 2:
                continue  # packet size cannot be less than 2

            raw_packet_id = socket.recv(1)
            (packet_id, *_) = ustruct.unpack('<B', raw_packet_id)

            packet = IncomingPackets.get(packet_id)
            if packet is None:
                continue  # we ignore unknown packets

            raw_packet_data = socket.recv(packet_size-2)
            packet_data = packet(raw_packet_data)

            handler = NetworkData.PacketHandlers.get(packet_id)
            if handler is None:
                continue
            handler(packet_data)


def NetworkThread():
    wlan = WLAN()  # WLAN instance is already initialized @ boot
    NetworkData.is_connected = wlan.isconnected()
    ip_address = wlan.ifconfig()[0]

    server_socket = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
    server_socket.setsockopt(usocket.SOL_SOCKET, usocket.SO_REUSEADDR, 1)
    server_socket.bind((ip_address, 7596))

    server_socket.listen(1)  # 1 client maximum (the computer)

    while True:
        (client_socket, address) = server_socket.accept()
        thread.start_new_thread(ClientThread, (client_socket, address))
        sleep(0.5)  # wait 500ms to let other threads run
