from machine import ADC

adc = ADC()
voltage = adc.channel(attn=ADC.ATTN_11DB, pin='P16')


def get_battery_level() -> int:
    voltage = get_battery_voltage()
    estimation = 90.2256*voltage-273.59  # Linear model

    # We gotta cheat due to the poor accuracy of the linear model
    if estimation < 0:
        return 0
    if estimation > 100:
        return 100
    return round(estimation)


def get_battery_voltage() -> float:
    return voltage.voltage()*2000
