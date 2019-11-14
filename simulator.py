from map import Map
from member import Member, BASE_CHANCE
from skill import Skill, Resource
from random import randint, choice
from concurrent.futures import ThreadPoolExecutor

NUM_SPECIES = 3
NUM_RESOURCES = 15
WIDTH = 10
HEIGHT = 10

map_obj = Map(width=WIDTH,height=HEIGHT)
pos_set = set([(i,j) for i in range(WIDTH) for j in range(HEIGHT)])

for i in range(NUM_SPECIES):
    m = Member(
        skill=Skill(
            strength=randint(0,3), 
            speed=randint(0,3)), 
        species_id=i,
        reproduction_chance=BASE_CHANCE//10)
    pos = choice(list(pos_set))
    pos_set.remove(pos)
    map_obj.add(m, pos)

for _ in range(NUM_RESOURCES):
    r = Resource(
        strength=randint(0,1),
        speed=randint(0,1))
    pos = choice(list(pos_set))
    pos_set.remove(pos)
    map_obj.add(r, pos)


TIMESTEPS = 100

print(map_obj)
with ThreadPoolExecutor(max_workers=5) as executor:
    for _ in range(TIMESTEPS):
        members = [map_obj.at(pos) for pos in map_obj.locations.values() if isinstance(map_obj.at(pos), Member)]
        list(executor.map(lambda m: m.move(map_obj), members))
print(map_obj)