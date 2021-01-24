#!/usr/bin/env python3
''' © 2014 Richard A. Benson <richardbenson91477@protonmail.com> '''
import sys, math, os, random, ctypes
import sdl2, sdl2.sdlmixer, sdl2.sdlimage

#from item import Item
from being import Being
import _map

class s:
    ''' global state '''
    #skip_intro = False
    skip_intro = True

    win_s = 'Turtle Crackers'
    win_w, win_h = (600, 600)
    win_stat_h = 50
    # win_rect_ref

    run_fps = 25
    # run_t_begin, run_t_end
    # run_frame_t, run_frame_t_ms

    # window, windowsurface

    LAYOUT_N = 5
    LAY_STAT, LAY_STAT_LIVES, LAY_STAT_LIVES2,\
            LAY_STAT_MWATER, LAY_STAT_MWATER2 =\
        range(LAYOUT_N)
    layout = [[] for c in range(LAYOUT_N)]

    # map_cur, map_cur_n
    # map_w, map_h

    # bub_x, bub_y, bub_rad, bub_rad_col
    bub_pos_last_n = 8
    # bub_img_rect

    # turt_active, turt_lives, turt_mwater
    turt_mwater_init = 10
    turt_mwater_rate = 1.0
    # turt_mwater_tick
    # turt_being

    IMG_INTRO, IMG_INTRO2, IMG_INTRO3,\
        IMG_BUBBLE, IMG_CRUNCH, IMG_STAT, \
        IMG_READY, IMG_GO, IMG_GAMEOVER =\
        range(9)
    imgs_s = [
        'intro0000', 'intro0001', 'intro0002',
        'bub', 'turt_crunch', 'stat',
        'ready', 'go', 'gameover']
    # imgs

    # font_imgs

    GAME_INTRO, GAME_INTRO2, GAME_INTRO3,\
            GAME_READY, GAME_GO, GAME_ON, GAME_OVER, GAME_NONE =\
        range(8)

    game_states = (
        # len, img, next
        (0.5, IMG_INTRO, GAME_NONE),
        (1.5, IMG_INTRO2, GAME_INTRO3),
        (1.5, IMG_INTRO3, GAME_READY),
        (1.0, IMG_READY, GAME_GO),
        (0.5, IMG_GO, GAME_ON),
        (0.0, False, GAME_NONE),
        (2.0, IMG_GAMEOVER, GAME_INTRO)
        )
    # game_state, game_state_tick
    # game_state_len, game_state_img, game_state_next
    # game_state_hlen

    SND_CRUNCH, SND_ITEM, SND_MAGIC1 = \
        range(3)
    snds_s = [
        'crunch', 'item', 'magic1']
    # snds

