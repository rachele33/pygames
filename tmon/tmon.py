#!/usr/bin/env python3
''' © 2014 Richard A. Benson <richardbenson91477@protonmail.com> '''
import sys, os, math, random, ctypes
import sdl2, sdl2.sdlmixer, sdl2.sdlimage

class s:
    ''' global state '''
    win_s = 'Treasure Monsters'
    win_w, win_h = (640, 672)
    # win_rect_ref

    run_fps = 25
    # run_t_end, run_t_begin
    # run_frame_t, run_frame_t_ms

    # window, windowsurface

    ID_LEADER_W, ID_MON_B_W, ID_MON_R_W, ID_MON_Y_W,\
            ID_LEADER_B, ID_MON_B_B, ID_MON_R_B, ID_MON_Y_B,\
            ID_GND_DES, ID_GND_GRASS, ID_GND_MTNS, ID_GND_WAT,\
            ID_TRES_C_B, ID_TRES_C_R, ID_TRES_C_Y,\
            ID_TRES_G_B, ID_TRES_G_R, ID_TRES_G_Y,\
            ID_SEL, ID_SEL_TURN, ID_STAT, ID_NONE =\
        range(22)

    maps_n = 2
    map_w, map_h = (640, 640)

    TILE_GND, TILE_BEING, TILE_ITEM, TILE_RECT, TILE_IDX =\
        range(5)
    tile_nx, tile_ny = (8, 8)
    tile_n = tile_nx * tile_ny
    tile_w, tile_h = (map_w // tile_nx, map_h // tile_ny)
    # tiles

    BEING_ID, BEING_TILE, BEING_ITEM, BEING_TILE_IDX=\
        range(4)
    # beings

    stat_w, stat_h = (win_w, win_h - map_h)
    # stat_sc1_rect, stat_sc2_rect
    # stat_sel1_rect, stat_sel2_rect
    # stat_reload_rect

    score_coin = 1
    score_gem = 2
    score_max = score_coin * 2 + score_gem * 2
    # scores

    # sel_tile, sel_turn_w

    imgs_s = (
        'leader_w', 'mon_b_w', 'mon_r_w', 'mon_y_w',
        'leader_b', 'mon_b_b', 'mon_r_b', 'mon_y_b',
        'tile_des', 'tile_grass', 'tile_mtns', 'tile_wat',
        'tres_c_b', 'tres_c_r', 'tres_c_y',
        'tres_g_b', 'tres_g_r', 'tres_g_y',
        'sel', 'sel_turn', 'stat')
    # imgs

    # font_imgs, font_w, font_h, font_hw, font_hh

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
            elif event.type == sdl2.SDL_MOUSEBUTTONDOWN:
                on_click (event.button.x, event.button.y, True)
            elif event.type == sdl2.SDL_MOUSEBUTTONUP:
                on_click (event.button.x, event.button.y, False)
        if done_:
            break;
        tick ()
        paint ()

    deinit ()
    return 0

def init ():
    if sdl2.SDL_Init (sdl2.SDL_INIT_VIDEO):
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

    s.imgs = [sdl2.sdlimage.IMG_Load (
        bytes (os.path.join ('data', fn + '.png'), 'utf-8'))
        for fn in s.imgs_s]

    s.font_imgs = [sdl2.sdlimage.IMG_Load (
        bytes (os.path.join ('data', 'font-' + str (c) + '.png'), 'utf-8'))
        for c in range(10)]

    s.font_w, s.font_h = (s.font_imgs[0].contents.w, s.font_imgs[0].contents.h)
    s.font_hw, s.font_hh = (s.font_w // 2, s.font_h // 2)

    s.stat_rect = sdl2.SDL_Rect (0, s.map_h)
    stat_hw, stat_hh = (s.stat_w // 2, s.stat_h // 2)
    y = s.map_h + stat_hh - s.font_hh
    s.stat_sc1_rect = sdl2.SDL_Rect (48, y)
    s.stat_sc2_rect = sdl2.SDL_Rect (stat_hw + 48, y)
    s.stat_sel1_rect = sdl2.SDL_Rect (16, y)
    s.stat_sel2_rect = sdl2.SDL_Rect (stat_hw + 16, y)
    s.stat_reload_rect = sdl2.SDL_Rect (s.map_w - 32, s.map_h)

    game_init ()

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

def paint ():
    map_paint ()
    stat_paint ()
    sdl2.SDL_UpdateWindowSurface (s.window)

def stat_paint ():
    sdl2.SDL_BlitSurface (s.imgs[s.ID_STAT], None,
        s.windowsurface,
        s.stat_rect)
    sdl2.SDL_BlitSurface (s.font_imgs[s.scores[0]], None,
        s.windowsurface,
        s.stat_sc1_rect)
    sdl2.SDL_BlitSurface (s.font_imgs[s.scores[1]], None,
        s.windowsurface,
        s.stat_sc2_rect)
    if s.sel_turn_w:
        sdl2.SDL_BlitSurface (s.imgs[s.ID_SEL_TURN], None,
            s.windowsurface,
            s.stat_sel1_rect)
    else:
        sdl2.SDL_BlitSurface (s.imgs[s.ID_SEL_TURN], None,
            s.windowsurface,
            s.stat_sel2_rect)

def map_paint ():
    for tile in s.tiles:
        rect = tile[s.TILE_RECT]
        sdl2.SDL_BlitSurface (s.imgs[tile[s.TILE_GND]], None,
            s.windowsurface, rect)
        if tile[s.TILE_BEING] != s.ID_NONE:
            sdl2.SDL_BlitSurface (s.imgs[tile[s.TILE_BEING]], None,
                s.windowsurface, rect)
        if tile[s.TILE_ITEM] != s.ID_NONE:
            sdl2.SDL_BlitSurface (s.imgs[tile[s.TILE_ITEM]], None,
                s.windowsurface, rect)
        if s.sel_tile:
            sdl2.SDL_BlitSurface (s.imgs[s.ID_SEL], None,
                s.windowsurface,
                s.sel_tile[s.TILE_RECT])

def on_click (mx, my, d):
    # reload ? 
    if (not d) and mx >= s.stat_reload_rect.x and my >= s.stat_reload_rect.y:
        game_init ()
        return

    # find tile clicked
    x = mx // s.tile_w
    y = my // s.tile_h
    # out of bounds?
    if x >= s.tile_nx or y >= s.tile_ny:
        return
    tile = s.tiles[x + s.tile_nx * y]

    # already selected tile?
    if tile == s.sel_tile:
        return

    tile_being_id = tile[s.TILE_BEING]

    # select tile?
    if not s.sel_tile:
        if d:
            if (s.sel_turn_w and\
                    tile_being_id >= s.ID_LEADER_W and\
                    tile_being_id <= s.ID_MON_Y_W) or\
                (not s.sel_turn_w and\
                    tile_being_id >= s.ID_LEADER_B and\
                    tile_being_id <= s.ID_MON_Y_B):
                s.sel_tile = tile
        return

    sel_prev = s.sel_tile
    s.sel_tile = []

    # not moving a being?
    being_id = sel_prev[s.TILE_BEING]
    if being_id == s.ID_NONE:
        return

    # moving too far?
    ox, oy = sel_prev[s.TILE_IDX]
    nx, ny = tile[s.TILE_IDX]
    if abs(ox - nx) > 1 or\
        abs(oy - ny) > 1:
        return

    # being being moved
    being = s.beings[being_id]
    being_item = being[s.BEING_ITEM]

    tile_item = tile[s.TILE_ITEM]

    # giving an item?
    if being_item != s.ID_NONE and\
            tile_being_id != s.ID_NONE and\
            tile_item == s.ID_NONE:

        if tile_being_id == s.ID_LEADER_W or\
                tile_being_id == s.ID_LEADER_B:
            if being_item >= s.ID_TRES_C_B and\
                    being_item <= s.ID_TRES_C_Y:
                points = s.score_coin
            elif being_item >= s.ID_TRES_G_B and\
                    being_item <= s.ID_TRES_G_Y:
                points = s.score_gem

            if tile_being_id == s.ID_LEADER_W:
                s.scores[0] += points
            else:
                s.scores[1] += points

            if s.scores[0] + s.scores[1] == s.score_max:
                # TODO: win
                pass
        else:
            tile_being = s.beings[tile_being_id]
            tile_being[s.BEING_ITEM] = being_item
            tile[s.TILE_ITEM] = being_item

        being[s.BEING_ITEM] = s.ID_NONE
        sel_prev[s.TILE_ITEM] = s.ID_NONE
        s.sel_turn_w = not s.sel_turn_w
        return
    # space occupied?
    elif tile_being_id != s.ID_NONE:
        return

    # dissalow invalid grounds
    gnd = tile[s.TILE_GND]
    if gnd != s.ID_GND_GRASS:
        if being_id == s.ID_LEADER_B or being_id == s.ID_LEADER_W:
            return
        if being_id == s.ID_MON_B_W or being_id == s.ID_MON_B_B:
            if gnd != s.ID_GND_WAT:
                return
        if being_id == s.ID_MON_R_W or being_id == s.ID_MON_R_B:
            if gnd != s.ID_GND_DES:
                return
        if being_id == s.ID_MON_Y_W or being_id == s.ID_MON_Y_B:
            if gnd != s.ID_GND_MTNS:
                return

    # onto an item?
    if tile_item != s.ID_NONE:
        # leader?
        if being_id == s.ID_LEADER_W or being_id == s.ID_LEADER_B:
            return
        # already have an item?
        if being_item != s.ID_NONE:
            return

    # clean prev tile
    sel_prev[s.TILE_BEING] = s.ID_NONE
    sel_prev[s.TILE_ITEM] = s.ID_NONE

    being_to (being_id, tile)
    s.sel_turn_w = not s.sel_turn_w

def game_init ():
    s.scores = [0, 0]
    s.sel_tile = []
    s.sel_turn_w = True
    map_init ()

def map_init ():
    s.tiles = []
    for n in range(s.tile_n):
        x = n % s.tile_nx
        y = n // s.tile_nx
        tile = [s.ID_GND_GRASS, s.ID_NONE, s.ID_NONE,
            sdl2.SDL_Rect (x * s.tile_w, y * s.tile_h),
            (x, y)]
        s.tiles.append (tile)

    s.beings = [[n, [], s.ID_NONE, [0, 0]] for n in range(8)]

    map_load (random.randint (1, s.maps_n))

def map_load (map_n):
    f = open (os.path.join ('data', 'map' + str(map_n) + '.map'))
    lines = f.readlines()
    f.close()

    tres_tiles = []

    n = 0
    for line in lines:
        for c in line.strip():
            if c == '.':
                n += 1
                continue

            tile = s.tiles[n]

            if c == 'd':
                tile[s.TILE_GND] = s.ID_GND_DES
                tres_tiles.append (tile)
            elif c == 'w':
                tile[s.TILE_GND] = s.ID_GND_WAT
                tres_tiles.append (tile)
            elif c == 'm':
                tile[s.TILE_GND] = s.ID_GND_MTNS
                tres_tiles.append (tile)

            elif c == 'L':
                being_to (s.ID_LEADER_W, tile)
            elif c == 'B':
                being_to (s.ID_MON_B_W, tile)
            elif c == 'R':
                being_to (s.ID_MON_R_W, tile)
            elif c == 'Y':
                being_to (s.ID_MON_Y_W, tile)
            elif c == 'l':
                being_to (s.ID_LEADER_B, tile)
            elif c == 'b':
                being_to (s.ID_MON_B_B, tile)
            elif c == 'r':
                being_to (s.ID_MON_R_B, tile)
            elif c == 'y':
                being_to (s.ID_MON_Y_B, tile)

            n += 1

    for tres in range(s.ID_TRES_C_B, s.ID_TRES_G_Y + 1):
        r = random.randrange (0, len (tres_tiles))
        tile = tres_tiles[r]
        tile[s.TILE_ITEM] = tres
        tres_tiles.remove (tile)

# NOTE being_to assumes move is valid
def being_to (_id, tile):
    being = s.beings[_id]
    tile_idx = tile[s.TILE_IDX]

    # set being's tile
    being[s.BEING_TILE_IDX] = tile_idx
    being[s.BEING_TILE] = tile

    if tile[s.TILE_ITEM] != s.ID_NONE:
        # set being's item
        being[s.BEING_ITEM] = tile[s.TILE_ITEM]
    else:
        # set tile's item
        tile[s.TILE_ITEM] = being[s.BEING_ITEM]

    # set tile's being
    tile[s.TILE_BEING] = _id

if __name__ == '__main__':
    sys.exit(main ())

