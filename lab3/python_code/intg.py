#!/usr/bin/env python3
from ev3dev.ev3 import LargeMotor
from ev3dev.ev3 import PowerSupply as ps
import time

motorA = LargeMotor('outA')
angle_final = 400
startPos = motorA.position

motorA.position = 0
max_voltage = ps().measured_volts
kp = 0.5
ki = 0.06
kd = 0
name = "intg_coef_" + str(kp) + str(ki) + str(kd)
file = open(name, "w")
e_prev = 150
ei = 0
time_start = time.time()
timePrev = time_start
while True:
    timeNow = time.time()-time_start
    angle_now = motorA.position
    e = angle_final - angle_now
    de = (e - e_prev) / (timeNow - timePrev)
    ei += e * (timeNow - timePrev)

    voltage = kp * e + ki * ei + kd * de

    if voltage > 100:
        voltage = 100
    elif voltage < -100:
        voltage = -100
    motorA.run_direct(duty_cycle_sp=voltage)
    e_prev = e
    timePrev = timeNow
    file.write(str(timeNow) + " " + str(motorA.position) + " " + str(motorA.speed) + "\n")
    if timeNow > 5:
        break
file.close()