def main ():
    res = init ()
    if res:
        return res

    event = sdl2.SDL_Event ()
    event_ref = ctypes.byref (event)

    done = False
    while not done:
        while sdl2.SDL_PollEvent (event_ref) != 0:
            if event.type == sdl2.SDL_QUIT:
                done = True
                break
            elif event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym == sdl2.keycode.SDLK_ESCAPE:
                    done = True
                    break
            elif event.type == sdl2.SDL_MOUSEBUTTONDOWN:
                if event.button.button is 1:
                    on_click (event.button.x, event.button.y)
            elif event.type == sdl2.SDL_MOUSEMOTION:
                on_move (event.motion.x, event.motion.y)
        if done:
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

    sdl2.mouse.SDL_ShowCursor (False)

    random.seed ()

    s.win_rect_ref = ctypes.byref (sdl2.SDL_Rect (0, 0, s.win_w, s.win_h))

    s.imgs = [sdl2.sdlimage.IMG_Load (
        bytes (os.path.join ('data', fn + '.png'), 'utf-8'))
        for fn in s.imgs_s]

    s.font_imgs = [sdl2.sdlimage.IMG_Load (
        bytes (os.path.join ('data', 'font-' + str(n) + '.png'), 'utf-8'))
        for n in range(10)]

    sdl2.sdlmixer.Mix_OpenAudio (
        sdl2.sdlmixer.MIX_DEFAULT_FREQUENCY,
        sdl2.sdlmixer.MIX_DEFAULT_FORMAT,
        sdl2.sdlmixer.MIX_DEFAULT_CHANNELS,
        4096)
    sdl2.sdlmixer.Mix_Init (sdl2.sdlmixer.MIX_INIT_OGG)

    s.snds = [sdl2.sdlmixer.Mix_LoadWAV (
        bytes (os.path.join ('data', fn + '.ogg'), 'utf-8'))
        for fn in s.snds_s]

    s.map_w = s.win_w
    s.map_h = s.win_h - s.win_stat_h

    s.turt_being = Being ('turt', 2, 1.0, 0.0, False)

    bw = s.imgs[s.IMG_BUBBLE].contents.w
    s.bub_rad = bw // 2
    s.bub_rad_col = int(bw / math.pi)

    init_layout ()

    _map.load_maps ()

    if s.skip_intro:
        game_set_state (s.GAME_READY)
        init_game ()
    else:
        game_set_state (s.GAME_INTRO)

    s.turt_active = False

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

    if s.game_state == s.GAME_ON:
        if s.turt_active:
            s.turt_being.tick (s.run_frame_t)
            s.turt_mwater_tick += s.run_frame_t
            if s.turt_mwater_tick >= s.turt_mwater_rate:
                s.turt_mwater_tick = 0
                s.turt_mwater -= 1
                if s.turt_mwater == 0:
                    game_crunch ()
                    return

        for being in s.map_cur.beings:
            being.tick (s.run_frame_t)
            if s.turt_active and being.path:
                # being > bubble collision
                if being.cir_col (s.bub_x, s.bub_y, s.bub_rad_col):
                    game_crunch ()
                    return
    else:
        s.game_state_tick += s.run_frame_t
        if s.game_state_next != s.GAME_NONE:
            if s.game_state_tick >= s.game_state_len:
                game_set_state (s.game_state_next)
                if s.game_state == s.GAME_READY:
                    init_game ()
                elif s.game_state == s.GAME_ON:
                    game_on ()

