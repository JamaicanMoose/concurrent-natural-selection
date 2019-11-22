"""Defines the Member class representing a member of a species.
"""

from item import Item
from skill import Skill, Resource
from random import choice, shuffle, randint
from map import Map, apply_delta
from threading import Thread, Event
from time import sleep

BASE_CHANCE = 1000

class Member(Item):
    def __init__(self, draw_fn, map_obj, skill: Skill, species_id: int, reproduction_chance: int, sim):
        assert(reproduction_chance <= BASE_CHANCE)
        this = self
        self._stop = Event()
        def member_thread():
            while not this._stop.is_set():
                with map_obj.lock:
                    this.move(map_obj)
                    draw_fn()
                max_sleep_int = 10-this.skill.speed if 10-this.skill.speed > 0 else 0
                min_sleep_int = 10-this.skill.speed-2 if 10-this.skill.speed-2 > 0 else 0
                sleep(randint(min_sleep_int, max_sleep_int)/10)
        self._thread = Thread(target=member_thread)
        self._draw_fn = draw_fn
        self.init_skill = skill.copy()
        self.skill = skill.copy()
        self.species_id = species_id
        self.repr_chc = reproduction_chance
        self.sim = sim

    def __repr__(self):
        return str(self.species_id)

    def move(self, map_obj):
        if self in map_obj:
            if randint(1, BASE_CHANCE//self.repr_chc) == 1 and self.skill.strength >= 2:
                self.reproduce(map_obj)
            else:
                self.walk(map_obj)
            if(map_obj.game_over()):
                self.sim.end_sim()

    def walk(self, map_obj):
        self.step(map_obj)
    #change to increasing strength using percentage instead of adding to surrounding member kevin
    def step(self, map_obj):
        curr_loc = map_obj.loc(self)
        move = choice(((1,0), (-1,0), (0,1), (0,-1)))
        new_loc = apply_delta(curr_loc, move)
        if map_obj.in_bounds(new_loc):
            if map_obj.at(new_loc) == None:
                map_obj.move(self, new_loc)
            elif isinstance(map_obj.at(new_loc), Resource):
                self.skill += map_obj.at(new_loc)
                map_obj.move(self, new_loc)
            elif isinstance(map_obj.at(new_loc), Member):
                other = map_obj.at(new_loc)
                if self.skill.strength > other.skill.strength:
                    map_obj.move(self, new_loc)
                elif self.skill.strength < other.skill.strength:
                    map_obj.remove(self)
                    return False
                else:
                    map_obj.remove(self)
                    map_obj.remove(other)
                    return False
            return True

    def reproduce(self, map_obj):
        curr_loc = map_obj.locations[str(id(self))]
        adj_set = [apply_delta(curr_loc, d) for d in ((1,0), (-1,0), (0,1), (0,-1))]
        shuffle(adj_set)
        for pos in adj_set:
            if map_obj.in_bounds(pos) and map_obj.at(pos) == None:
                child_skill = self.init_skill.copy()
                #child_skill = self.skill // 2
                #self.skill -= child_skill
                child = Member(
                    draw_fn=self._draw_fn,
                    map_obj=map_obj,
                    skill=child_skill, 
                    species_id=self.species_id, 
                    reproduction_chance=self.repr_chc, sim=self.sim)
                map_obj.add(child, pos)
                child._thread.start()
                break




