from src.ship import Ship
from src.constants import DIKE_STATE_BUSY, DIKE_STATE_EMPTY


class Dike:
    def __init__(self, identifier="", rows=2, slots_per_row=6):
        self._occuped_space: list = [[] for _ in range(rows)]
        self._slots_per_row: int = slots_per_row
        self._rows: int = rows
        self.identifier = identifier
        # ready for phase 1 or not
        self.state: int = DIKE_STATE_EMPTY
        # awaiting for enter
        self.ships_queue = []
        # for phase 2 and 3
        self.ships_inside = set()
        # for phase 1
        self.ships_registred_to_in = []

    def __occuped_spaces_str(self):
        for row in self._occuped_space:
            occup = sum(row)
            res += occup * '-' + (self._slots_per_row - occup) * ' '
            res += '\n'

    def __str__(self):
        return 'Dike(id: {}, inside: \n{}\n)'.format(self.identifier, self.__occuped_spaces_str())

    def register_ships(self, time):
        occuped = [0 for _ in range(self._rows)]
        assert self.ships_registred_to_in == [], "{}".format(
            self.ships_registred_to_in)
        is_full = False
        for ship in self.ships_queue:
            for i in range(self._rows):
                if ship.arrival_time <= time and occuped[i] + ship.size <= self._slots_per_row:
                    self.ships_registred_to_in.append(ship)
                    occuped[i] += ship.size
                    if sum(occuped) == self._slots_per_row * self._rows:
                        is_full = True
                    break
            if is_full:
                break
        for ship_reg in self.ships_registred_to_in:
            self.ships_queue.remove(ship_reg)
        return is_full

    def enter_ship(self, ship: [Ship]) -> bool:
        assert ship != None, "ship can't be None"
        for i in range(self._rows):
            if sum(self._occuped_space[i]) + ship.size <= self._slots_per_row and ship not in self.ships_inside:
                self.ships_inside.add(ship)
                self._occuped_space[i] += [ship.size]
                return True
        return False

    def prepare_inside(self):
        self.state = DIKE_STATE_EMPTY
        self._occuped_space = [[] for _ in range(self._rows)]
        self.ships_inside = set()
        self.ships_registred_to_in = []
