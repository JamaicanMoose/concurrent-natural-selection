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
        return 'R'

    @property
    def type(self):
        return 'resource'
