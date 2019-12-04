# pylint: skip-file
import urwid
import urwid.raw_display
from random import randint, choice, uniform
from random import lognormvariate as lnv
from concurrent.futures import ThreadPoolExecutor
from threading import Thread, Event, active_count
from time import sleep, time
from collections import Counter
from signal import signal, SIGINT

from map import Map
from member import Member
from skill import Skill, Resource
from defs import SIM_SPEED_MULT, BASE_CHANCE, RESOURCE_MEAN, RESOURCE_STDEV

class Window:
    def __init__(self):
        self.map = urwid.Text('')
        self.scoreboard = urwid.Text('')
        self.widgetlist = [urwid.Filler(w, 'top') for w in [self.map, self.scoreboard]]
        self.win = urwid.Columns(self.widgetlist, dividechars=2)
        self.loop = urwid.MainLoop(self.win)

    def start(self):
        self.loop.start()

    def stop(self):
        self.loop.stop()

    def draw(self, map_obj):
        # Render Map
        self.map.set_text(repr(map_obj))
        # Render Scoreboard
        members = [map_obj.at(pos) for pos in map_obj.members.values()]
        members.sort(key=lambda m: m.skill.strength + m.skill.speed)
        sep = '---------------'
        header = 'Top Ten Members'
        counts = list(Counter([m.species_id for m in members]).items())
        counts.sort(key=lambda c: c[1])
        countstr = '\n'.join([f'Species {c[0]}: {c[1]}' for c in counts])
        statstr = '\n'.join([m.stats() for m in members[:10]])
        string = '\n'.join([header, sep, countstr, sep, statstr])
        self.scoreboard.set_text(string)
        # Draw Screen
        self.loop.draw_screen()


class Simulator:
    def __init__(self):
        self.num_species = 3
        self.num_members = 2
        self.num_resources = 15
        self.resource_spawn_rate = BASE_CHANCE//20
        self.width = 30
        self.height = 30
        self.map_obj = Map(width=self.width,height=self.height)
        self.pos_set = pos_set = set([(i,j) for i in range(self.width) for j in range(self.height)])
        self.win = Window()
        self.init_map();

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
                strength=lnv(RESOURCE_MEAN, RESOURCE_STDEV),
                speed=lnv(RESOURCE_MEAN, RESOURCE_STDEV))
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
                    strength=lnv(RESOURCE_MEAN, RESOURCE_STDEV),
                    speed=lnv(RESOURCE_MEAN, RESOURCE_STDEV))
                pos = choice(list(self.map_obj.empty_pos))
                self.map_obj.add(r, pos)
            sleep(uniform(0, BASE_CHANCE/self.resource_spawn_rate)/SIM_SPEED_MULT)

    def _ctrlc_handler(self, signal_received, frame):
        with self.map_obj.lock:
            self.map_obj.game_over = True

    def print_end_state(self):
        self.map_obj.check_game_over()

    def draw(self):
        self.win.draw(self.map_obj)

    def start(self):
        self.win.start()
        signal(SIGINT, self._ctrlc_handler)
        for m in self.members():
            m._thread.start()
        Thread(target=self._random_resource_inclusion_thread).start()
        while True:
            if active_count() == 1:
                break
            self.draw()
            sleep(.2)
        self.win.stop()
        self.print_end_state()
