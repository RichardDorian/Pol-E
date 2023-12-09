from machine import RTC
from time import mktime, localtime

rtc = RTC(0)
if not rtc.synced():
    rtc.init((2023, 12, 11, 8, 30, 0, 0, 0), RTC.XTAL_32KHZ)


def pretty_print_time(time: tuple | int) -> str:
    if type(time) is int:
        time = localtime(time)
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep',
              'Oct', 'Nov', 'Dec']
    return '{} {:0>2} {} {:0>2}:{:0>2}:{:0>2}'.format(months[time[1]-1], time[2], time[0], time[3], time[4], time[5])


def get_time_us() -> int:
    time = rtc.now()
    us = time[6]
    return int(mktime(time))*1000000 + us


def get_time_ms() -> int:
    time = rtc.now()
    ms = time[6] // 1000
    return int(mktime(time))*1000 + ms


def get_time() -> int:
    time = rtc.now()
    return int(mktime(time))
