"""Defines the Member class representing a member of a species.
"""

from item import Item
from skill import Skill, Resource
from random import choice, shuffle, randint
from map import Map, apply_delta

BASE_CHANCE = 1000

class Member(Item):
    def __init__(self, skill: Skill, species_id: int, reproduction_chance: int):
        assert(reproduction_chance <= BASE_CHANCE)
        self.init_skill = skill.copy()
        self.skill = skill.copy()
        self.species_id = species_id
        self.repr_chc = reproduction_chance

    def __repr__(self):
        return str(self.species_id)

    def move(self, map_obj):
        with map_obj.lock:
            if self in map_obj:
                if randint(1, BASE_CHANCE//self.repr_chc) == 1 and self.skill.strength >= 2:
                    self.reproduce(map_obj)
                else:
                    self.walk(map_obj)

    def walk(self, map_obj):
        for _ in range(self.skill.speed):
            if not self.step(map_obj):
                break

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
                    skill=child_skill, 
                    species_id=self.species_id, 
                    reproduction_chance=self.repr_chc)
                map_obj.add(child, pos)
                break




