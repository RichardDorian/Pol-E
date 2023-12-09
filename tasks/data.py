from os import mount
from time import sleep

from machine import SD

from ntime import get_time, pretty_print_time
from tasks.network import NetworkData, queue_packet
from tasks.network_packets.outgoing import SensorsPacket
from tasks.sensors import SensorsData

FILE_PATH = '/sd/data.csv'
HEADER = ['        Time        ',
          'Temperature (°C)', 'Humidity (%)', 'Pressure (hPa)', 'Battery level (%)']


class DataData:
    sd_card_present = False


def DataThread():
    try:
        sd = SD()
        mount(sd, '/sd')
        DataData.sd_card_present = True

        with open(FILE_PATH, 'w') as file:
            file.write(';'.join(HEADER))
    except OSError:
        if not NetworkData.is_connected:
            print('SD card not present, priting data instead')
            print('| {} |'.format(' | '.join(HEADER)))

    while True:
        display_time = pretty_print_time(get_time())

        if SensorsData.temperature == 0.0:  # On the first run sensors didn't run yet, this delays the first run only
            sleep(0.05)
            continue

        queue_packet(SensorsPacket(SensorsData.temperature,
                     SensorsData.humidity, SensorsData.pressure, SensorsData.ambient_light, SensorsData.battery_level))

        if DataData.sd_card_present:
            file = open(FILE_PATH, 'a')
            file.write('\n{};{:2f};{:2f};{:2f};{d}'.format(
                display_time, SensorsData.temperature, SensorsData.humidity, SensorsData.pressure, SensorsData.battery_level))
            file.close()
        elif not NetworkData.is_connected:
            print('| {} | {: <16.2f} | {: <12.2f} | {: <14.2f} | {: <17d} |'.format(
                display_time, SensorsData.temperature, SensorsData.humidity, SensorsData.pressure, SensorsData.battery_level))

        sleep(4)
