# pylint: skip-file
import random
from item import Item

class Skill():
    def __init__(self, strength: int = 0, speed: int = 0,
        skill_bag: dict = {"injure": 1, "poison": 1, "klutz": 1, "disable": 1}):
        self.strength = strength
        self.speed = speed
        self.skill_bag = skill_bag
    def add_to_bag(self):
        '''Random skill magnitude and skill type added to skill bag'''
        skill = random.choice(list(self.skill_bag.keys()))
        self.skill_bag[skill] = random.random()
    def merge_bags(self, other_bag):
        '''New bag is created with best skill values from both bags'''
        newbag = {}
        for item in self.skill_bag:
            if item in newbag:
                newbag[item] = min(self.skill_bag[item], other_bag[item])
            else:
                newbag[item] = 1
        for item in other_bag:
            if item in newbag:
                newbag[item] += min(self.skill_bag[item], other_bag[item])
            else:
                newbag[item] = 1
        return newbag
    def __repr__(self):
        return f'Skill(strength={self.strength}, speed={self.speed})'
    def __mul__(self, other):
        '''Returns a new skill multiplied by magnitude of the resource'''
        skill = Skill(
            strength=self.strength*other.strength,
            speed=self.speed*other.speed,
            skill_bag=self.merge_bags(other.skill_bag))
        return skill
    def copy(self):
        '''Deep copy of skill'''
        return Skill(skill_bag=self.skill_bag,
            strength=self.strength,
            speed=self.speed)

class Resource(Item, Skill):
    def __repr__(self):
        return ' '

    def markup(self):
        '''Defines thresholds between resources for resource coloring'''
        mag = (self.speed + self.strength)/2
        if mag > 1.5:
            if mag > 1.6:
                if mag > 1.7:
                    return [('best', repr(self))]
                else:
                    return [('better', repr(self))]
            else:
                return [('normal', repr(self))]
        else:
            if mag < 1.3:
                if mag < 1.1:
                    return [('worst', repr(self))]
                else:
                    return [('worse', repr(self))]
            else:
                return [('normal', repr(self))]
        return [('best', repr(self))]

    @property
    def type(self):
        return 'resource'
