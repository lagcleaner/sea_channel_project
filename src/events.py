import src.constants as const
import src.distributions as dist

from src.container import Dike
from src.helper import time_str
from src.ship import Ship
from src.dispatcher import onEvent
from src.ship import next_arrive
from heapq import heapify, heappush, heappop


class Event:
    PRIORITY = 0

    def __init__(self, time):
        self.time = time

    def __lt__(self, other):
        if self.time != other.time:
            return self.time < other.time
        else:
            return self.PRIORITY < other.PRIORITY


class ShipArriveToChannel(Event):
    PRIORITY = 1

    def __init__(self, ship: Ship, time):
        super().__init__(time)
        self.ship = ship

    def __str__(self):
        return "[{}] : ShipArriveToChannel(ship: (arrived_at: {}, size: {}))".format(time_str(self.time), self.ship.arrival_time, self.ship.size)
    __repr__ = __str__


class EnqueueToDike(Event):
    PRIORITY = 2

    def __init__(self, dike: Dike, ship: Ship, time):
        super().__init__(time)
        self.dike = dike
        self.ship = ship

    def __str__(self):
        return "[{}] : EnqueueToDike(dike: {}, ship: arrived_at({}))".format(time_str(self.time), self.dike.identifier, self.ship.arrival_time)
    __repr__ = __str__


class OpenDikeEntryGates(Event):
    PRIORITY = 3

    def __init__(self, dike: Dike, time):
        super().__init__(time)
        self.dike = dike

    def __str__(self):
        return "[{}] : OpenDikeEntryGates(dike: {})".format(time_str(self.time), self.dike.identifier)
    __repr__ = __str__


class TransportShipsInsideDike(Event):
    PRIORITY = 4

    def __init__(self, dike: Dike, time):
        super().__init__(time)
        self.dike = dike

    def __str__(self):
        return "[{}] : TransportShipsInsideDike(dike: {}, ships_registred: {})".format(time_str(self.time), self.dike.identifier, self.dike.ships_registred_to_in)
    __repr__ = __str__


class TransportThroughDike(Event):
    PRIORITY = 5

    def __init__(self, dike: Dike, time):
        super().__init__(time)
        self.dike = dike

    def __str__(self):
        return "[{}] : TransportInDike(dike: {})".format(time_str(self.time), self.dike.identifier)
    __repr__ = __str__


class ExitShipsFromDike(Event):
    PRIORITY = 6

    def __init__(self, dike: Dike, time):
        super().__init__(time)
        self.dike = dike

    def __str__(self):
        return "[{}] : ExitShipsFromDike(dike: {} amount: {})".format(time_str(self.time), self.dike.identifier, len(self.dike.ships_inside))
    __repr__ = __str__


class ExitShipsFromChannel(Event):
    PRIORITY = 7

    def __init__(self, ships_exiting: set, time):
        super().__init__(time)
        self.ships_exiting = ships_exiting

    def __str__(self):
        return "[{}] : ExitShipsFromChannel(amount: {})".format(time_str(self.time), len(self.ships_exiting))
    __repr__ = __str__
