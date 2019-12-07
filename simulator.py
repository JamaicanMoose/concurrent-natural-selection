# pylint: skip-file
import math
from random import randint, choice, uniform
from random import lognormvariate as lnv
from concurrent.futures import ThreadPoolExecutor
from threading import Thread, Event, active_count
from time import sleep, time
from signal import signal, SIGINT
import random
from map import Map
from gui import Window
from member import Member
from skill import Skill, Resource
from defs import SIM_SPEED_MULT, BASE_CHANCE, RESOURCE_MEAN, RESOURCE_STDEV

class Simulator:
    def __init__(self):
        self.resource_spawn_rate = BASE_CHANCE//20
        self.user_params();
        self.map_obj = Map(width=self.width,height=self.height)
        self.pos_set = set([(i,j) for i in range(self.height) for j in range(self.width)])
        self.win = Window()
        self.init_map();

    def user_params(self):
            self.num_species = int(input("Enter number of species on board (Default: 3) : ") or 3)
            self.num_members = int(input("Enter number of members per species (Default: 2) : ") or 2)
            self.num_resources = int(input("Enter number of resources on the board (Default: 15) : ") or 15)
            dimension = int(math.ceil(math.sqrt(self.num_resources + self.num_species * self.num_members * 1.5)))
            self.width = 0
            self.height = 0
            print(f"Minimum Number of Spaces: {dimension**2}")
            while(self.width*self.height < dimension**2):
                self.width = int(input("Enter width of the board : ") or dimension)
                self.height = int(input("Enter height of the board : ") or dimension)
                if self.width*self.height < dimension**2:
                    print("There isnt enough space on the board for the specified items!")

    def init_map(self):
        for i in range(self.num_species):
            for _ in range(self.num_members):
                skill=Skill(strength=uniform(0,10), speed=uniform(0,3))
                m = Member(
                    draw_fn=self.draw,
                    map_obj=self.map_obj,
                    skill=skill,
                    species_id=i,
                    reproduction_chance=BASE_CHANCE//10)
                pos = choice(list(self.pos_set))
                self.pos_set.remove(pos)
                self.map_obj.add(m, pos)
        for _ in range(self.num_resources):
            r = Resource(
                strength=1+random.random(),
                speed=1+random.random())
            if random.random() > 0.75:
                r.add_to_bag()
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
                    strength=1+random.random(),
                    speed=1+random.random())
                if random.random() > 0.75:
                    r.add_to_bag()
                pos = choice(list(self.map_obj.empty_pos))
                self.map_obj.add(r, pos)
            sleep(uniform(0, BASE_CHANCE/self.resource_spawn_rate)/SIM_SPEED_MULT)

    def _ctrlc_handler(self, signal_received, frame):
        with self.map_obj.lock:
            self.map_obj.game_over = True

    def print_end_state(self):
        counts = list(self.map_obj.species_counts.items())
        if len(counts) == 1:
            print(f'Species {counts[0][0]} wins!')
        elif len(counts) == 0:
            print(f'All species dead.')

    def draw(self):
        self.win.draw(self.map_obj)

    def start(self):
        self.win.start()
        signal(SIGINT, self._ctrlc_handler)
        for m in self.members():
            m._thread.start()
        Thread(target=self._random_resource_inclusion_thread).start()
        while True:
            with self.map_obj.lock:
                if self.map_obj.is_game_over:
                    break
                self.draw()
            sleep(.2)
        self.win.stop()
        self.print_end_state()
