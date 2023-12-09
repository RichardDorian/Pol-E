from micropython import const
from machine import Pin, PWM


class DRV8833:
    FORWARD = const(0)
    REVERSE = const(1)

    TIMER = const(1)
    FREQUENCY = const(500)

    def __init__(self, pin_1: str, pin_2: str, sleep_pin: Pin, pwm_channel_1: int, pwm_channel_2: int) -> None:
        self.sleep_pin = sleep_pin
        self.sleep_pin.value(0)

        self.direction = DRV8833.FORWARD
        self.speed = 0

        pwm = PWM(DRV8833.TIMER, DRV8833.FREQUENCY)
        self.pwm_1 = pwm.channel(pwm_channel_1, pin=pin_1, duty_cycle=0)
        self.pwm_2 = pwm.channel(pwm_channel_2, pin=pin_2, duty_cycle=0)

        self.enable()

    def enable(self) -> None:
        self.sleep_pin.value(1)

    def disable(self) -> None:
        self.sleep_pin.value(0)

    def stop(self) -> None:
        self.pwm_1.duty_cycle(0)
        self.pwm_2.duty_cycle(0)

    def set_direction(self, direction: int) -> None:
        DRV8833.is_valid_direction(direction)

        self.direction = direction
        self.set_speed(self.speed)

    def set_speed(self, speed: float) -> None:
        DRV8833.is_valid_speed(speed)

        if self.direction == DRV8833.FORWARD:
            self.pwm_1.duty_cycle(0)
            self.pwm_2.duty_cycle(speed)
        elif self.direction == DRV8833.REVERSE:
            self.pwm_2.duty_cycle(0)
            self.pwm_1.duty_cycle(speed)

        self.speed = speed

    @staticmethod
    def is_valid_speed(speed: float, return_value: bool = False):
        valid = 0 <= speed <= 1

        if return_value:
            return valid
        elif not valid:
            raise ValueError(
                "Speed must be between 0 and 1, received " + str(speed))

    @staticmethod
    def is_valid_direction(direction: int, return_value: bool = False):
        valid = direction in [DRV8833.FORWARD, DRV8833.REVERSE]

        if return_value:
            return valid
        elif not valid:
            raise ValueError(
                "Direction must be either DRV8833.FORWARD or DRV8833.REVERSE, received " + str(direction))

    @staticmethod
    def get_right_motor():
        sleep_pin = Pin('P20', mode=Pin.OUT)
        return DRV8833('P22', 'P21', sleep_pin, 2, 3)

    @staticmethod
    def get_left_motor():
        sleep_pin = Pin('P20', mode=Pin.OUT)
        return DRV8833('P12', 'P19', sleep_pin, 0, 1)
