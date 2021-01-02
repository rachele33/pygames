''' © 2014 Richard A. Benson <richardbenson91477@gmail.com> '''
import math, os
import sdl2
from path import Path

class Being:
    # pos, rad, rot_n
    # img_s, img_sets, img_sets_n, img_rect
    # img_len, img_tick, img_cur
    # path, path_curves_n
    # path_rate, path_tick, path_tick_max

    def __init__ (self, img_s, img_sets_n, img_len, path_rate,
            path_data):
        self.pos = (0, 0)
        self.rad = 0
        self.rot_n = 0
        self.img_s = img_s
        self.img_sets_n = img_sets_n
        self.img_len = img_len
        self.img_rect = sdl2.SDL_Rect ()
        self.path_rate = path_rate
        self.path = False

        self.img_sets = [None] * img_sets_n
        for i in range (img_sets_n):
            self.img_sets[i] = [sdl2.sdlimage.IMG_Load (
                bytes (os.path.join ('data',
                    img_s + '_' + str(i) + '_' + str(j) + '.png'),
                    'utf-8'))
                for j in range (36)]

        iw = self.img_sets[0][0].contents.w
        self.rad = iw // 2

        if path_data:
            self.path = Path ()
            self.path_curves_n = len (path_data) // 4
            self.path_tick_max = float(self.path_curves_n)
            for c in range (self.path_curves_n):
                c2 = c * 4
                self.path.curve_add (
                    path_data[c2],
                    path_data[c2 + 1],
                    path_data[c2 + 2],
                    path_data[c2 + 3])

        self.reset ()

    def tick (self, t):
        self.img_tick += t
        if self.img_tick >= self.img_len:
            self.img_tick -= self.img_len
            self.img_cur += 1
            if self.img_cur == self.img_sets_n:
                self.img_cur = 0

        if self.path:
            self.path_tick += t * self.path_rate
            if self.path_tick >= self.path_tick_max:
                self.path_tick -= self.path_tick_max

            self.path_eval ()

    def reset (self):
        self.img_cur = 0
        self.img_tick = 0.0
        if self.path:
            self.path_tick = 0
            self.path_eval ()

    def set_pos (self, x, y):
        self.pos = (x, y)
        self.img_rect.x = x - self.rad
        self.img_rect.y = y - self.rad

    def set_rot_n (self, rot_n):
        self.rot_n = rot_n

    def path_eval (self):
        pos = self.path.curve_eval (self.path_tick)
        self.set_pos (pos[0], pos[1])

        # find movement angle
        t_ahead = 0.2
        a_tick = self.path_tick + t_ahead
        if a_tick >= self.path_tick_max:
            a_tick -= self.path_tick_max
        angle_pos = self.path.curve_eval (a_tick)
        a = math.degrees (math.atan2 (\
            pos[0] - angle_pos[0],
            pos[1] - angle_pos[1]))
        while (a < 0):
            a += 360
        while (a >= 360):
            a -= 360
        self.set_rot_n (int(a / 10))

    def paint (self, windowsurface):
        sdl2.SDL_BlitSurface (self.img_sets[self.img_cur][self.rot_n], None,
            windowsurface, self.img_rect)

    def cir_col (self, x, y, rad):
        d = math.sqrt (((x - self.pos[0]) ** 2) + ((y - self.pos[1]) ** 2))
        if d < rad + self.rad:
            return True
        else:
            return False

