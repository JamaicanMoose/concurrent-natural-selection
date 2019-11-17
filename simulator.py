from map import Map
from member import Member, BASE_CHANCE
from skill import Skill, Resource
from random import randint, choice
from concurrent.futures import ThreadPoolExecutor
import curses
from time import sleep


NUM_SPECIES = 3
NUM_RESOURCES = 15
WIDTH = 10
HEIGHT = 10

map_obj = Map(width=WIDTH,height=HEIGHT)
pos_set = set([(i,j) for i in range(WIDTH) for j in range(HEIGHT)])

stdscr = curses.initscr()
win = curses.newwin(len(repr(map_obj).split('\n'))+1, max([len(s) for s in repr(map_obj).split('\n')])+1, 0,0)
curses.noecho()
curses.cbreak()
stdscr.keypad(True)

def draw_map():
    win.clear()
    win.addstr(0,0,repr(map_obj))
    win.refresh()

def end_sim():
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()
    print(map_obj)

for i in range(NUM_SPECIES):
    m = Member(
        skill=Skill(
            strength=randint(0,10), 
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

draw_map()
with ThreadPoolExecutor(max_workers=5) as executor:
    s = 0
    frozen = 0
    init_skills = [(map_obj.at(pos).species_id, map_obj.at(pos).skill) for pos in map_obj.locations.values() if isinstance(map_obj.at(pos), Member)]
    while True:
        s += 1
        old_locations = map_obj.locations.copy()
        members = [map_obj.at(pos) for pos in map_obj.locations.values() if isinstance(map_obj.at(pos), Member)]
        list(executor.map(lambda m: m.move(map_obj), members))
        if map_obj.locations == old_locations:
            frozen += 1
            if frozen == 10:
                end_sim()
                print(f'Degenerate state.')
                print(init_skills)
                print([(m.species_id, m.skill) for m in members])
                break
        else:
            frozen = 0
        new_members = [map_obj.at(pos) for pos in map_obj.locations.values() if isinstance(map_obj.at(pos), Member)]
        mem_set = set([m.species_id for m in new_members])
        if len(mem_set) == 1:
            end_sim()
            print(f'Species {list(mem_set)[0]} wins after {s} steps!')
            print(init_skills)
            print(new_members[0].skill)
            break
        elif len(mem_set) == 0:
            end_sim()
            print(f'All species dead after {s} steps.')
            print(init_skills)
            break
        draw_map()
        sleep(.2)
