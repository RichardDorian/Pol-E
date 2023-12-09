from DRV8833 import DRV8833

from tasks.network import register_packet_handler


def MovementThread():
    left_motor = DRV8833.get_left_motor()
    right_motor = DRV8833.get_right_motor()

    def change_speed(delta: int) -> None:
        left_motor.set_speed(1)
        right_motor.set_speed(delta / 100)

    register_packet_handler(0x04, change_speed)

    left_motor.set_direction(DRV8833.FORWARD)
    right_motor.set_direction(DRV8833.FORWARD)

    left_motor.set_speed(1)
    right_motor.set_speed(1)
