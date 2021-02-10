''' © 2014 Richard A. Benson <richardbenson91477@protonmail.com> '''
import os, json
import sdl2, sdl2.sdlimage

import item
from being import Being

class s:
    maps = []
    maps_n = 0

class Map:
    def __init__ (self):
        self.rects = []
        self.arcs = []
        self.items = []
        self.beings = []
        self.img = []

    def set_begin (self, begin_pos, begin_siz):
        self.begin_pos = begin_pos
        self.begin_siz = begin_siz
        self.begin_center = (
            begin_pos[0] + begin_siz[0] // 2,
            begin_pos[1] + begin_siz[1] // 2)

    def set_end (self, end_pos, end_siz):
        self.end_pos = end_pos
        self.end_siz = end_siz

    def add_rect (self, pos, siz):
        self.rects.append((pos, siz))

    def add_arc (self, pos, siz):
        self.arcs.append((pos, siz))

    def add_item (self, _item):
        self.items.append(_item)

    def add_being (self, being):
        self.beings.append(being)

    def paint_img (self, windowsurface):
        sdl2.SDL_BlitSurface (self.img, None, windowsurface, None)

    def paint_ents (self, windowsurface):
        for being in self.beings:
            being.paint (windowsurface)

        for _item in self.items:
            _item.paint (windowsurface)

    def load_img (self, img_fn):
        self.img = sdl2.sdlimage.IMG_Load (bytes (img_fn, 'utf-8'))

def load_maps ():
    item.init_imgs ()

    ifn = os.path.join ('data', 'maps.json')

    f = open (ifn, 'r')
    maps_data = json.load (f)
    f.close ()

    s.maps_n = len (maps_data)

    s.maps = []
    for c in range (s.maps_n):
        map_data = maps_data[c]

        _map = Map ()

        _map.set_begin (
            map_data['doors']['begin']['pos'],
            map_data['doors']['begin']['siz'])

        _map.set_end (
            map_data['doors']['end']['pos'],
            map_data['doors']['end']['siz'])

        _map.load_img (
            os.path.join ('data', 'map_' + str(c) + '.png'))

        for rect in map_data['rects']:
            _map.add_rect (
                rect['pos'],
                rect['siz'])

        for arc in map_data['arcs']:
            _map.add_arc (
                arc['pos'],
                arc['siz'])

        for _item in map_data['items']:
            _map.add_item (item.Item (
                _item['id'],
                item.s.imgs[item.s.imgs_s.index (_item['id'])],
                _item['pos'],
                _item['rad']))

        for being in map_data['beings']:
            _map.add_being (Being (
                being['img_s'],
                being['img_sets_n'],
                being['img_len'],
                being['path_rate'],
                being['path_data']))

        s.maps.append(_map)

def reset_maps ():
    for _map in s.maps:
        for _item in _map.items:
            _item.reset ()
        for being in _map.beings:
            being.reset ()

