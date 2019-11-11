class Item():
    pass

class Skill():
    def __init__(self, strength: int = 0, speed: int = 0):
        self.strength = strength
        self.speed = speed

class Resource(Item, Skill):
    pass

class Member(Item):
    def __init__(self, skill: Skill):
        self.skill = skill

    def consume_resource(self, resource: Resource):
        for s_name, val in list(vars(resource)):
            if s_name in vars(self.skill):
                newval = getattr(self.skill, s_name) + val
                setattr(self.skill, s_name, newval if newval > 0 else 0)

    def walk(self):
        pass

    def reproduce(self):
        pass
