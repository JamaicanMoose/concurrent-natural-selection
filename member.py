# pylint: skip-file
"""Defines the Member class representing a member of a species.
"""
from item import Item
from skill import Skill, Resource
from random import choice, shuffle, randint, uniform
from map import Map, apply_delta
from threading import Thread, Event
from time import sleep
from defs import SIM_SPEED_MULT, BASE_CHANCE
import random

class Member(Item):
    def __init__(self, draw_fn, map_obj, skill: Skill, species_id: int, reproduction_chance: int):
        assert(reproduction_chance <= BASE_CHANCE)
        this = self
        self._exists = True
        map_obj.add_species_member(species_id)
        def member_thread():
            while self._exists:
                with map_obj.lock:
                    if map_obj.is_game_over:
                        break
                    this.move(map_obj)
                    map_obj.check_game_over()
                    if not self._exists:
                        map_obj.remove_species_member(species_id)
                max_sleep_int = 10-this.skill.speed if 10-this.skill.speed > 0 else 0
                min_sleep_int = 10-this.skill.speed-2 if 10-this.skill.speed-2 > 0 else 0
                sleep(uniform(min_sleep_int, max_sleep_int)/SIM_SPEED_MULT)
        self._thread = Thread(target=member_thread)
        self._draw_fn = draw_fn
        self.init_skill = skill.copy()
        self.skill = skill.copy()
        self.species_id = species_id
        self.repr_chc = reproduction_chance

    def __repr__(self):
        return str(self.species_id)

    def markup(self):
        return repr(self)

    def stats(self):
        return f'Species:{self.species_id}; Speed:{self.skill.speed:.2f}; Strength:{self.skill.strength:.2f}'

    @property
    def type(self):
        return 'member'

    def move(self, map_obj):
        if self in map_obj:
            if randint(1, BASE_CHANCE//self.repr_chc) == 1 and self.skill.strength >= 2:
                self.reproduce(map_obj)
            else:
                self.step(map_obj)
        else:
            self._exists = False

    def use_bag(self, other):
        bag = self.skill.skill_bag
        skill = random.choice(list(bag.keys()))
        amounts = bag[skill]
        if amounts:
            if (skill == 'injure'):
                print("!")
                amt = amounts.pop()
                other.skill.strength *= amt

    def step(self, map_obj):
        curr_loc = map_obj.loc(self)
        move = choice(((1,0), (-1,0), (0,1), (0,-1)))
        new_loc = apply_delta(curr_loc, move)
        if map_obj.in_bounds(new_loc):
            if map_obj.at(new_loc) == None:
                map_obj.move(self, new_loc)
            elif isinstance(map_obj.at(new_loc), Resource):
                self.skill *= map_obj.at(new_loc)
                map_obj.move(self, new_loc)
            elif isinstance(map_obj.at(new_loc), Member):
                other = map_obj.at(new_loc)
                if self.skill.strength > other.skill.strength:
                    map_obj.move(self, new_loc)
                elif self.skill.strength < other.skill.strength:
                    self.use_bag(other)
                    map_obj.remove(self)
                    return False
                else:
                    map_obj.remove(self)
                    map_obj.remove(other)
                    return False
            return True

    def reproduce(self, map_obj):
        curr_loc = map_obj.members[str(id(self))]
        adj_set = [apply_delta(curr_loc, d) for d in ((1,0), (-1,0), (0,1), (0,-1))]
        shuffle(adj_set)
        for pos in adj_set:
            if map_obj.in_bounds(pos) and map_obj.at(pos) == None:
                child_skill = self.init_skill.copy()
                child = Member(
                    draw_fn=self._draw_fn,
                    map_obj=map_obj,
                    skill=child_skill,
                    species_id=self.species_id,
                    reproduction_chance=self.repr_chc)
                map_obj.add(child, pos)
                child._thread.start()
                break
