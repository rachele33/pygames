#!/usr/bin/env python3
''' R.J. Dominoes '''
''' © 2014 Richard A. Benson <richardbenson91477@protonmail.com> '''
import sys, math, os, random, ctypes
import sdl2, sdl2.sdlmixer, sdl2.sdlimage

class domino:
    def __init__ (self):
        self.used = 0
        self.rot = 0
        # board tile indices
        self.tile1_i = [0, 0]
        self.tile2_i = [0, 0]
        # part values
        self.vals = [0, 0]
        # part image index
        self.ic = [0, 0]

class s:
    ''' global state '''
    win_s = 'rjdom'
    win_w, win_h = (600, 600)
    # win_rect_ref

    run_fps = 30
    # run_t_end, run_t_begin
    # run_frame_t, run_frame_t_ms

    # window, windowsurface
    # mouse_rect

    tile_w = 60

    # doms, grid
    # dom_c, tile_c, tile_c_valid
    # del_list, del_list_c
    # gameon, gameon_toggle
    # score, score_list, score_list_c

    LAYOUT_N = 9
    LAY_TILE, LAY_BOARD, LAY_POWER, LAY_SCORE, LAY_REMAIN,  LAY_CUR_A, \
        LAY_CUR_B, LAY_NEXT_A, LAY_NEXT_B =\
        range(LAYOUT_N)
    layout = [[] for c in range(LAYOUT_N)]

    # board_img, d_img, ld_img, misc_imgs
    IMG_SEL, IMG_INVALID, IMG_POINT, IMG_POWER0, IMG_POWER1 =\
        range(5)
    misc_imgs_s = ['sel', 'invalid', 'point', 'power0', 'power1']

    # snd_score, snd_fx

    # font_imgs
    # font_w, font_h, font_hw, font_hh
    # font_rect, font_rect_n
    # font_surf_score, font_surf_remain

def main ():
    res = init ()
    if res:
        return res

    event = sdl2.SDL_Event ()
    event_ref = ctypes.byref (event)

    done_ = False
    while not done_:
        while sdl2.SDL_PollEvent (event_ref) != 0:
            if event.type == sdl2.SDL_QUIT:
                done_ = True
                break
            elif event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym == sdl2.keycode.SDLK_ESCAPE:
                    done_ = True
                    break
            elif event.type == sdl2.SDL_MOUSEBUTTONUP:
                if event.button.button == 1:
                    on_declick (event.button.x, event.button.y)
            elif event.type == sdl2.SDL_MOUSEBUTTONDOWN:
                if event.button.button == 3:
                    on_click3 (event.button.x, event.button.y)
            elif event.type == sdl2.SDL_MOUSEMOTION:
                on_move (event.motion.x, event.motion.y)
        if done_:
            break
        tick ()
        paint ()

    deinit ()
    return 0

