import random
import src.distributions as dist
import src.constants as const

from src.helper import time_str


def next_arrive(time, last_interval, size):
    curr_interval = None
    if last_interval[0] <= time < last_interval[1]:
        curr_interval = last_interval
    else:
        for interval in const.INTERVAL_RANGES:
            if interval[0] <= time < interval[1]:
                curr_interval = interval
                break
    if curr_interval == None:
        return None
    miu, squad_ro = const.NORMAL_PARAMETERS[(
        size, curr_interval)]
    dtime = dist.normal(miu, squad_ro)
    return Ship(size, time + dtime, time + dtime) if time + dtime < const.FINAL_TIME else None


class Ship:
    def __init__(self, size, arrival_time, arrival_time_to_channel):
        assert size in const.POSSIBLE_SIZES
        #
        self.arrival_time_to_channel = arrival_time_to_channel
        self.arrival_time = arrival_time
        self.waiting_time = 0
        self.size = size
        self.finished = 0

    def __str__(self):
        return 'Ship(size: {}, arrival_t: {})'.format(self.size, time_str(self.arrival_time))
    __repr__ = __str__

    def __lt__(self, other):
        return self.arrival_time < other.arrival_time
