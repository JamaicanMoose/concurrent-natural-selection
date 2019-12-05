import urwid
from collections import Counter

BEST = 28 # green_4
BETTER = 112 # chartreuse_2b
NORMAL = 208 # dark_orange
WORSE = 220 # gold_1
WORST = 124 # red_3a

class Window:
    def __init__(self):
        self.map = urwid.Text('')
        self.scoreboard = urwid.Text('')
        self.widgetlist = [urwid.Filler(w, 'top') for w in [self.map, self.scoreboard]]
        self.win = urwid.Columns(self.widgetlist, dividechars=2)
        self.loop = urwid.MainLoop(self.win)
        self.loop.screen.set_terminal_properties(colors=256)
        palette = [
            ('best', 'white', 'default', None, None, 'h28'),
            ('better', 'white', 'default', None, None, 'h112'),
            ('normal', 'white', 'default', None, None, 'h208'),
            ('worse', 'white', 'default', None, None, 'h220'),
            ('worst', 'white', 'default', None, None, 'h124')
        ]
        self.loop.screen.register_palette(palette)

    def start(self):
        self.loop.start()

    def stop(self):
        self.loop.stop()

    def draw(self, map_obj):
        # Render Map
        self.map.set_text(map_obj.markup())
        # Render Scoreboard
        members = [map_obj.at(pos) for pos in map_obj.members.values()]
        members.sort(key=lambda m: m.skill.strength + m.skill.speed)
        sep = '---------------'
        header = 'Top Ten Members'
        counts = list(map_obj.species_counts.items())
        counts.sort(key=lambda c: c[1])
        countstr = '\n'.join([f'Species {c[0]}: {c[1]}' for c in counts])
        statstr = '\n'.join([m.stats() for m in members[:10]])
        string = '\n'.join([header, sep, countstr, sep, statstr])
        self.scoreboard.set_text(string)
        # Draw Screen
        self.loop.draw_screen()