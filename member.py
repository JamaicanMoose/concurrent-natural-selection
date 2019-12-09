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
from itertools import chain
from statistics import mean
import random

class Member(Item):
    '''Adds member to the the map and intializes member parameters'''
    def __init__(self, draw_fn, map_obj, skill: Skill, species_id: int, 
                                    reproduction_chance: int):
        assert(reproduction_chance <= BASE_CHANCE)
        this = self
        self._exists = True
        map_obj.add_species_member(species_id)
        #member thread keeps moving until killed 
        def member_thread():
            while self._exists: 
            # If we were killed while sleeping then exit thread.
                with map_obj.lock:
                    if not self._exists: 
                    # If we were killed while waiting for lock then exit thread.
                        break
                    if map_obj.is_game_over: 
                    # If the game is over and we're not dead then exit thread.
                        break
                    this.move(map_obj)
                    map_obj.check_game_over()
                max_sleep_int = 10-this.skill.speed if 10-this.skill.speed > 0 \
                                else 0
                min_sleep_int = 10-this.skill.speed-2 if 10-this.skill.speed-2 \
                                > 0 else 0
                #length of sleep before next move based on member speed
                sleep(uniform(min_sleep_int, max_sleep_int)/SIM_SPEED_MULT)
        self._thread = Thread(target=member_thread)
        self._draw_fn = draw_fn
        #stored for reproduced species to have same initial skill
        self.init_skill = skill.copy()
        self.skill = skill.copy()
        self.species_id = species_id
        self.repr_chc = reproduction_chance
        self.moves = [(1,0), (-1,0), (0,1), (0,-1)]

    def __repr__(self):
        return str(self.species_id)

    def markup(self):
        return repr(self)

    def stats(self):
        '''Provides a measure of how favorable a member's skills are'''
        skill_bag_chain = self.skill.skill_bag.values()
        skill_bag_mag = mean(skill_bag_chain) if skill_bag_chain else 1
        return f'Species:{self.species_id}: Speed:\
{self.skill.speed:.2f}; Strength:{self.skill.strength:.2f}; Skill-Bag:\
{skill_bag_mag:.2f}'

    @property
    def type(self):
        return 'member'

    def move(self, map_obj):
        '''Randomly chooses if member reproduces or takes a step on the board'''
        if self in map_obj:
            if randint(1, BASE_CHANCE//self.repr_chc) == 1 and\
            self.skill.strength >= 2:
                self.reproduce(map_obj)
            else:
                self.step(map_obj)
        else:
            self._exists = False

    def use_bag(self, other):
        '''Chooses a random skill type for a member to use on 
            another from the bag and uses it'''
        bag = self.skill.skill_bag
        skill = random.choice(list(bag.keys()))
        amount = bag[skill]
        if amount:                
            if (skill == 'injure'):
                #decreases the other's skill
                other.skill.strength *= amount
            elif (skill == 'poison'):
                #decreases the other's strength
                other.skill.speed *= amount
            elif (skill == 'klutz'):
                #empties the skill bag of the other member
                for item in other.skill.skill_bag:
                    other.skill.skill_bag[item] = 1
            elif (skill == 'disable'):
                #disables other member by removing one of its moves.
                if len(other.moves) > 0 and amount != 1:
                    other.moves.pop()

    def step(self, map_obj):
        '''Moves the member and battles or picks up a resource.'''
        curr_loc = map_obj.loc(self)
        if len(self.moves) <= 0:
            return
        move = choice(self.moves)
        new_loc = apply_delta(curr_loc, move)
        if map_obj.in_bounds(new_loc):
            if map_obj.at(new_loc) == None:
                map_obj.move(self, new_loc)
            elif isinstance(map_obj.at(new_loc), Resource):
                #if there is a resource, increase the users skill
                self.skill *= map_obj.at(new_loc)
                map_obj.move(self, new_loc)
            elif isinstance(map_obj.at(new_loc), Member):
                #if there is another member, battle and the stronger member wins
                other = map_obj.at(new_loc)
                if self.skill.strength > other.skill.strength:
                    #losing species damages other species by using item in bag
                    other.use_bag(self)
                    map_obj.move(self, new_loc)
                    map_obj.remove_species_member(other.species_id)
                elif self.skill.strength < other.skill.strength:
                    self.use_bag(other)
                    map_obj.remove(self)
                    map_obj.remove_species_member(self.species_id)
                    return
                else:
                    map_obj.remove(self)
                    map_obj.remove(other)
                    map_obj.remove_species_member(self.species_id)
                    map_obj.remove_species_member(other.species_id)
                    return
            return

    def reproduce(self, map_obj):
        '''Reproduces member by creating a new member of the species 
            (with initial skill)'''
        curr_loc = map_obj.members[str(id(self))]
        adj_set = [apply_delta(curr_loc, d) for d in \
                    ((1,0), (-1,0), (0,1), (0,-1))]
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
