# pylint: skip-file

from item import Item

### Add __mul__ (Skill, int) => Skill to scale skill by an integer kevin
class Skill():
    def __init__(self, strength: int = 0, speed: int = 0):
        self.strength = strength
        self.speed = speed
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
        return Skill(
            strength=self.strength*other.strength,
            speed=self.speed*other.speed)
    def copy(self):
        return Skill(
            strength=self.strength,
            speed=self.speed)

class Resource(Item, Skill):
    def __repr__(self):
        return ' '

    def markup(self):
        mag = (self.speed + self.strength)/2
        if mag > 1:
            if mag > 1.1:
                if mag > 1.2:
                    return [('best', repr(self))]
                else:
                    return [('better', repr(self))]
            else:
                return [('normal', repr(self))]
        else:
            if mag < .9:
                if mag < .8:
                    return [('worst', repr(self))]
                else:
                    return [('worse', repr(self))]
            else:
                return [('normal', repr(self))]
        return [('best', repr(self))]

    @property
    def type(self):
        return 'resource'
