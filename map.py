# pylint: skip-file
"""Defines the Map class representing a simulation map.
"""
from item import Item
from threading import Lock, Event
import random

class Map():
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.arr = [[None]*width for _ in range(height)] #(row, col)
        self.members = {}
        self.resources = {}
        self.empty_pos = set([(i,j) for i in range(width) for j in range(height)])
        self.lock = Lock()
        self.game_over = False

    def __repr__(self):
        rep = ''
        repfn = lambda o: ' ' if o == None else repr(o)
        for row in self.arr:
            rep += ' | '.join([repfn(o) for o in row]) + '\n'
            rep += ('-'*(self.width+3*(self.width-1))) + '\n'
        return rep

    def __getitem__(self, pos):
        return self.at(pos)

    def __contains__(self, item: Item):
        if item.type == 'member':
            return item.id in self.members
        elif item.type == 'resource':
            return item.id in self.resources
        else:
            return False

    def add(self, item, pos):
        self.remove(self.at(pos))
        self.empty_pos.discard(pos)
        self._setat(pos, item)
        self._setloc(item, pos)

    def remove(self, item):
        if item == None: return
        item_pos = self.loc(item)
        self._setat(item_pos, None)
        self._setloc(item, None)
        self.empty_pos.add(item_pos)


    def move(self, item, pos):
        self.remove(self.at(pos))
        item_pos = self.loc(item)
        self._setat(item_pos, None)
        self.empty_pos.add(item_pos)
        self._setat(pos, item)
        self._setloc(item, pos)
        self.empty_pos.discard(pos)

    def _setloc(self, item, pos):
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
        locations = None
        if item.type == 'member':
            locations = self.members
        elif item.type == 'resource':
            locations = self.resources
        return locations[item.id]

    def _setat(self, pos, item: Item):
        self.arr[pos[0]][pos[1]] = item

    def at(self, pos):
        return self.arr[pos[0]][pos[1]]

    def in_bounds(self, pos):
        if pos[0] < 0 or pos[0] > self.height - 1: return False
        if pos[1] < 0 or pos[1] > self.width - 1: return False
        return True

    @property
    def is_game_over(self):
        return self.game_over

    def check_game_over(self):
        members = [self.at(pos) for pos in self.members.values()]
        mem_set = set([m.species_id for m in members])
        if len(mem_set) <= 1:
            if len(mem_set) == 1:
                print(f'Species {members[0].species_id} wins!')
            elif len(mem_set) == 0:
                print(f'All species dead.')
            self.game_over = True

def apply_delta(curr, d): return (curr[0]+d[0], curr[1]+d[1])
