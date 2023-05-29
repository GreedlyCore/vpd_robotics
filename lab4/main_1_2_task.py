import time
import math
from ev3dev2.motor import *
from ev3dev2.sound import Sound
from ev3dev2.button import Button
from ev3dev2.sensor import *
from ev3dev2.sensor.lego import *
from ev3dev2.sensor.virtual import *
from math import *
from ev3dev2.motor import OUTPUT_A, OUTPUT_B, LargeMotor
from ev3dev2 import *
from time import sleep
import math
from math import atan2, sqrt, pi, cos, sin
import time

class linear_controller:
    x_goal = 0
    y_goal = 0
    Ks = 0
    Kr = 0

    def __init__(self, coor, koefs):
        self.x_goal = coor[0]
        self.y_goal = coor[1]
        self.Ks = koefs[0]
        self.Kr = koefs[1]

    def get_azimuth(self, coords):
        return atan2((self.y_goal - coords[1]), (self.x_goal - coords[0]))

    def get_distance(self, coords):
        return sqrt((self.x_goal - coords[0]) ** 2 + (self.y_goal - coords[1]) ** 2)

    def get_U_linear(self, coords, theta):
        return self.Ks * self.get_distance(coords)

    def get_leading_angle(self, coords, theta):
        azimuth = self.get_azimuth(coords)
        angle = round(azimuth - theta, 1)
        if azimuth < -pi / 2:
            angle = round(azimuth - theta + 2 * pi, 1)
        return angle

    def get_U_angular(self, coords, theta):
        return self.Kr * self.get_leading_angle(coords, theta)

class non_linear_controller:
    x_goal = 0
    y_goal = 0
    K1 = 0
    K2 = 0

    def __init__(self, coor, koefs):
        self.x_goal = coor[0]
        self.y_goal = coor[1]
        self.K1 = koefs[0]
        self.K2 = koefs[1]

    def get_azimuth(self, coords):
        return round(atan2((self.y_goal - coords[1]), (self.x_goal - coords[0])))

    def get_distance(self, coords):
        return sqrt((self.x_goal - coords[0]) ** 2 + (self.y_goal - coords[1]) ** 2)

    def get_leading_angle(self, coords, theta):
        azimuth = self.get_azimuth(coords)
        angle = round(azimuth - theta, 1)
        if azimuth < -pi / 2:
            angle = round(azimuth - theta + 2 * pi, 1)
        return angle

    def get_U_linear(self, coords, theta):
        alpha = self.get_leading_angle(coords, theta)
        return self.K1 * self.get_distance(coords) * cos(alpha)

    def get_U_angular(self, coords, theta):
        alpha = self.get_leading_angle(coords, theta)
        return (self.K1 * cos(alpha) * sin(alpha)) + self.K2 * alpha
    

def set_U(U):
    if U >= 75:
        return 75
    if U <= -75:
        return -75
    else:
        return round(U)


motorA = LargeMotor(OUTPUT_A)
motorB = LargeMotor(OUTPUT_B)
left_motor = motorA
right_motor = motorB
pen_in5 = Pen(INPUT_5)
pen_in5.down()

DISTANCE_BETWEEN_WHEELS = 12.1 + 0.4 + 4  # in 'cm'
WHEEL_RADIUS = 3  # 2.8  # in "cm"

left_motor_pos = 0
right_motor_pos = 0
x = 0
y = 0
theta = 0


def update_coordinates():
    global left_motor_pos, right_motor_pos, x, y, theta
    left_cur_pos = left_motor.position
    right_cur_pos = right_motor.position

    left_dist = (left_cur_pos - left_motor_pos) * WHEEL_RADIUS * pi / 180
    right_dist = (right_cur_pos - right_motor_pos) * WHEEL_RADIUS * pi / 180
    left_motor_pos = left_cur_pos
    right_motor_pos = right_cur_pos

    distance = (left_dist + right_dist) / 2
    theta = (left_cur_pos - right_cur_pos) * (WHEEL_RADIUS / DISTANCE_BETWEEN_WHEELS) / 180 * pi
    x += distance * cos(theta)
    y += distance * sin(theta)


pair = [(6, 8), (12,14), (30,35)]
a, b, c, d = 70, 80, 60, 80
end_positions = ((a, 0), (0, b), (-c, 0), (0, -d))

i = 3
j = 0

robot = non_linear_controller(end_positions[i],pair[j])
start_time = time.time()
print("\n\n\n")
print("finish coords: ", end_positions[i])
print("coeffs: ", pair[j])

dist = robot.get_distance((0, 0))

while dist >= 4:
    update_coordinates()
    now = (x, y)
    dist = robot.get_distance((x, y))
    Ur = robot.get_U_angular(now, theta)
    Us = robot.get_U_linear(now, theta)
    motorA.on(set_U(set_U(Ur) + set_U(Us)))
    motorB.on(set_U(set_U(Us) - set_U(Ur)))

    param = dist ** 2 + robot.get_leading_angle(now, theta) ** 2
    time_now = round(time.time() - start_time, 1)
    print("{} {} {} {} {}".format(
        '%.2f' % round(x, 2),
        '%.2f' % round(y, 2),
        round(math.degrees(theta)),
        '%.2f' % round(param, 2),
        '%.2f' % round(time_now, 2)))

    if time_now > 40:
        break
    sleep(0.1)
print("stopped")
motorA.on(0)
motorB.on(0)
