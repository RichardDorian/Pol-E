from time import sleep
from math import cos, pi

from DRV8833 import DRV8833

from tasks.network import register_packet_handler
from tasks.sensors import SensorsData


class MovementData:
    autonomous = True
    max_autonomous_speed = 0.8
    reduced_autonomous_speed = 0.6
    rotation_speed = 0.4
    speed_delta_percent = 3

    slow_down_treshold = int(75 / cos(pi/6))


def MovementThread():
    def update_delta(new_delta: int) -> None:
        MovementData.speed_delta_percent = new_delta
    register_packet_handler(0x03, update_delta)

    left_motor = DRV8833.get_left_motor()
    right_motor = DRV8833.get_right_motor()

    left_motor.set_direction(DRV8833.FORWARD)
    right_motor.set_direction(DRV8833.FORWARD)

    def set_speed(speed: float) -> None:
        left_motor.set_speed(speed)
        right_motor.set_speed(
            speed - speed*MovementData.speed_delta_percent/100)

    def rotation_sequence(start_left: bool) -> None:
        left_motor.set_direction(DRV8833.REVERSE)
        right_motor.set_direction(DRV8833.REVERSE)

    while True:
        if SensorsData.gathering_light_data:
            # Light data gathering is very long, so we don't want to run the motors during this time
            set_speed(0)
            sleep(0.1)
            continue

        # Autonomous behavior
        if MovementData.autonomous:

            # Object in front of us
            if SensorsData.left_is_object_detected and SensorsData.right_is_object_detected:
                if SensorsData.left_distance > MovementData.slow_down_treshold or SensorsData.right_distance > MovementData.slow_down_treshold:
                    set_speed(MovementData.reduced_autonomous_speed)
                else:
                    rotation_sequence(SensorsData.left_distance >
                                      SensorsData.right_distance)

            else:
                set_speed(MovementData.max_autonomous_speed)

        # Manual override (commands coming from the computer)
        else:
            pass
