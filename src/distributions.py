import random
from math import log, sqrt


def exponential(lam):
    u = random.random()
    return -1 / lam * log(u)


def normal01():
    y = 0
    while y <= 0:
        y1, y2 = exponential(1), exponential(2)
        y = (y2 - (y1 - 1) ** 2) / 2
    u = random.random()
    return y if u < 1/2 else -y


def normal(miu, squad_ro):
    return normal01() * sqrt(squad_ro) + miu
