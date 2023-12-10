from time import sleep

from machine import I2C
from micropython import const

from VL6180X import VL6180X
from BME280 import BME280
from ntime import get_time_ms
import battery


class SensorsData:
    gathering_light_data = False

    left_is_object_detected = False
    right_is_object_detected = False

    left_distance = 0
    right_distance = 0

    ambient_light = 0.0

    temperature = 0.0
    humidity = 0.0
    pressure = 0.0

    battery_level = 0


def SensorsThread():
    # Distance sensors de-init
    VL6180X.deactivate_gpio('P3')
    VL6180X.deactivate_gpio('P5')

    # I2C
    i2c_bus = I2C(0)
    i2c_bus.init(I2C.MASTER, baudrate=400000)

    # Distance & ambient light sensors
    left_sensor_pin = VL6180X.activate_gpio('P3')
    left_sensor = VL6180X(i2c_bus, VL6180X.DEFAULT_ADDRESS)
    left_sensor.change_address(left_sensor_pin, 0x2a)

    middle_sensor_pin = VL6180X.activate_gpio('P5')
    middle_sensor = VL6180X(i2c_bus, VL6180X.DEFAULT_ADDRESS)
    middle_sensor.change_address(middle_sensor_pin, 0x2b)

    # Temperature, humidity and pressure sensor
    bme280 = BME280(i2c_bus)
    bme280.calibrate()

    # Time settings (we want the distance sensors to run all the time and the others to run every 500ms)
    last_data_dump_time = 0
    other_sensors_interval = const(2 * 1000)
    light_data_dump_interval = const(30 * 1000)

    while True:
        SensorsData.left_is_object_detected = left_sensor.is_object_detected()
        SensorsData.right_is_object_detected = middle_sensor.is_object_detected()

        SensorsData.left_distance = left_sensor.get_measured_distance()
        SensorsData.right_distance = middle_sensor.get_measured_distance()

        now = get_time_ms()

        if (last_data_dump_time + other_sensors_interval) <= now:

            SensorsData.temperature = bme280.get_temperature_measurement() - 4
            SensorsData.humidity = bme280.get_humidity_measurement()
            SensorsData.pressure = bme280.get_pressure_measurement()

            SensorsData.battery_level = battery.get_battery_level()

            if (last_data_dump_time + light_data_dump_interval) <= now:
                SensorsData.gathering_light_data = True
                # Let other threads know that we are gathering light data
                sleep(0.1)
                SensorsData.ambient_light = middle_sensor.measure_raw_ambient_light()
                SensorsData.gathering_light_data = False

            last_data_dump_time = now

        sleep(0.001)  # Wait 1ms to let other threads run