def paint ():
    if s.game_state > s.GAME_INTRO3:
        # status bar
        sdl2.SDL_BlitSurface (s.imgs[s.IMG_STAT], None, s.windowsurface,
            s.layout[s.LAY_STAT])

        if s.turt_lives < 10:
            sdl2.SDL_BlitSurface (s.font_imgs[s.turt_lives], None,
                s.windowsurface, s.layout[s.LAY_STAT_LIVES])
        else:
            sdl2.SDL_BlitSurface (s.font_imgs[s.turt_lives // 10],
                None, s.windowsurface, s.layout[s.LAY_STAT_LIVES])
            sdl2.SDL_BlitSurface (s.font_imgs[s.turt_lives % 10],
                None, s.windowsurface, s.layout[s.LAY_STAT_LIVES2])

        if s.turt_mwater < 10:
            sdl2.SDL_BlitSurface (s.font_imgs[s.turt_mwater], None,
                s.windowsurface, s.layout[s.LAY_STAT_MWATER])
        else:
            sdl2.SDL_BlitSurface (s.font_imgs[s.turt_mwater // 10],
                None, s.windowsurface, s.layout[s.LAY_STAT_MWATER])
            sdl2.SDL_BlitSurface (s.font_imgs[s.turt_mwater % 10],
                None, s.windowsurface, s.layout[s.LAY_STAT_MWATER2])

        s.map_cur.paint_img (s.windowsurface)

        # turtle (inactive)
        if not s.turt_active:
            sdl2.SDL_BlitSurface (s.imgs[s.IMG_CRUNCH], None, s.windowsurface,
                s.bub_img_rect)

        s.map_cur.paint_ents (s.windowsurface)

        # turtle (active)
        if s.turt_active:
            s.turt_being.paint (s.windowsurface)
            sdl2.SDL_BlitSurface (s.imgs[s.IMG_BUBBLE], None, s.windowsurface,
                s.bub_img_rect)

        # game messages
        if s.game_state != s.GAME_ON:
            sdl2.SDL_BlitSurface (s.game_state_img, None, s.windowsurface, None)

        if s.game_state == s.GAME_OVER:
            if s.game_state_tick > s.game_state_hlen:
                paint_fade_out (s.game_state_tick - s.game_state_hlen,
                    s.game_state_hlen)

    # intro image
    elif s.game_state == s.GAME_INTRO:
        sdl2.SDL_BlitSurface (s.game_state_img, None, s.windowsurface, None)
        if s.game_state_tick < s.game_state_len:
            paint_fade_in (s.game_state_tick, s.game_state_len)

    # intro scenes
    else:
        sdl2.SDL_BlitSurface (s.game_state_img, None, s.windowsurface, None)

    sdl2.SDL_UpdateWindowSurface (s.window)

def paint_fade_in (cur, _max):
    a = 255 - int((cur / _max) * 255.0)
    sdl2.SDL_FillRect (s.windowsurface, s.win_rect_ref, a)

def paint_fade_out (cur, _max):
    a = int((cur / _max) * 255.0)
    sdl2.SDL_FillRect (s.windowsurface, s.win_rect_ref, a)

def on_click (mx, my):
    if s.game_state == s.GAME_ON:
        if not s.turt_active:
            game_on ()
            s.turt_mwater = s.turt_mwater_init
            s.turt_mwater_tick = 0.0
            return
    elif s.game_state == s.GAME_INTRO:
        game_set_state (s.GAME_INTRO2)

def on_move (mx, my):
    if s.game_state != s.GAME_ON:
        return

    if not s.turt_active:
        return

    s.bub_x = mx
    s.bub_y = my
    s.bub_img_rect.x = s.bub_x - s.bub_rad
    s.bub_img_rect.y = s.bub_y - s.bub_rad

    # turtle tracks bubble
    s.turt_being.set_pos (s.bub_x, s.bub_y)

    # find movement angle
    s.bub_pos_last.insert (0, (s.bub_x, s.bub_y))
    angle_pos = s.bub_pos_last.pop ()
    a = -90 + math.degrees (math.atan2 (\
        s.bub_x - angle_pos[0],
        s.bub_y - angle_pos[1]))
    while (a < 0): a += 360
    while (a >= 360): a -= 360
    s.turt_being.set_rot_n (int(a / 10))

    # bubble > begin zone collision
    if cir_rect_col (
            s.bub_x, s.bub_y, s.bub_rad_col,
            s.map_cur.begin_pos[0], s.map_cur.begin_pos[1],
            s.map_cur.begin_siz[0], s.map_cur.begin_siz[1]):
        # return to ignore further collisions
        return

    # bubble > end zone collision
    if cir_rect_col (
            s.bub_x, s.bub_y, s.bub_rad_col,
            s.map_cur.end_pos[0], s.map_cur.end_pos[1],
            s.map_cur.end_siz[0], s.map_cur.end_siz[1]):
        win_room ()
        return

    # bubble > wall collision
    if \
            s.bub_x + s.bub_rad_col > s.map_w or \
            s.bub_x - s.bub_rad_col < 0 or \
            s.bub_y + s.bub_rad_col > s.map_h or \
            s.bub_y - s.bub_rad_col < 0:
        game_crunch ()
        return

    # bubble > rectangle collision
    for rect in s.map_cur.rects:
        if cir_rect_col (s.bub_x, s.bub_y, s.bub_rad_col,
                rect[0][0], rect[0][1], rect[1][0], rect[1][1]):
            game_crunch ()
            return

    # arc collisions
    for arc in s.map_cur.arcs:
        if cir_arc_col (s.bub_x, s.bub_y, s.bub_rad_col, arc[0], arc[1]):
            game_crunch ()
            return

    # bubble > item collision
    for _item in s.map_cur.items:
        if _item.cir_col (s.bub_x, s.bub_y, s.bub_rad_col):
            get_item (_item)
            _item.active = False

    # bubble > being collision
    for being in s.map_cur.beings:
        if being.cir_col (s.bub_x, s.bub_y, s.bub_rad_col):
            game_crunch ()
            return

def init_layout ():
    font_w = s.font_imgs[0].contents.w
    font_h = s.font_imgs[0].contents.h
    font_hw = font_w // 2
    font_hh = font_h // 2

    stat_w = s.win_w
    stat_h = s.win_stat_h
    stat_hw = stat_w // 2
    stat_hh = stat_h // 2
    stat_x = 0
    stat_y = s.win_h - stat_h

    s.layout[s.LAY_STAT] = sdl2.SDL_Rect (stat_x, stat_y)

    stat_lives_x = 64
    stat_lives_y = s.map_h + stat_hh - font_hh

    s.layout[s.LAY_STAT_LIVES] = sdl2.SDL_Rect (stat_lives_x, stat_lives_y)
    s.layout[s.LAY_STAT_LIVES2] = sdl2.SDL_Rect (stat_lives_x + font_w,
        stat_lives_y)

    s.layout[s.LAY_STAT_MWATER] = sdl2.SDL_Rect (stat_lives_x + stat_hw,
        stat_lives_y)
    s.layout[s.LAY_STAT_MWATER2] = sdl2.SDL_Rect (
        stat_lives_x + font_w + stat_hw,
        stat_lives_y)

def cir_rect_col (p1x, p1y, r1, p2x, p2y, s2x, s2y):
    # FIXME: corners are too sensitive?
    if \
        p1x >= p2x - r1 and \
        p1y >= p2y - r1 and \
        p1x <= p2x + s2x + r1 and \
        p1y <= p2y + s2y + r1:
            return True
    else:
        return False

def cir_arc_col (p1, r1, p2, s2):
    # FIXME: this is just rect collision
    if \
        p1x >= p2x - s2x and \
        p1y >= p2y - s2y and \
        p1x <= p2x + s2x and \
        p1y <= p2y + s2y:
            return True
    else:
        return False

def init_game ():
    s.turt_lives = 3
    s.turt_mwater = s.turt_mwater_init
    s.turt_mwater_tick = 0.0

    init_room (0)

    _map.reset_maps ()

def game_on ():
    init_room (s.map_cur_n)
    sdl2.sdlmixer.Mix_PlayChannel (0, s.snds[s.SND_MAGIC1], 0)

def game_crunch ():
    s.turt_active = False
    sdl2.sdlmixer.Mix_PlayChannel (0, s.snds[s.SND_CRUNCH], 0)

    sdl2.SDL_ShowCursor (True)

    s.turt_mwater = 0

    s.turt_lives -= 1
    if not s.turt_lives:
        game_set_state (s.GAME_OVER)

def game_set_state (state):
    s.game_state_tick = 0.0
    s.game_state_len = s.game_states[state][0]
    s.game_state_img = s.imgs[s.game_states[state][1]]
    s.game_state_next = s.game_states[state][2]
    s.game_state_hlen = s.game_state_len / 2.0
    s.game_state = state

def get_item (item):
    if item._id == 'cheddar':
        s.turt_lives += 1

    if item._id == 'mwater':
        s.turt_mwater += 10

    sdl2.sdlmixer.Mix_PlayChannel (0, s.snds[s.SND_ITEM], 0)

def init_room (n):
    s.map_cur_n = n
    s.map_cur = _map.s.maps[n]

    s.bub_x = s.map_cur.begin_center[0]
    s.bub_y = s.map_cur.begin_center[1]
    s.bub_img_rect = sdl2.SDL_Rect (
        s.bub_x - s.bub_rad,
        s.bub_y - s.bub_rad)

    s.bub_pos_last = [(s.bub_x, s.bub_y)] * s.bub_pos_last_n

    # turtle tracks bubble
    s.turt_being.set_pos (s.bub_x, s.bub_y)

    s.turt_being.reset ()
    s.turt_active = True

    sdl2.SDL_ShowCursor (False)
    # FIXME: sdl2.SDL_FlushEvents ?
    sdl2.SDL_WarpMouseInWindow (s.window, s.bub_x, s.bub_y)

def win_room ():
    if s.map_cur_n + 1 < _map.s.maps_n:
        init_room (s.map_cur_n + 1)
        game_set_state (s.GAME_GO)
    else:
        game_set_state (s.GAME_OVER)

if __name__ == '__main__':
    sys.exit(main ())

