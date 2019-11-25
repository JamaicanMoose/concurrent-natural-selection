# pylint: skip-file
import random
from item import Resource

MAX_STRENGTH_MULTIPLIER = 5
MAX_MOVEMENT_MULTIPLIER = 5
UPGRADE_ODDS = 3

# does not take into account if a species will spawn at a location with a resource
class Resources:
    def __init__(self, map_width, map_length, resource_percentage):
        if map_width < 1 or map_length < 1 or resource_percentage > 1:
            raise Exception("Invalid initial values for resources")
            return

        self.map_dict = {}
        self.map_width = map_width
        self.map_length = map_length
        self.num_resouces = int(map_width * map_length * resource_percentage)

    def place_resources(self):
        for i in  range(self.num_resouces):
            while True:
                row = random.randint(0, self.map_length - 1)
                col = random.randint(0, self.map_width - 1)

                if (row, col) not in self.map_dict:
                    break

            self.map_dict[(row, col)] = self.random_resource()

    def random_resource(self):
        resource_dict = {}
        strength = 2
        movement = 2
        for i in range(MAX_STRENGTH_MULTIPLIER - 2):
            if random.randint(1,UPGRADE_ODDS) == 1:
                strength += 1
            else:
                break

        for i in range(MAX_MOVEMENT_MULTIPLIER - 2):
            if random.randint(1,UPGRADE_ODDS) == 1:
                movement += 1
            else:
                break

        return Resource(strength=strength, speed=speed)
