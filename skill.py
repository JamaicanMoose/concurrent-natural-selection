# pylint: skip-file
import random
from item import Item

class Skill():
    def __init__(self, strength: int = 0, speed: int = 0, skill_bag: dict = {"injure": [], "poison": [], "klutz": [], "disable": []}):
        self.strength = strength
        self.speed = speed
        self.skill_bag = skill_bag
    def add_to_bag(self):
        skill = random.choice(list(self.skill_bag.keys()))
        self.skill_bag[skill].append(random.random())
    def merge_bags(self, bag2):
        newbag = {}
        for item in self.skill_bag:
            if item in newbag:
                newbag[item] += self.skill_bag[item]
            else:
                newbag[item] = []
        for item in bag2:
            if item in newbag:
                newbag[item] += bag2[item]
            else:
                newbag[item] = []
        return newbag
    def __repr__(self):
        return f'Skill(strength={self.strength}, speed={self.speed})'
    def __add__(self, other):
        return Skill(
            strength=(self.strength+other.strength),
            speed=(self.speed+other.speed))
    def __sub__(self, other):
        return Skill(
            strength=(self.strength-other.strength),
            speed=(self.speed-other.speed))
    def __floordiv__(self, div: int):
        return Skill(
            strength=self.strength//div,
            speed=self.speed//div)
    def __mul__(self, other):
        skill = Skill(
            strength=self.strength*other.strength,
            speed=self.speed*other.speed,
            skill_bag=self.merge_bags(other.skill_bag))
        return skill
    def copy(self):
        return Skill(skill_bag=self.skill_bag,
            strength=self.strength,
            speed=self.speed)

class Resource(Item, Skill):
    def __repr__(self):
        return ' '

    def markup(self):
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
