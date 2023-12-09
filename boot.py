import json
from time import sleep, localtime

import pycom
from machine import RTC
from network import WLAN, Bluetooth

from ntime import get_time_us, pretty_print_time

pycom.heartbeat(False)
pycom.rgbled(0x7f7f00)

# Disable bluetooth to save battery
bt = Bluetooth()
bt.deinit()


def wlan_connect(wlan: WLAN, wifi_config) -> bool:
    try:
        wlan.connect(
            wifi_config.get('ssid'),
            auth=(wifi_config.get('security'), wifi_config.get('password')),
            timeout=7500
        )

        while not wlan.isconnected():
            sleep(0.05)

        return wlan.isconnected()
    except:
        return False


def set_time():
    ntp_servers = ('time.google.com', 'pool.ntp.org')
    rtc = RTC(0)
    rtc.init((2023, 12, 11, 0, 0, 0, 0, 0), RTC.XTAL_32KHZ)
    rtc.ntp_sync(ntp_servers[0], backup_server=ntp_servers[1])
    while not rtc.synced():
        sleep(0.05)

    utc_plus_1_us = get_time_us() + 60 * 60 * 1000000
    utc_plus_1 = localtime(utc_plus_1_us // 1000000)
    rtc.init(
        (utc_plus_1[0], utc_plus_1[1], utc_plus_1[2], utc_plus_1[3],
         utc_plus_1[4], utc_plus_1[5], utc_plus_1_us % 1000000, 0),
        RTC.XTAL_32KHZ
    )

    print('Time synced (time: {}, main NTP server: {}, backup NTP server: {})'.format(
        pretty_print_time(rtc.now()), ntp_servers[0], ntp_servers[1]))


try:
    with open('/flash/wifi.conf') as file:
        wifi_configs = json.load(file)

    wlan = WLAN()
    wlan.init(mode=WLAN.STA)

    connected = False
    for wifi_config in wifi_configs:
        print('Connecting to WiFi network ({})...'.format(wifi_config.get('ssid')))
        success = wlan_connect(wlan, wifi_config)
        connected |= success
        if success:
            print('Wifi connected (ip address:' + wlan.ifconfig()[0] + ')')
            break
        else:
            print('Connection failed')

    set_time()

    print('Boot complete')
    pycom.rgbled(0x007f00)
    pycom.heartbeat(True)
except Exception as error:
    print('Boot failed')
    pycom.rgbled(0x7f0000)
    raise error
