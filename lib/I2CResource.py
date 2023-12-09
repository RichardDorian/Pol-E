from machine import I2C


class I2CResource:
    def __init__(self, i2c: I2C, address: int, address_size: int = 8) -> None:
        I2CResource.is_valid_address(address)
        I2CResource.is_valid_address_size(address_size)

        self.i2c = i2c
        self.address = address
        self.address_size = address_size

    def write_to_memory(self, address: int, buffer: int, *, address_size: int = None) -> None:
        if not address_size is None:
            I2CResource.is_valid_address_size(address_size)
        address_size = self.address_size if address_size is None else address_size

        self.i2c.writeto_mem(self.address, address,
                             buffer, addrsize=address_size)

    def read_from_memory(self, address: int, length: int, *, address_size: int = None) -> list[int]:
        if not address_size is None:
            I2CResource.is_valid_address_size(address_size)
        address_size = self.address_size if address_size is None else address_size

        return self.i2c.readfrom_mem(self.address, address, length, addrsize=address_size)

    @staticmethod
    def is_valid_address(address: int, return_value: bool = False):
        valid = 0x00 <= address <= 0x7f

        if return_value:
            return valid
        elif not valid:
            raise ValueError(
                "Address must be between 0 and 127, received " + str(address))

    @staticmethod
    def is_valid_address_size(address_size: int, return_value: bool = False):
        valid = address_size in [8, 16]

        if return_value:
            return valid
        elif not valid:
            raise ValueError(
                "Address size must be either 8 or 16, received " + str(address_size))
