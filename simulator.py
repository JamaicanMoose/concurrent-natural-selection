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
        self.num_species = 2
        self.num_members = 3
        self.num_resources = 15
        self.user_skill = 0
        self.user_speed = 0
        self.user_strength = 0
        self.user_params()
        self.map_obj = Map(width=self.width,height=self.height)
        self.pos_set = set([(i,j)
                     for i in range(self.height) for j in range(self.width)])
        self.win = Window()
        self.init_map();

    def create_species(self):
        '''Takes in user specifications for strength/speed of species 
             they are rooting for on the board'''
        print("You will be species 0.")
        self.user_speed = float(input("Enter speed of your species (0-3): ")
                                or uniform(0,3))
        self.user_strength = float(input(
                                "Enter strength of your species (0-10): ") 
                                or uniform(0,10))

    def user_params(self):
        '''Initializes simulation data with user preferences.'''
        self.num_species = int(input(
                            "Enter number of species on board (Default: 3): ") 
                                or 3)
        self.num_members = int(input(
                        "Enter number of members per species (Default: 2): ") 
                                or 2)
        self.num_resources = int(input(
                    "Enter number of resources on the board (Default: 15) : ") 
                                or 15)
        if input("Would you like to create a species? ") == 'Y':
            self.create_species() 
        else:
            self.user_speed = uniform(0,3)
            self.user_strength = uniform(0,10)
        dimension = int(math.ceil(math.sqrt(
                    self.num_resources + self.num_species 
                    * self.num_members * 1.5)))
        self.width = dimension
        self.height = dimension
        print(f"Minimum Number of Spaces: {dimension**2}")
        while(self.width*self.height < dimension**2):
            self.width = int(input("Enter width of the board") or dimension)
            self.height = int(input("Enter height of the board") or dimension)
            if self.width*self.height < dimension**2:
                print("Not enough space on board for specified items!")

    def init_map(self):
        '''Creates members of each species, with 
           random attributes characteristic to each species.
            Places members and resources on the map.'''
        for i in range(self.num_members):
            #Creates members of species user is rooting for.
            skill= Skill(strength=self.user_strength, speed=self.user_speed)
            m = Member(
                draw_fn=self.draw,
                map_obj=self.map_obj,
                skill=skill,
                species_id=0,
                reproduction_chance=BASE_CHANCE//10)
            pos = choice(list(self.pos_set))
            self.pos_set.remove(pos)
            self.map_obj.add(m, pos)
        for i in range(1, self.num_species):
            for j in range(self.num_members):
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
            #Add extra types of skills to the resource at random
            if random.random() > 0.75:
                r.add_to_bag()
            pos = choice(list(self.pos_set))
            self.pos_set.remove(pos)
            self.map_obj.add(r, pos)

    def members(self):
        return [self.map_obj.at(pos) for pos in self.map_obj.members.values()]

    def _random_resource_inclusion_thread(self):
        '''Adds resources with random attributes to the board at a rate
        determined by the resource spawn rate and simulation speed'''
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
            sleep(uniform(
                0, BASE_CHANCE/self.resource_spawn_rate)/SIM_SPEED_MULT)

    def _ctrlc_handler(self, signal_received, frame):
        '''Allows simulation to quit cleanly if interrupted before it ends'''
        with self.map_obj.lock:
            self.map_obj.game_over = True

    def print_end_state(self):
        '''Prints the winning species/ result of the simulation.
        The simulation is over if there are 1 or 0 species left on the board.'''
        counts = list(self.map_obj.species_counts.items())
        if len(counts) == 1:
            print(f'Species {counts[0][0]} wins!')
        elif len(counts) == 0:
            print(f'All species dead.')

    def draw(self):
        '''renders map object for GUI.'''
        self.win.draw(self.map_obj)

    def start(self):
        '''Starts threads for members, and resource inclusion thread. Renders
        GUI until the simulation is over.'''
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
