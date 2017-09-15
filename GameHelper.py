
from math import sqrt, pi

def calcDistance(point1, point2):
    return sqrt((point2.x - point1.x) ** 2 + (point2.y - point1.y) ** 2)

def calcDeltaOnShortestTurnAngle(desiredAngleRad, actualAngleRad):
    deltaRad = desiredAngleRad - actualAngleRad
    if deltaRad > pi:
        deltaRad -= 2 * pi
    elif deltaRad < -pi:
        deltaRad += 2 * pi
    return deltaRad

def limitToUInt8(value):
    if value > 255:
        return 255
    elif value < 0:
        return 0
    else:
        return value;
