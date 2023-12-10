from time import sleep
import _thread as thread

import pycom
import machine

from tasks.sensors import SensorsThread
from tasks.data import DataThread
from tasks.network import NetworkThread, register_packet_handler
from tasks.movement import MovementThread

# If boot failed heartbeat is False
if pycom.heartbeat():
    pycom.heartbeat(False)
    pycom.rgbled(0x007f00)

    thread.start_new_thread(NetworkThread, ())
    thread.start_new_thread(SensorsThread, ())
    thread.start_new_thread(MovementThread, ())
    thread.start_new_thread(DataThread, ())

    register_packet_handler(0x00, lambda _: machine.reset())

    while True:
        sleep(2)  # sleep 2 seconds to keep main thread alive
