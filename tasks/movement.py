from time import sleep
from math import cos, pi

from DRV8833 import DRV8833

from tasks.network import register_packet_handler
from tasks.sensors import SensorsData


class MovementData:
    autonomous = True
    max_autonomous_speed = 0.90
    reduced_autonomous_speed = 0.85
    rotation_speed = 0.80
    speed_delta_percent = 3

    complete_turn_treshold = int(115 / cos(pi/6))
    small_turn_treshold = int(75 / cos(pi/3))
    rotation_time = 0.2


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

    def rotate_left(waiting_time_coef: float = 1) -> None:
        set_speed(MovementData.rotation_speed)
        left_motor.set_direction(DRV8833.REVERSE)
        right_motor.set_direction(DRV8833.FORWARD)
        sleep(MovementData.rotation_time * waiting_time_coef)
        left_motor.set_direction(DRV8833.FORWARD)
        right_motor.set_direction(DRV8833.FORWARD)

    def rotate_right(waiting_time_coef: float = 1) -> None:
        set_speed(MovementData.rotation_speed)
        left_motor.set_direction(DRV8833.FORWARD)
        right_motor.set_direction(DRV8833.REVERSE)
        sleep(MovementData.rotation_time * waiting_time_coef)
        left_motor.set_direction(DRV8833.FORWARD)
        right_motor.set_direction(DRV8833.FORWARD)

    # def rotation_sequence() -> None:
        # set_speed(MovementData.rotation_speed)

        # # We go back a few mms
        # left_motor.set_direction(DRV8833.REVERSE)
        # right_motor.set_direction(DRV8833.REVERSE)
        # sleep(0.3)

        # rotate_left()
        # if not SensorsData.left_is_object_detected and not SensorsData.right_is_object_detected:
        #     return

        # rotate_left()
        # if not SensorsData.left_is_object_detected and not SensorsData.right_is_object_detected:
        #     return

        # rotate_right(3)
        # if not SensorsData.left_is_object_detected and not SensorsData.right_is_object_detected:
        #     return

        # rotate_right()
        # if not SensorsData.left_is_object_detected and not SensorsData.right_is_object_detected:
        #     return

        # rotate_right(2)
        # if not SensorsData.left_is_object_detected and not SensorsData.right_is_object_detected:
        #     return

    def rotation_sequence(start_left: bool) -> None:
        rotate = rotate_left if start_left else rotate_right
        while SensorsData.left_is_object_detected and SensorsData.right_is_object_detected:
            rotate()

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
                if SensorsData.left_distance > MovementData.complete_turn_treshold or SensorsData.right_distance > MovementData.complete_turn_treshold:
                    set_speed(MovementData.reduced_autonomous_speed)
                else:
                    rotation_sequence(SensorsData.left_distance >
                                      SensorsData.right_distance)

            elif SensorsData.left_distance < MovementData.small_turn_treshold or SensorsData.right_distance < MovementData.small_turn_treshold:
                if SensorsData.left_is_object_detected:
                    rotate_right(0.6)
                elif SensorsData.right_is_object_detected:
                    rotate_left(0.6)

            else:
                set_speed(MovementData.max_autonomous_speed)

        # Manual override (commands coming from the computer)
        else:
            pass
