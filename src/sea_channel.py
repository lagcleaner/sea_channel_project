import src.distributions as dist
import src.constants as const

from heapq import heappush, heappop, heapify
from src.container import Dike
from src.ship import next_arrive, Ship
from src.dispatcher import onEvent, on
from src.events import (Event,
                        EnqueueToDike,
                        ExitShipsFromChannel,
                        ExitShipsFromDike,
                        OpenDikeEntryGates,
                        ShipArriveToChannel,
                        TransportThroughDike,
                        TransportShipsInsideDike)


def generate_arrivals_for(ship_size):
    arrivals = []
    time = 0

    interval = const.INTERVAL_RANGES[0]
    ship = next_arrive(
        time,
        interval,
        ship_size,
    )
    while not (ship is None):
        time = ship.arrival_time
        heappush(arrivals, ShipArriveToChannel(ship, ship.arrival_time))
        ship = next_arrive(
            time,
            interval,
            ship_size,
        )
    return arrivals


class SeaChannelEventsLoopHandler:
    """
    Assuming as initial time `t = 0` and final time `t = 520` in minutes

    this style can be easily convertible to hours style as fallows:
    `[(t + 520) // 60 ] hours and [t % 60] minutes`
    """

    def __init__(self, number_of_dikes=5):
        self.time = const.INITIAL_TIME
        self.ships_exited = []
        self.dikes = [
            Dike(identifier="#" + str(i))
            for i in range(number_of_dikes)
        ]
        self.events: list = self.initial_events()

    def initial_events(self):
        arrivals = []
        for size in const.POSSIBLE_SIZES:
            arrivals += generate_arrivals_for(size)
        heapify(arrivals)
        return arrivals

    def event_loop(self):
        while any(self.events):
            event = self.next_event()
            self.time = event.time
            yield event
            self.handle(event)

    def next_event(self):
        return heappop(self.events)

    def add_event(self, event: Event):
        heappush(self.events, event)

    @on('event')
    def handle(self, event):
        pass

    @onEvent(ShipArriveToChannel)
    def handle(self, event: ShipArriveToChannel):
        self.add_event(
            EnqueueToDike(
                self.dikes[0],
                event.ship,
                self.time),
        )

    @onEvent(EnqueueToDike)
    def handle(self, event: EnqueueToDike):
        # continue functioning until the channel is empty,
        #  but don't recieve more visitor at the entrance
        if self.time <= const.FINAL_TIME or event.dike != self.dikes[0]:
            # Phase 0
            heappush(event.dike.ships_queue, event.ship)
            if event.dike.state == const.DIKE_STATE_EMPTY:
                self.add_event(OpenDikeEntryGates(event.dike, self.time))

    @onEvent(OpenDikeEntryGates)
    def handle(self, event: OpenDikeEntryGates):
        if event.dike.state == const.DIKE_STATE_EMPTY and any(event.dike.ships_queue):
            # Phase 1
            event.dike.state = const.DIKE_STATE_BUSY
            curr_time = self.time
            event.dike.register_ships(curr_time)
            open_entrance_time = dist.exponential(4)
            for ship in event.dike.ships_registred_to_in:
                # (time awaited per a ship) = (time of registration to pass through) - (arrival time to the current dike)
                ship.waiting_time += curr_time - ship.arrival_time
            time = curr_time + open_entrance_time
            self.add_event(TransportShipsInsideDike(event.dike, time))

    @onEvent(TransportShipsInsideDike)
    def handle(self, event: TransportShipsInsideDike):
        if event.dike.state == const.DIKE_STATE_BUSY:
            # Phase 1
            time = self.time
            success = True
            for ship in event.dike.ships_registred_to_in:
                time += dist.exponential(2)
                success &= event.dike.enter_ship(ship)
            assert success, "something wrong ocurred entering ships to dike"
            self.add_event(TransportThroughDike(event.dike, time))

    @onEvent(TransportThroughDike)
    def handle(self, event: TransportThroughDike):
        if event.dike.state == const.DIKE_STATE_BUSY:
            # Phase 2
            time = self.time
            transporting_time = dist.exponential(7)
            time += transporting_time
            self.add_event(ExitShipsFromDike(event.dike, time))

    @onEvent(ExitShipsFromDike)
    def handle(self, event: ExitShipsFromDike):
        if event.dike.state == const.DIKE_STATE_BUSY:
            # Phase 3
            time = self.time
            count_ships_inside = len(event.dike.ships_inside)
            time_to_exit = sum(
                dist.exponential(3/2)
                for _ in range(count_ships_inside)
            )
            time += time_to_exit
            #
            if event.dike == self.dikes[-1]:
                for ship in event.dike.ships_inside:
                    ship.finished = time
                self.add_event(ExitShipsFromChannel(
                    event.dike.ships_inside.copy(), time))
            else:
                next_dique = self.dikes[self.dikes.index(event.dike) + 1]
                # enqueue in the next dike the ships exited
                for ship in event.dike.ships_inside:
                    ship.arrival_time = time
                    self.add_event(EnqueueToDike(next_dique, ship, time))
            # prepare the empty dike for recive ships
            event.dike.prepare_inside()
            # open gates if there is any ship on the entry
            self.add_event(OpenDikeEntryGates(event.dike, time))

    @onEvent(ExitShipsFromChannel)
    def handle(self, event: ExitShipsFromChannel):
        self.ships_exited.extend(event.ships_exiting)
        # store exited ships to take statistics from his times
        # TODO: MAKE THIS STUFF
