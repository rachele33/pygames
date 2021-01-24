''' © 2014 Richard A. Benson <richardbenson91477@protonmail.com> '''
import math, os
import sdl2

class s:
    imgs_s = ['cheddar', 'mwater']
    imgs = []

class Item:
    # _id
    # pos, rad, rot_n
    # img, img_rect, img_rad
    # active

    def __init__ (self, _id, img, pos, rad):
        if not img:
            return False

        self._id = _id
        self.pos = pos
        self.rad = rad
        self.img = img

        iw = img.contents.w
        self.img_rad = iw // 2
        self.img_rect = sdl2.SDL_Rect (\
            pos[0] - self.img_rad, pos[1] - self.img_rad)

        self.reset()

    def reset (self):
        self.active = True

    def set_pos (self, x, y):
        self.pos = (x, y)
        self.img_rect.x = x - self.img_rad
        self.img_rect.y = y - self.img_rad

    def paint (self, windowsurface):
        if self.active:
            sdl2.SDL_BlitSurface (self.img, None, windowsurface, self.img_rect)

    def cir_col (self, x, y, rad):
        if not self.active:
            return False

        d = math.sqrt (((x - self.pos[0]) ** 2) + ((y - self.pos[1]) ** 2))
        if d < rad + self.rad:
            return True
        else:
            return False

def init_imgs ():
    s.imgs = [sdl2.sdlimage.IMG_Load (
        bytes (os.path.join ('data', fn + '.png'), 'utf-8'))
        for fn in s.imgs_s]

