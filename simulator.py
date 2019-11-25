# pylint: skip-file
from map import Map
from member import Member, BASE_CHANCE
from skill import Skill, Resource
from random import randint, choice
from concurrent.futures import ThreadPoolExecutor
from threading import Thread, Event, active_count
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
        self.stdscr = curses.initscr()
        self.win = curses.newwin(len(repr(self.map_obj).split('\n'))+1, max([len(s) for s in repr(self.map_obj).split('\n')])+1, 0,0)
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)
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

    def members(self):
        return [self.map_obj.at(pos) for pos in self.map_obj.members.values()]

    def start(self):
        for m in self.members():
            m._thread.start()
        while True:
            if active_count() == 1:
                break
            sleep(1)
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()
        self.print_end_state()

    def print_end_state(self):
        print(self.map_obj)
        self.map_obj.check_game_over()

    def draw_map(self):
        self.stdscr.clear()
        self.win.clear()
        self.win.addstr(0,0,repr(self.map_obj))
        self.win.refresh()
