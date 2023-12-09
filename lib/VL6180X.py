from time import sleep

from micropython import const
from machine import I2C, Pin

from I2CResource import I2CResource


class VL6180X(I2CResource):
    DEFAULT_ADDRESS = const(0x29)
    ID_MODEL = const(0xb4)  # unused

    REG_IDENTIFICATION_MODEL_ID = const(0x000)  # unused
    REG_SYSTEM_INTERRUPT_CONFIG = const(0x014)
    REG_SYSTEM_INTERRUPT_CLEAR = const(0x015)
    REG_SYSTEM_FRESH_OUT_OF_RESET = const(0x016)
    REG_SYSRANGE_START = const(0x018)
    REG_SYSALS_START = const(0x038)
    REG_SYSALS_ANALOGUE_GAIN = const(0x03f)
    REG_SYSALS_INTEGRATION_PERIOD_HI = const(0x040)  # unused
    REG_SYSALS_INTEGRATION_PERIOD_LO = const(0x041)  # unused
    REG_RESULT_ALS_VAL = const(0x050)
    REG_RESULT_RANGE_VAL = const(0x062)
    REG_RESULT_RANGE_STATUS = const(0x04d)  # unused
    REG_RESULT_INTERRUPT_STATUS_GPIO = const(0x04f)  #  unused
    REG_I2C_SLAVE_DEVICE_ADDRESS = const(0x212)  #  unused

    ALS_GAIN_1 = const(0x46)
    ALS_GAIN_1_25 = const(0x45)
    ALS_GAIN_1_67 = const(0x44)
    ALS_GAIN_2_5 = const(0x43)
    ALS_GAIN_5 = const(0x42)
    ALS_GAIN_10 = const(0x41)
    ALS_GAIN_20 = const(0x40)
    ALS_GAIN_40 = const(0x47)

    def __init__(self, i2c: I2C, address: int) -> None:
        super().__init__(i2c, address, address_size=16)

        data_to_write = [
            (0x0207, 0x01), (0x0208, 0x01), (0x0096, 0x00), (0x0097, 0xfd),
            (0x00e3, 0x00), (0x00e4, 0x04), (0x00e5, 0x02), (0x00e6, 0x01),
            (0x00e7, 0x03), (0x00f5, 0x02), (0x00d9, 0x05), (0x00db, 0xce),
            (0x00dc, 0x03), (0x00dd, 0xf8), (0x009f, 0x00), (0x00a3, 0x3c),
            (0x00b7, 0x00), (0x00bb, 0x3c), (0x00b2, 0x09), (0x00ca, 0x09),
            (0x0198, 0x01), (0x01b0, 0x17), (0x01ad, 0x00), (0x00ff, 0x05),
            (0x0100, 0x05), (0x0199, 0x05), (0x01a6, 0x1b), (0x01ac, 0x3e),
            (0x01a7, 0x1f), (0x0030, 0x00), (0x010a, 0x30), (0x0031, 0xFF),
            (0x0040, 0x63), (0x002e, 0x01),

            (VL6180X.REG_SYSALS_ANALOGUE_GAIN, VL6180X.ALS_GAIN_1),
            (VL6180X.REG_SYSTEM_INTERRUPT_CONFIG, 0x24)
        ]

        for data in data_to_write:
            self.write_to_memory(data[0], data[1])

        self._cached_distance = None

    def change_address(self, pin: Pin, new_address: int) -> None:
        I2CResource.is_valid_address(new_address)
        if self.address == new_address:
            raise ValueError("Address is already " + str(self.address))

        pin.value(1)
        sleep(0.0015)  #  is this really needed?

        register_data = self.read_from_memory(
            VL6180X.REG_SYSTEM_FRESH_OUT_OF_RESET, 1)
        if register_data[0] == 0x01:
            self.write_to_memory(VL6180X.REG_SYSTEM_FRESH_OUT_OF_RESET, 0x00)
            self.write_to_memory(
                VL6180X.REG_I2C_SLAVE_DEVICE_ADDRESS, new_address)
            self.address = new_address

    def measure_raw_distance(self) -> int:
        self.write_to_memory(VL6180X.REG_SYSRANGE_START, 0x01)
        sleep(0.001)  # is this really needed?

        status = 0
        while status != 0x04:
            sleep(0.001)
            raw_status = self.read_from_memory(
                VL6180X.REG_RESULT_INTERRUPT_STATUS_GPIO, 1)
            status = raw_status[0] & 0x04

        distance = self.read_from_memory(VL6180X.REG_RESULT_RANGE_VAL, 1)
        self.write_to_memory(VL6180X.REG_SYSTEM_INTERRUPT_CLEAR, 0x07)
        return distance[0]

    def is_object_detected(self) -> bool:
        self._cached_distance = self.measure_raw_distance()
        return self._cached_distance != 255

    def get_measured_distance(self, *, force: bool = False) -> int:
        if force or self._cached_distance is None:
            self._cached_distance = self.measure_raw_distance()

        return self._cached_distance

    def measure_raw_ambient_light(self):
        self.write_to_memory(VL6180X.REG_SYSALS_START, 0x01)
        sleep(0.001)  # is this really needed?

        status = 0
        while status != 0x20:
            sleep(0.001)
            raw_status = self.read_from_memory(
                VL6180X.REG_RESULT_INTERRUPT_STATUS_GPIO, 1)
            status = raw_status[0] & 0x20

        als = self.read_from_memory(VL6180X.REG_RESULT_ALS_VAL, 2)
        self.write_to_memory(VL6180X.REG_SYSTEM_INTERRUPT_CLEAR, 0x07)

        return 0.32 * (als[0] << 8 | als[1])

    @staticmethod
    def deactivate_gpio(id: str) -> None:
        pin = Pin(id, mode=Pin.OUT)
        pin.value(0)

    @staticmethod
    def activate_gpio(id: str) -> Pin:
        pin = Pin(id, mode=Pin.OUT)
        pin.value(1)
        return pin
