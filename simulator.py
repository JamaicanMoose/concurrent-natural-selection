from map import Map
from member import Member, BASE_CHANCE
from skill import Skill, Resource
from random import randint, choice
from concurrent.futures import ThreadPoolExecutor
from threading import Thread, Event
import curses
from time import sleep, time

class Simulator:
    def __init__(self):
        self.num_species = 3
        self.num_members = 2
        self.num_resources = 15
        self.width = 10
        self.height = 10
        self.map_obj = Map(width=self.width,height=self.height)
        self.pos_set = pos_set = set([(i,j) for i in range(self.width) for j in range(self.height)])
        # self.stdscr = curses.initscr()
        # self.win = curses.newwin(len(repr(self.map_obj).split('\n'))+1, max([len(s) for s in repr(self.map_obj).split('\n')])+1, 0,0)
        self.init_map();

    def init_map(self):
        for i in range(self.num_species):
            for _ in range(self.num_members):
                m = Member(
                    draw_fn=self.draw_map,
                    map_obj=self.map_obj,
                    skill=Skill(
                        strength=randint(0,10), 
                        speed=randint(0,3)), 
                    species_id=i,
                    reproduction_chance=BASE_CHANCE//10)
                pos = choice(list(self.pos_set))
                self.pos_set.remove(pos)
                self.map_obj.add(m, pos)
        for _ in range(self.num_resources):
            r = Resource(
                strength=randint(0,1),
                speed=randint(0,1))
            pos = choice(list(self.pos_set))
            self.pos_set.remove(pos)
            self.map_obj.add(r, pos)
        # curses.noecho()
        # curses.cbreak()
        # self.stdscr.keypad(True)

    def start(self):
        members = [self.map_obj.at(pos) for pos in self.map_obj.locations.values() if isinstance(self.map_obj.at(pos), Member)]
        for m in members:
            m._thread.start()
        for m in members:
            m._stop.set()
        for m in members:
            m._thread.join()

    def draw_map(self):
        print("in draw map")
        # self.win.clear()
        # self.win.addstr(0,0,repr(self.map_obj))
        # self.win.refresh()

    def end_sim(self):
        print("in end sim")
        # curses.nocbreak()
        # self.stdscr.keypad(False)
        # curses.echo()
        # curses.endwin()
        print(self.map_obj)