def init ():
    if sdl2.SDL_Init (sdl2.SDL_INIT_VIDEO | sdl2.SDL_INIT_AUDIO):
        return -1

    s.window = sdl2.SDL_CreateWindow (bytes(s.win_s, 'utf-8'),
        sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED,
        s.win_w, s.win_h,
        sdl2.SDL_WINDOW_SHOWN)
    if not s.window:
        return -2

    s.windowsurface = sdl2.SDL_GetWindowSurface (s.window)

    random.seed ()

    s.win_rect_ref = ctypes.byref (sdl2.SDL_Rect (0, 0, s.win_w, s.win_h))

    s.board_img = sdl2.sdlimage.IMG_Load (
        bytes (os.path.join ('data', 'board.png'), 'utf-8'))

    s.d_img, s.ld_img = [[],[]]
    for i in range(40):
        s.d_img += [sdl2.sdlimage.IMG_Load (
            bytes (os.path.join ('data', 'd' + '%.2d' % i + '.png'), 'utf-8'))]

        s.ld_img += [sdl2.sdlimage.IMG_Load (
            bytes (os.path.join ('data', 'ld' + '%.2d' % i + '.png'), 'utf-8'))]

    s.misc_imgs = [sdl2.sdlimage.IMG_Load (
        bytes (os.path.join ('data', str(n) + '.png'), 'utf-8'))
        for n in s.misc_imgs_s]

    s.font_imgs = [sdl2.sdlimage.IMG_Load (
        bytes (os.path.join ('data', 'font-' + str (fc) + '.png'),
        'utf-8'))
        for fc in range(10)]
    s.font_w = s.font_imgs[0].contents.w
    s.font_h = s.font_imgs[0].contents.h
    s.font_hw, s.font_hh = (s.font_w // 2, s.font_h // 2)
    s.font_rect = sdl2.SDL_Rect (0, 0, s.font_w * 3, s.font_h)
    s.font_rect_n = (
        sdl2.SDL_Rect (0, 0),
        sdl2.SDL_Rect (s.font_w, 0),
        sdl2.SDL_Rect (s.font_w * 2, 0))

    s.font_surf_score = sdl2.SDL_CreateRGBSurface (0, s.font_rect.w,
        s.font_rect.h, 32, 0, 0, 0, 0)
    s.font_surf_remain = sdl2.SDL_CreateRGBSurface (0, s.font_rect.w,
        s.font_rect.h, 32, 0, 0, 0, 0)

    sdl2.sdlmixer.Mix_OpenAudio (
        sdl2.sdlmixer.MIX_DEFAULT_FREQUENCY,
        sdl2.sdlmixer.MIX_DEFAULT_FORMAT,
        sdl2.sdlmixer.MIX_DEFAULT_CHANNELS,
        4096)
    sdl2.sdlmixer.Mix_Init (sdl2.sdlmixer.MIX_INIT_OGG)

    s.snd_score = [sdl2.sdlmixer.Mix_LoadWAV (
        bytes (os.path.join ('data', 'n' + '%d' % i + '.ogg'), 'utf-8'))
        for i in range(10)]

    s.snd_fx = [sdl2.sdlmixer.Mix_LoadWAV (
        bytes (os.path.join ('data', 'fx' + '%d' % i + '.ogg'), 'utf-8'))
        for i in range(4)]

    s.gameon = s.gameon_toggle = False

    init_layout ()

    s.score = 0
    render_score ();

    s.run_frame_t = 1.0 / s.run_fps
    s.run_frame_t_ms = int(s.run_frame_t * 1000.0)
    s.run_t_begin = s.run_t_end = sdl2.SDL_GetTicks ()
    return 0

def deinit ():
    sdl2.sdlmixer.Mix_Quit ()
    sdl2.SDL_DestroyWindow (s.window)
    sdl2.SDL_Quit ()

def tick ():
    s.run_t_end = sdl2.SDL_GetTicks ()
    _t = s.run_t_begin - s.run_t_end + s.run_frame_t_ms
    if _t > 0:
        sdl2.SDL_Delay (_t)
    s.run_t_begin = sdl2.SDL_GetTicks ()

    if not s.gameon:
        paint ()
        return

    if len (s.score_list):
        s.score_list_c += 1
        if s.score_list_c > 10:
            s.score_list_c = 0
            sc = s.score_list.pop ()
            s.score += sc[2]

            render_score ()

            sdl2.sdlmixer.Mix_PlayChannel (0, s.snd_score[sc[2] - 1], 0)

    elif s.gameon_toggle:
        end ()
        return

    elif len (s.del_list):
        s.del_list_c += 1
        if s.del_list_c > 5:
            s.del_list_c = 0
            y = s.del_list.pop ()
            d = s.doms[y]
            d.used = 0
            s.grid [d.tile1_i[0]][d.tile1_i[1]] = 0
            s.grid [d.tile2_i[0]][d.tile2_i[1]] = 0

            sdl2.sdlmixer.Mix_PlayChannel (0, s.snd_fx[2], 0)

def paint ():
    sdl2.SDL_BlitSurface (s.board_img, None, s.windowsurface,
        s.layout [s.LAY_BOARD])

    sdl2.SDL_BlitSurface (s.font_surf_score, None, s.windowsurface,
        s.layout [s.LAY_SCORE])

    if not s.gameon:
        sdl2.SDL_BlitSurface (s.misc_imgs[s.IMG_POWER0], None, s.windowsurface,
            s.layout [s.LAY_POWER])

        sdl2.SDL_UpdateWindowSurface (s.window)
        return

    sdl2.SDL_BlitSurface (s.misc_imgs[s.IMG_POWER1], None, s.windowsurface,
        s.layout [s.LAY_POWER])

    for d in s.doms:
        if d.used:
            sdl2.SDL_BlitSurface (s.d_img [d.ic[0]], None, s.windowsurface,
                s.layout [s.LAY_TILE][d.tile1_i[0]][d.tile1_i[1]])
            sdl2.SDL_BlitSurface (s.d_img [d.ic[1]], None, s.windowsurface,
                s.layout [s.LAY_TILE][d.tile2_i[0]][d.tile2_i[1]])

    d = s.doms [s.dom_c]

    if not s.tile_c_valid:
        sdl2.SDL_BlitSurface (s.misc_imgs[s.IMG_INVALID], None, s.windowsurface,
            s.layout [s.LAY_TILE][d.tile1_i[0]][d.tile1_i[1]])
        if d.tile2_i [0] >= 0 and d.tile2_i[0] <= 7 \
            and d.tile2_i[1] >= 0 and d.tile2_i[1] <= 7:
                sdl2.SDL_BlitSurface (s.misc_imgs [s.IMG_INVALID], None,
                    s.windowsurface,
                    s.layout [s.LAY_TILE][d.tile2_i[0]][d.tile2_i[1]])

    elif s.tile_c_valid == 1:
        sdl2.SDL_BlitSurface (s.d_img[d.ic[0]], None, s.windowsurface,
            s.layout [s.LAY_TILE][d.tile1_i[0]][d.tile1_i[1]])
        sdl2.SDL_BlitSurface (s.d_img[d.ic[1]], None, s.windowsurface,
            s.layout [s.LAY_TILE][d.tile2_i[0]][d.tile2_i[1]])
        sdl2.SDL_BlitSurface (s.misc_imgs[s.IMG_SEL], None, s.windowsurface,
            s.layout [s.LAY_TILE][d.tile1_i[0]][d.tile1_i[1]])
        sdl2.SDL_BlitSurface (s.misc_imgs[s.IMG_SEL], None, s.windowsurface,
            s.layout [s.LAY_TILE][d.tile2_i[0]][d.tile2_i[1]])

    if len (s.score_list):
        sc = s.score_list [len (s.score_list) - 1]
        sdl2.SDL_BlitSurface (s.misc_imgs [s.IMG_POINT], None, s.windowsurface,
            s.layout [s.LAY_TILE][sc[0]][sc[1]])

    sdl2.SDL_BlitSurface (s.font_surf_remain, None, s.windowsurface,
        s.layout [s.LAY_REMAIN])

    if not s.gameon_toggle:
        sdl2.SDL_BlitSurface (s.ld_img [d.vals[0]], None, s.windowsurface,
            s.layout [s.LAY_CUR_A])
        sdl2.SDL_BlitSurface (s.ld_img [d.vals[1] + 20], None, s.windowsurface,
            s.layout [s.LAY_CUR_B])
        if s.dom_c < 54:
            d2 = s.doms [s.dom_c + 1]
            sdl2.SDL_BlitSurface (s.ld_img [d2.vals[0]], None, s.windowsurface,
                s.layout [s.LAY_NEXT_A])
            sdl2.SDL_BlitSurface (s.ld_img [d2.vals[1] + 20], None,
                s.windowsurface,
                s.layout [s.LAY_NEXT_B])

    sdl2.SDL_UpdateWindowSurface (s.window)

def on_click3 (mx, my):
    if s.gameon_toggle or (not s.gameon):
        return

    d = s.doms [s.dom_c]
    d.rot += 1
    if d.rot > 3:
        d.rot = 0

    sdl2.sdlmixer.Mix_PlayChannel (0, s.snd_fx [3], 0)

    prepare_dom_c ()

def on_move (mx, my):
    if s.gameon_toggle or (not s.gameon):
        return

    if mx >= s.tile_w and mx < s.tile_w * 9 and \
            my >= s.tile_w and my < s.tile_w * 9:
        tx = (mx - s.tile_w) // s.tile_w
        ty = (my - s.tile_w) // s.tile_w
    else:
        return

    if tx == s.tile_c[0] and ty == s.tile_c[1]:
        return

    s.tile_c[0], s.tile_c[1] = tx, ty
    prepare_dom_c ()

def on_declick (mx, my):
    if s.gameon_toggle:
        return

    if not s.gameon:
        if mx < s.tile_w and my < s.tile_w:
            begin ()
            #on_move (p)
        return

    if mx < s.tile_w and my < s.tile_w:
        end ()
        return

    if s.tile_c_valid != 1:
        sdl2.sdlmixer.Mix_PlayChannel (0, s.snd_fx[0], 0)
        return

    d = s.doms[s.dom_c]

    d.used = 1
    s.grid [d.tile1_i[0]][d.tile1_i[1]] = d.vals[0] + 1
    s.grid [d.tile2_i[0]][d.tile2_i[1]] = d.vals[1] + 1
    rot = d.rot
    sdl2.sdlmixer.Mix_PlayChannel (0, s.snd_fx[1], 0)

    calc_score ()

    s.dom_c += 1
    if s.dom_c > 54:
        s.dom_c = 0
        s.tile_c_valid = 2
        s.gameon_toggle = True
        return

    render_remain ()

    # out of space?
    check_space()

    d = s.doms[s.dom_c]
    d.rot = rot

    s.tile_c_valid = 2

def init_layout ():
    s.layout [s.LAY_TILE] = [[],[],[],[],[],[],[],[]]
    for cx in range(8):
        x = s.tile_w + cx * s.tile_w
        for cy in range(8):
            y = s.tile_w + cy * s.tile_w
            s.layout [s.LAY_TILE][cx] += [sdl2.SDL_Rect (x, y)]

    s.layout [s.LAY_BOARD] = sdl2.SDL_Rect (0, 0)
    s.layout [s.LAY_POWER] = sdl2.SDL_Rect (0, 0)
    x = s.tile_w // 4
    s.layout [s.LAY_CUR_A] = sdl2.SDL_Rect (x, s.tile_w * 2)
    s.layout [s.LAY_CUR_B] = sdl2.SDL_Rect (x, s.tile_w * 2 + s.tile_w // 2)
    s.layout [s.LAY_NEXT_A] = sdl2.SDL_Rect (x, s.tile_w * 4)
    s.layout [s.LAY_NEXT_B] = sdl2.SDL_Rect (x, s.tile_w * 4 + s.tile_w // 2)
    x = s.win_h // 2 - s.font_hw * 3
    y = s.font_hh
    s.layout [s.LAY_SCORE] = sdl2.SDL_Rect (x, y)
    y = s.win_h - s.font_h - s.font_hh
    s.layout [s.LAY_REMAIN] = sdl2.SDL_Rect (x, y)

def end ():
    s.gameon = s.gameon_toggle = False
    s.tile_c_valid = 2
    del s.grid
    del s.doms
    paint ()

def begin ():
    s.score = 0
    s.score_list_c = 0
    s.score_list = []
    render_score ()

    s.del_list_c = 0
    s.del_list = []

    s.dom_c = 0
    render_remain ()

    s.tile_c = [0, 0]
    s.tile_c_valid = 0

    s.gameon = True
    s.gameon_toggle = False

    s.grid = []
    for y in range(8):
        s.grid.append ([0] * 8)

    s.doms = []
    for y in range(10):
        for x in range(y, 10):
            d = domino ()
            d.vals[0] = x;
            d.vals[1] = y;
            s.doms += [d]

    random.shuffle (s.doms)

    prepare_dom_c ()

def render_remain ():
    remain = 55 - s.dom_c
    d1 = remain // 100
    d2 = remain % 100 // 10
    d3 = remain % 100 % 10

    sdl2.SDL_FillRect (s.font_surf_remain, ctypes.byref (s.font_rect),
        0xff000000)
    sdl2.SDL_BlitSurface (s.font_imgs[d1], None, s.font_surf_remain,
        s.font_rect_n[0])
    sdl2.SDL_BlitSurface (s.font_imgs[d2], None, s.font_surf_remain,
        s.font_rect_n[1])
    sdl2.SDL_BlitSurface (s.font_imgs[d3], None, s.font_surf_remain,
        s.font_rect_n[2])

def render_score ():
    d1 = s.score // 100
    d2 = s.score % 100 // 10
    d3 = s.score % 100 % 10

    sdl2.SDL_FillRect (s.font_surf_score, ctypes.byref (s.font_rect),
        0xff000000)
    sdl2.SDL_BlitSurface (s.font_imgs[d1], None, s.font_surf_score,
        s.font_rect_n[0])
    sdl2.SDL_BlitSurface (s.font_imgs[d2], None, s.font_surf_score,
        s.font_rect_n[1])
    sdl2.SDL_BlitSurface (s.font_imgs[d3], None, s.font_surf_score,
        s.font_rect_n[2])

def calc_score ():
    d = s.doms[s.dom_c]
    p1 = d.vals[0] + 1
    p2 = d.vals[1] + 1

    loose = 0

    if p1 != 1:
        unc, empty = 0, 0
        valid = False
        if d.tile1_i[1] < 7 and d.rot != 0:
            v = s.grid [d.tile1_i[0]][d.tile1_i[1] + 1]
            if v == 1 or v == p1:
                valid = True
            elif not v:
                empty += 1
        else:
            unc += 1
        if d.tile1_i[0] > 0 and d.rot != 1:
            v = s.grid [d.tile1_i[0] - 1][d.tile1_i[1]]
            if v == 1 or v == p1:
                valid = True
            elif not v:
                empty += 1
        else:
            unc += 1
        if d.tile1_i[1] > 0 and d.rot != 2:
            v = s.grid [d.tile1_i[0]][d.tile1_i[1] - 1]
            if v == 1 or v == p1:
                valid = True
            elif not v:
                empty += 1
        else:
            unc += 1
        if d.tile1_i[0] < 7 and d.rot != 3:
            v = s.grid [d.tile1_i[0] + 1][d.tile1_i[1]]
            if v == 1 or v == p1:
                valid = True
            elif not v:
                empty += 1
        else:
            unc += 1

        if empty == 4 - unc:
            loose += 1
        elif not valid:
            return

    if p2 != 1:
        unc, empty = 0, 0
        valid = False
        if d.tile2_i[1] < 7 and d.rot != 2:
            v = s.grid [d.tile2_i[0]][d.tile2_i[1] + 1]
            if v == 1 or v == p2:
                valid = True
            elif not v:
                empty += 1
        else:
            unc += 1
        if d.tile2_i[0] > 0 and d.rot != 3:
            v = s.grid [d.tile2_i[0] - 1][d.tile2_i[1]]
            if v == 1 or v == p2:
                valid = True
            elif not v:
                empty += 1
        else:
            unc += 1
        if d.tile2_i[1] > 0 and d.rot != 0:
            v = s.grid [d.tile2_i[0]][d.tile2_i[1] - 1]
            if v == 1 or v == p2:
                valid = True
            elif not v:
                empty += 1
        else:
            unc += 1
        if d.tile2_i[0] < 7 and d.rot != 1:
            v = s.grid [d.tile2_i[0] + 1][d.tile2_i[1]]
            if v == 1 or v == p2:
                valid = True
            elif not v:
                empty += 1
        else:
            unc += 1

        if empty == 4 - unc:
            loose += 1
        elif not valid:
            return

    if loose == 2:
        return

    if d.tile1_i[1] < 7 and d.rot != 0:
        v = s.grid [d.tile1_i[0]][d.tile1_i[1] + 1]
        if v:
            s.score_list += [[d.tile1_i[0], d.tile1_i[1] + 1, v]]
    if d.tile1_i[0] > 0 and d.rot != 1:
        v = s.grid [d.tile1_i[0] - 1][d.tile1_i[1]]
        if v:
            s.score_list += [[d.tile1_i[0] - 1, d.tile1_i[1], v]]
    if d.tile1_i[1] > 0 and d.rot != 2:
        v = s.grid [d.tile1_i[0]][d.tile1_i[1] - 1]
        if v:
            s.score_list += [[d.tile1_i[0], d.tile1_i[1] - 1, v]]
    if d.tile1_i[0] < 7 and d.rot != 3:
        v = s.grid [d.tile1_i[0] + 1][d.tile1_i[1]]
        if v:
            s.score_list += [[d.tile1_i[0] + 1, d.tile1_i[1], v]]

    if d.tile2_i[1] < 7 and d.rot != 2:
        v = s.grid [d.tile2_i[0]][d.tile2_i[1] + 1]
        if v:
            s.score_list += [[d.tile2_i[0], d.tile2_i[1] + 1, v]]
    if d.tile2_i[0] > 0 and d.rot != 3:
        v = s.grid [d.tile2_i[0] - 1][d.tile2_i[1]]
        if v:
            s.score_list += [[d.tile2_i[0] - 1, d.tile2_i[1], v]]
    if d.tile2_i[1] > 0 and d.rot != 0:
        v = s.grid [d.tile2_i[0]][d.tile2_i[1] - 1]
        if v:
            s.score_list += [[d.tile2_i[0], d.tile2_i[1] - 1, v]]
    if d.tile2_i[0] < 7 and d.rot != 1:
        v = s.grid [d.tile2_i[0] + 1][d.tile2_i[1]]
        if v:
            s.score_list += [[d.tile2_i[0] + 1, d.tile2_i[1], v]]

def check_space ():
    for y in range(8):
        for x in range(8):
            if not s.grid [x][y]:
                if x < 7:
                    if not s.grid [x + 1][y]:
                        return
                if y < 7:
                    if not s.grid [x][y + 1]:
                        return

    x, y = 0, 0
    while (x < 16 and y < s.dom_c):
        d = s.doms[y]
        if not d.used:
            y += 1
            continue
        x += 1
        s.del_list += [y]
        y += 1

def prepare_dom_c ():
    d = s.doms[s.dom_c]
    d.tile1_i[0], d.tile1_i[1] = s.tile_c[0], s.tile_c[1]

    if d.rot == 0:
        d.tile2_i[0] = s.tile_c[0]
        d.tile2_i[1] = s.tile_c[1] + 1
        d.ic = [d.vals[0], d.vals[1] + 20]
    elif d.rot == 1:
        d.tile2_i[0] = s.tile_c[0] - 1
        d.tile2_i[1] = s.tile_c[1]
        d.ic = [d.vals[0] + 10, d.vals[1] + 30]
    elif d.rot == 2:
        d.tile2_i[0] = s.tile_c[0]
        d.tile2_i[1] = s.tile_c[1] - 1
        d.ic = [d.vals[0] + 20, d.vals[1]]
    elif d.rot == 3:
        d.tile2_i[0] = s.tile_c[0] + 1
        d.tile2_i[1] = s.tile_c[1]
        d.ic = [d.vals[0] + 30, d.vals[1] + 10]

    if d.tile2_i[0] < 0 or d.tile2_i[1] < 0:
        s.tile_c_valid = 0
    elif d.tile2_i[0] > 7 or d.tile2_i[1] > 7:
        s.tile_c_valid = 0
    elif s.grid [d.tile1_i[0]][d.tile1_i[1]] or\
            s.grid [d.tile2_i[0]][d.tile2_i[1]]:
        s.tile_c_valid = 0;
    else:
        s.tile_c_valid = 1

if __name__ == '__main__':
    sys.exit (main ())

