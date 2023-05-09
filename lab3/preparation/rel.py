#!/usr/bin/env python3
from ev3dev.ev3 import LargeMotor
import time

motorA = LargeMotor('outA')
angle_final = 180
voltage = 100
motorA.position = 0
try:
    file = open("rele_reg15", "w")
    timeStart = time.time()
    while True:
        if motorA.position > angle_final:
            voltage = -100
        elif motorA.position < angle_final:
            voltage = 100
        else:
            voltage = 0

        motorA.run_direct(duty_cycle_sp=voltage)
        timeNow = time.time() - timeStart
        file.write(str(timeNow) + " " + str(motorA.position) + " " + str(motorA.speed) + "\n")
        if timeNow > 15:
            break
    file.close()




except Exception as e:
    raise e
finally:
    motorA.stop(stop_action='brake')
    file.close()
