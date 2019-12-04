# pylint: skip-file
from map import Map
from member import Member
from skill import Skill, Resource
from random import randint, choice, lognormvariate, uniform
from concurrent.futures import ThreadPoolExecutor
from threading import Thread, Event, active_count
import curses
import math
from time import sleep, time
from defs import SIM_SPEED_MULT, BASE_CHANCE, nvcl, RESOURCE_MEAN, RESOURCE_STDEV

class Window:
    def __init__(self, height=0, width=0):
        self.stdscr = curses.initscr()
        self.win = curses.newwin(height, width, 0,0)
        self.scorewin = curses.newwin(height, width, 0, width+1)
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)

    def end(self):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()

    def draw_map(self, map_obj):
        self.win.clear()
        self.win.addstr(0,0,repr(map_obj))
        self.win.refresh()

    def draw_scores(self, map_obj):
        self.scorewin.clear()
        members = [map_obj.at(pos) for pos in map_obj.members.values()]
        members.sort(key=lambda m: m.skill.strength + m.skill.speed)
        string = '\n'.join([m.stats() for m in members[:10]])
        self.scorewin.addstr(0,0, string)
        self.scorewin.refresh()

class Simulator:
    def __init__(self):
        self.num_species = 3
        self.num_members = 2
        self.num_resources = 15
        self.resource_spawn_rate = BASE_CHANCE//20
        self.width = 10
        self.height = 10
        self.user_params();
        self.map_obj = Map(width=self.width,height=self.height)
        self.pos_set = pos_set = set([(i,j) for i in range(self.width) for j in range(self.height)])
        win_height = len(repr(self.map_obj).split('\n'))+1
        win_width = max([len(s) for s in repr(self.map_obj).split('\n')])+1
        self.win = Window(height=win_height, width=win_width)
        self.init_map();

    def user_params(self):
            self.num_species = int(input("Enter number of species on board (Default: 3)\n"))
            self.num_members = int(input("Enter number of members per species (Default: 2)"))
            self.num_resources = int(input("Enter number of resources on the board (Default: 15)"))
            dimension = int(math.ceil(math.sqrt(self.num_resources + self.num_species * self.num_members * 1.5)))
            self.width = 10
            self.height = 10

    def init_map(self):
        for i in range(self.num_species):
            for _ in range(self.num_members):
                m = Member(
                    draw_fn=self.draw,
                    map_obj=self.map_obj,
                    skill=Skill(
                        strength=uniform(0,10),
                        speed=uniform(0,3)),
                    species_id=i,
                    reproduction_chance=BASE_CHANCE//10)
                pos = choice(list(self.pos_set))
                self.pos_set.remove(pos)
                self.map_obj.add(m, pos)
        for _ in range(self.num_resources):
            r = Resource(
                strength=nvcl(RESOURCE_MEAN, RESOURCE_STDEV),
                speed=nvcl(RESOURCE_MEAN, RESOURCE_STDEV))
            pos = choice(list(self.pos_set))
            self.pos_set.remove(pos)
            self.map_obj.add(r, pos)

    def members(self):
        return [self.map_obj.at(pos) for pos in self.map_obj.members.values()]

    def _random_resource_inclusion_thread(self):
        while True:
            with self.map_obj.lock:
                if self.map_obj.is_game_over:
                    break
                r = Resource(
                    strength=nvcl(RESOURCE_MEAN, RESOURCE_STDEV),
                    speed=nvcl(RESOURCE_MEAN, RESOURCE_STDEV))
                pos = choice(list(self.map_obj.empty_pos))
                self.map_obj.add(r, pos)
            sleep(uniform(0, BASE_CHANCE/self.resource_spawn_rate)/SIM_SPEED_MULT)

    def print_end_state(self):
        #print(self.map_obj)
        self.map_obj.check_game_over()

    def draw(self):
        self.win.draw_map(self.map_obj)
        self.win.draw_scores(self.map_obj)

    def start(self):
        for m in self.members():
            m._thread.start()
        Thread(target=self._random_resource_inclusion_thread).start()
        while True:
            if active_count() == 1:
                break
            self.draw()
            sleep(.2)
        self.win.end()
        self.print_end_state()
