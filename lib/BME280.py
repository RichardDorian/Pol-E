from time import sleep

from micropython import const
from machine import I2C

from I2CResource import I2CResource
from ntime import get_time_ms


class BME280(I2CResource):
    I2C_ADDRESS = const(0x77)

    NO_OVERSAMPLING = const(0b000)
    OVERSAMPLING_1X = const(0b001)
    OVERSAMPLING_2X = const(0b010)
    OVERSAMPLING_4X = const(0b011)
    OVERSAMPLING_8X = const(0b0100)
    OVERSAMPLING_16X = const(0b101)

    MODE_SLEEP = const(0x00)
    MODE_FORCED = const(0x01)
    MODE_NORMAL = const(0x03)

    HUMIDITY_CTRL_ADDRESS = const(0xf2)
    CONFIG_ADDRESS = const(0xf3)
    MEASURE_CTRL_ADDRESS = const(0xf4)

    TP_CALIBRATION_DATA_ADDRESS = const(0x88)
    TP_CALIBRATION_DATA_LENGTH = const(26)
    H_CALIBRATION_DATA_ADDRESS = const(0xe1)
    H_CALIBRATION_DATA_LENGTH = const(7)

    DATA_ADDRESS = const(0xf7)
    DATA_LENGTH = const(8)

    CACHE_TTL_MS = const(500)

    PRESSURE_CORRECTION = const(500)

    def __init__(self, i2c: I2C, address: int = I2C_ADDRESS, oversampling: tuple[int, int, int] = (OVERSAMPLING_16X, OVERSAMPLING_16X, OVERSAMPLING_16X)):
        super().__init__(i2c, address)

        for oversampling_value in oversampling:
            BME280.is_valid_oversampling(oversampling_value)

        self.pressure_oversampling = oversampling[0]
        self.temperature_oversampling = oversampling[1]
        self.humidity_oversampling = oversampling[2]

        self.config_filter = 0x01
        self.standby_time = 0x02
        self.mode = BME280.MODE_NORMAL

        config = (self.config_filter << 2) | (self.standby_time << 5)
        measure_ctrl = self.mode | (self.pressure_oversampling << 2) | (
            self.temperature_oversampling << 5)

        self.write_to_memory(BME280.HUMIDITY_CTRL_ADDRESS,
                             self.humidity_oversampling)
        self.write_to_memory(BME280.CONFIG_ADDRESS, config)
        self.write_to_memory(BME280.MEASURE_CTRL_ADDRESS, measure_ctrl)

        self._cached_data = None
        self._cached_data_time = 0

    def calibrate(self):
        buffer = self.read_from_memory(
            BME280.TP_CALIBRATION_DATA_ADDRESS, BME280.TP_CALIBRATION_DATA_LENGTH)
        sleep(0.004)  # is this really needed?
        self.dig_T1 = buffer[1] << 8 | buffer[0]
        self.dig_T2 = buffer[3] << 8 | buffer[2]
        self.dig_T2 = self.to_signed_int16(self.dig_T2)
        self.dig_T3 = buffer[5] << 8 | buffer[4]
        self.dig_T3 = self.to_signed_int16(self.dig_T3)
        self.dig_P1 = buffer[7] << 8 | buffer[6]
        self.dig_P2 = (buffer[9] << 8 | buffer[8])
        self.dig_P2 = self.to_signed_int16(self.dig_P2)
        self.dig_P3 = buffer[11] << 8 | buffer[10]
        self.dig_P3 = self.to_signed_int16(self.dig_P3)
        self.dig_P4 = buffer[13] << 8 | buffer[12]
        self.dig_P4 = self.to_signed_int16(self.dig_P4)
        self.dig_P5 = buffer[15] << 8 | buffer[14]
        self.dig_P5 = self.to_signed_int16(self.dig_P5)
        self.dig_P6 = buffer[17] << 8 | buffer[16]
        self.dig_P6 = self.to_signed_int16(self.dig_P6)
        self.dig_P7 = buffer[19] << 8 | buffer[18]
        self.dig_P7 = self.to_signed_int16(self.dig_P7)
        self.dig_P8 = buffer[21] << 8 | buffer[20]
        self.dig_P8 = self.to_signed_int16(self.dig_P8)
        self.dig_P9 = buffer[23] << 8 | buffer[22]
        self.dig_H1 = buffer[25]

        buffer = self.read_from_memory(
            BME280.H_CALIBRATION_DATA_ADDRESS, BME280.H_CALIBRATION_DATA_LENGTH)
        sleep(0.004)  # is this really needed?
        self.dig_H2 = buffer[1] << 8 | buffer[0]
        self.dig_H2 = self.to_signed_int16(self.dig_H2)
        self.dig_H3 = buffer[2]
        self.dig_H4 = buffer[3] << 4 | buffer[4]
        self.dig_H4 = self.to_signed_int16(self.dig_H4)
        self.dig_H5 = buffer[4] >> 4 | buffer[5] << 4
        self.dig_H5 = self.to_signed_int16(self.dig_H5)
        self.dig_H6 = buffer[6]
        self.dig_H6 = self.to_signed_int8(self.dig_H6)

    def retrieve_raw_measurements(self, force: bool = False) -> None:
        if force:
            self._cached_data = self.read_from_memory(
                BME280.DATA_ADDRESS, BME280.DATA_LENGTH)
            return
        sleep(0.004)

        current_time = get_time_ms()
        if self._cached_data is None or (current_time - self._cached_data_time) > BME280.CACHE_TTL_MS:
            self._cached_data = self.read_from_memory(
                BME280.DATA_ADDRESS, BME280.DATA_LENGTH)
            self._cached_data_time = current_time

    def measure_raw_temperature(self):
        self.retrieve_raw_measurements()
        sleep(0.004)  # is this really needed?
        return (self._cached_data[3] << 12) | (self._cached_data[4] << 4) | (self._cached_data[5] >> 4)

    def measure_raw_pressure(self):
        self.retrieve_raw_measurements()
        sleep(0.004)  # is this really needed?
        return (self._cached_data[0] << 12) | (self._cached_data[1] << 4) | (self._cached_data[2] >> 4)

    def measure_raw_humidity(self):
        self.retrieve_raw_measurements()
        sleep(0.004)  # is this really needed?
        return (self._cached_data[6] << 8) | self._cached_data[7]

    def get_temperature_measurement(self) -> float:
        var1 = 0.0
        var2 = 0.0
        temperature = 0.0
        temperature_min = 0.0
        temperature_max = 85.0
        self.t_fine = 0.0

        u_data_temp = self.measure_raw_temperature()
        var1 = float(u_data_temp) / 16384.0 - float(self.dig_T1) / 1024.0
        var1 = var1 * float(self.dig_T2)
        var2 = (float(u_data_temp) / 131072.0) - (float(self.dig_T1) / 8192.0)
        var2 = var2 * var2 * (float(self.dig_T3))
        self.t_fine = (var1 + var2)
        temperature = (var1 + var2) / 5120.0
        if (temperature < temperature_min):
            temperature = temperature_min
        elif (temperature > temperature_max):
            temperature = temperature_max
        return temperature

    def get_pressure_measurement(self) -> float:
        var1 = 0.0
        var2 = 0.0
        var3 = 0.0
        p = 0.0
        pression_min = 30000.0
        pression_max = 110000.0

        u_data_press = self.measure_raw_pressure()
        var1 = self.t_fine / 2.0 - 64000.0
        var2 = var1 * var1 * float(self.dig_P6) / 32768.0
        var2 = var2 + var1 * float(self.dig_P5) * 2.0
        var2 = (var2 / 4.0) + (float(self.dig_P4) * 65536.0)
        var3 = float(self.dig_P3) * var1 * var1 / 524288.0
        var1 = (var3 + float(self.dig_P2) * var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * float(self.dig_P1)

        if (var1):
            p = 1048576.0 - float(u_data_press)
            p = (p - (var2 / 4096.0)) * 6250.0 / var1
            var1 = float(self.dig_P9) * p * p / 2147483648.0
            var2 = p * float(self.dig_P8) / 32768.0
            p = (p + (var1 + var2 + float(self.dig_P7)) / 16.0)
            p = (p + BME280.PRESSURE_CORRECTION)
            if (p < pression_min):
                p = pression_min
            elif (p > pression_max):
                p = pression_max
        else:
            p = 0.0
        return p / 100.0

    def get_humidity_measurement(self) -> float:
        humidity_min = 0.0
        humidity_max = 100.0
        var1 = 0.0
        var2 = 0.0
        var3 = 0.0
        var4 = 0.0
        var5 = 0.0
        var6 = 0.0

        u_data_hum = self.measure_raw_humidity()
        var1 = float(self.t_fine) - 76800.0
        var2 = (float(self.dig_H4) * 64.0) + \
            ((float(self.dig_H5) / 16384.0) * var1)
        var3 = u_data_hum - var2
        var4 = float(self.dig_H2) / 65536.0
        var5 = (1.0 + ((float(self.dig_H3)) / 67108864.0) * var1)
        var6 = 1.0 + ((float(self.dig_H6)) / 67108864.0) * var1 * var5
        var6 = var3 * var4 * (var5 * var6)
        humidity = var6 * (1.0 - float(self.dig_H1) * var6 / 524288.0)
        if (humidity > humidity_max):
            humidity = humidity_max
        elif (humidity < humidity_min):
            humidity = humidity_min
        return humidity

    @staticmethod
    def to_signed_int16(value: int) -> int:
        return value - 0xffff - 1 if value >= (0x8000) else value

    @staticmethod
    def to_signed_int8(value: int) -> int:
        return value - 0xff - 1 if value >= 0x80 else value

    @staticmethod
    def is_valid_oversampling(oversampling: int, return_value: bool = False):
        valid = oversampling in [BME280.NO_OVERSAMPLING, BME280.OVERSAMPLING_1X, BME280.OVERSAMPLING_2X,
                                 BME280.OVERSAMPLING_4X, BME280.OVERSAMPLING_8X, BME280.OVERSAMPLING_16X]

        if return_value:
            return valid
        elif not valid:
            raise ValueError(
                "Oversampling must be either 0, 1, 2, 3, 4, 5 received " + str(oversampling))
