# pylint: skip-file
"""Defines the Map class representing a simulation map.
"""
from item import Item
from threading import Lock, Event
import random
from itertools import chain


class Map():
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.arr = [[None]*(width) for _ in range(height)] #(row, col)
        self.members = {}
        self._species_counts = {}
        self.resources = {}
        self.empty_pos = set([(i,j) for i in range(height) for j in\
                                                                 range(width)])
        self.lock = Lock()
        self.game_over = False

    def __repr__(self):
        """Draw map interface for user"""
        rep = ''
        repfn = lambda o: ' ' if o == None else repr(o)
        for row in self.arr:
            rep += '  |  '.join([repfn(o) for o in row]) + '\n'
            rep += ('--'*(self.width+3*(self.width-1))) + '\n'
        return rep

    def markup(self):
        def intersperse(lst, item):
            result = [item] * (len(lst) * 2 - 1)
            result[0::2] = lst
            return result
        rep = []
        repfn = lambda o: [' '] if o == None else o.markup()
        for row in self.arr:
            rep += intersperse(list(chain.from_iterable(
                                [repfn(o) for o in row])), ' | ')
            rep.append('\n')
            rep += ('-'*(self.width+3*(self.width-1))) + '\n'
        return rep

    def __getitem__(self, pos):
        """Returns item at specific position"""
        return self.at(pos)

    def __contains__(self, item: Item):
        """Returns an item id of the passed in item
           If it is not an item, it returns False"""
        if item.type == 'member':
            return item.id in self.members
        elif item.type == 'resource':
            return item.id in self.resources
        else:
            return False

    def add_species_member(self, species_id):
        """Update species count"""
        if species_id in self._species_counts:
            self._species_counts[species_id] += 1
        else:
            self._species_counts[species_id] = 1

    def remove_species_member(self, species_id):
        """Update species count"""
        if species_id in self._species_counts:
            self._species_counts[species_id] -= 1
            if self._species_counts[species_id] == 0:
                del self._species_counts[species_id]

    @property
    def species_counts(self):
        """Return species count"""
        return self._species_counts.copy()

    def add(self, item, pos):
        """Place item in new position"""
        self.remove(self.at(pos))
        self.empty_pos.discard(pos)
        self._setat(pos, item)
        self._setloc(item, pos)

    def remove(self, item):
        """Remove item from current position"""
        if item == None: return
        item_pos = self.loc(item)
        self._setat(item_pos, None)
        self._setloc(item, None)
        self.empty_pos.add(item_pos)


    def move(self, item, pos):
        """Update item position"""
        self.remove(self.at(pos))
        item_pos = self.loc(item)
        self._setat(item_pos, None)
        self.empty_pos.add(item_pos)
        self._setat(pos, item)
        self._setloc(item, pos)
        self.empty_pos.discard(pos)

    def _setloc(self, item, pos):
        """Set location in our datastructures"""
        locations = None
        if item.type == 'member':
            locations = self.members
        elif item.type == 'resource':
            locations = self.resources
        if pos:
            locations[item.id] = pos
        else:
            del locations[item.id]

    def loc(self, item: Item):
        """Rturns our location representation for an item"""
        locations = None
        if item.type == 'member':
            locations = self.members
        elif item.type == 'resource':
            locations = self.resources
        return locations[item.id]

    def _setat(self, pos, item: Item):
        """Set item to 2d array"""
        self.arr[pos[0]][pos[1]] = item

    def at(self, pos):
        """Return item in our 2d array representation"""
        return self.arr[pos[0]][pos[1]]

    def in_bounds(self, pos):
        """Return boolean if position representation is in bound"""
        if pos[0] < 0 or pos[0] > self.height - 1: return False
        if pos[1] < 0 or pos[1] > self.width - 1: return False
        return True

    @property
    def is_game_over(self):
        """return boolean if game is over or not"""
        return self.game_over

    def check_game_over(self):
        """Set game_over to True if only 1 or less species left"""
        if len(self.species_counts) <= 1:
            self.game_over = True

def apply_delta(curr, d): return (curr[0]+d[0], curr[1]+d[1])
