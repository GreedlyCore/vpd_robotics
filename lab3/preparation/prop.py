#!/usr/bin/env python3
from ev3dev.ev3 import LargeMotor
from ev3dev.ev3 import PowerSupply as ps
import time

motorA = LargeMotor('outA')
angle_final = 180
startPos = motorA.position

motorA.position = 0
timeStart = time.time()
max_voltage = ps().measured_volts
# kp = 10  # set random int value for result
# for kp in range(1, 20, 1):
#     kp = kp/10
kp = 0.6
name = "prop_coef_" + str(kp)
file = open(name, "w")
while True:
    angle_now = motorA.position
    # voltage = (kp * (angle_final - angle_now) / max_voltage) * 100
    voltage = kp * (angle_now - angle_final)
    if voltage > 100:
        voltage = 100
    elif voltage < -100:
        voltage = -100
    motorA.run_direct(duty_cycle_sp=voltage)
    timeNow = time.time() - timeStart
    file.write(str(timeNow) + " " + str(motorA.position) + " " + str(motorA.speed) + "\n")
    if timeNow > 10:
        break
timeStart = time.time()
file.close()

# except Exception as e:
#     raise e
# finally:
#     motorA.stop(stop_action='brake')
#     file.close()
