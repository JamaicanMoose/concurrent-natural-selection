"""Defines the Map class representing a simulation map.
"""

from threading import Lock

class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.arr = [[None]*width for _ in range(height)] #(row, col)
        self.locations = {}
        self.lock = Lock()

    def __repr__(self):
        rep = ''
        repfn = lambda o: ' ' if o == None else repr(o) 
        for row in self.arr:
            rep += ' | '.join([repfn(o) for o in row]) + '\n'
            rep += ('-'*(self.width+3*(self.width-1))) + '\n'
        return rep

    def __getitem__(self, pos):
        return self.at(pos)

    def __contains__(self, item):
        return item.id in self.locations

    def add(self, item, pos):
        self.remove(self.at(pos))
        self._setat(pos, item)
        self._setloc(item, pos)

    def remove(self, item):
        if item == None: return
        self._setat(self.loc(item), None)
        self._setloc(item, None)

    def move(self, item, pos):
        self.remove(self.at(pos))
        self._setat(self.loc(item), None)
        self._setat(pos, item)
        self._setloc(item, pos)

    def _setloc(self, item, pos):
        if pos: 
            self.locations[item.id] = pos
        else:
            del self.locations[item.id]

    def loc(self, item):
        return self.locations[item.id]

    def _setat(self, pos, item):
        self.arr[pos[0]][pos[1]] = item

    def at(self, pos):
        return self.arr[pos[0]][pos[1]]

    def in_bounds(self, pos):
        if pos[0] < 0 or pos[0] > self.height - 1: return False
        if pos[1] < 0 or pos[1] > self.width - 1: return False
        return True

def apply_delta(curr, d): return (curr[0]+d[0], curr[1]+d[1])