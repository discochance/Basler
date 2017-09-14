
from math import sqrt

def calcDistance(point1, point2):
    return sqrt((point2.x - point1.x)**2 + (point2.y - point1.y)**2)