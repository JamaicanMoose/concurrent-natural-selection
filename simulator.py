from map import Map
from member import Member, BASE_CHANCE
from skill import Skill, Resource
from random import randint, choice
from concurrent.futures import ThreadPoolExecutor
from threading import Thread, Event
import curses
from time import sleep, time


NUM_SPECIES = 3
NUM_MEMBERS = 2
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
    for _ in range(NUM_MEMBERS):
        m = Member(
            draw_fn=draw_map,
            map_obj=map_obj,
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

end_event = Event()

def frozen_monitor_thread():
    while not end_event.is_set():
        with map_obj.lock:
            old_locations = map_obj.locations.copy()
        sleep(5)
        with map_obj.lock:
            if map_obj.locations == old_locations:
                end_sim()
                print(f'Degenerate state.')
                print([(m.species_id, m.skill) for m in members])
                break

def completion_monitor_thread():
    start_time = time()
    while not end_event.is_set():
        with map_obj.lock:
            new_members = [map_obj.at(pos) for pos in map_obj.locations.values() if isinstance(map_obj.at(pos), Member)]
            mem_set = set([m.species_id for m in new_members])
            if len(mem_set) <= 1:
                if len(mem_set) == 1:
                    s = time() - start_time
                    end_sim()
                    print(f'Species {list(mem_set)[0]} wins after {s} seconds!')
                    print(new_members[0].skill)
                    break
                elif len(mem_set) == 0:
                    s = time() - start_time
                    end_sim()
                    print(f'All species dead after {s} seconds.')
                    break

fmt = Thread(target=frozen_monitor_thread)
fmt.start()
cmt = Thread(target=completion_monitor_thread)
cmt.start()
members = [map_obj.at(pos) for pos in map_obj.locations.values() if isinstance(map_obj.at(pos), Member)]
for m in members:
    m._thread.start()

cmt.join()
fmt.join()

members = [map_obj.at(pos) for pos in map_obj.locations.values() if isinstance(map_obj.at(pos), Member)]
for m in members:
    m._stop.set()
for m in members:
    m._thread.join()

