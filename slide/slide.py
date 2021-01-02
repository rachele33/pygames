#!/usr/bin/env python3
''' © 2014 Richard A. Benson <richardbenson91477@gmail.com> '''

import sys, math, os, random, ctypes
import sdl2, sdl2.sdlmixer, sdl2.sdlimage

class s:
    ''' global state '''
    win_s = 'slide'
    win_w, win_h = (600, 600)
    # win_rect, win_rect_ref

    run_fps = 30
    # run_t_end, run_t_begin
    # run_frame_t, run_frame_t_ms

    # window, windowsurface
    # mouse_rect

    N_DIRS = 6
    DIR_LEFT, DIR_UP, DIR_RIGHT, DIR_DOWN, DIR_INVALID, DIR_BUTTON =\
        range(N_DIRS)

    STATE_ACTIVE, STATE_STOP, STATE_STOPPED, STATE_START, STATE_SCRAMBLE,\
            STATE_WIN =\
        range(6)

    # state, state_level, state_tick
    state_scram_speed = 30
    state_won_len = 30

    puzzle_w, puzzle_h = (500, 500)
    puzzle_border = 0.1
    # puzzle_x, puzzle_y
    # puzzle_dim
    # puzzle_surface

    # mouse_x, mouse_y

    IMG_BOARD, IMG_PUZZLE =\
        range(2)
    imgs_s = ['board', 'puzzle']
    # imgs

    power_x, power_y = (0, 0)
    # power_w, power_h
    power_imgs_n = 2
    # power_imgs
    # power_rect

    # arrow_dir
    # arrow_imgs, arrow_hw
    # arrow_rect

    # won_imgs
    won_imgs_n = 5
    # won_img_c
    # won_rect

    SND_WON, SND_BUZZ =\
        range(2)
    snds_s = ['won', 'buzz']

    slide_snds_n = 5
    # slide_snds

    # piece_n
    # piece_w, piece_h
    # piece_pos
    # piece_srcrects, piece_dstrects
    # grid_dstrects

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
                if event.button.button == 1:
                    on_click (event.button.x, event.button.y)
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

    sdl2.mouse.SDL_ShowCursor (False)

    random.seed ()

    s.win_rect = sdl2.SDL_Rect (0, 0, s.win_w, s.win_h)
    s.win_rect_ref = ctypes.byref (s.win_rect)

    s.imgs = [sdl2.sdlimage.IMG_Load (
        bytes (os.path.join ('data', fn + '.png'), 'utf-8'))
        for fn in s.imgs_s]

    s.arrow_imgs = [sdl2.sdlimage.IMG_Load (
        bytes (os.path.join ('data', 'arrow' + str(i) + '.png'), 'utf-8'))
        for i in range(s.N_DIRS)]
    s.arrow_hw = s.arrow_imgs[0].contents.w // 2
    s.arrow_rect = sdl2.SDL_Rect (0, 0)

    s.power_imgs = [sdl2.sdlimage.IMG_Load (
        bytes (os.path.join ('data', 'power' + str(i) + '.png'), 'utf-8'))
        for i in range(s.power_imgs_n)]
    s.power_w = s.power_imgs[0].contents.w
    s.power_h = s.power_imgs[0].contents.h
    s.power_rect = sdl2.SDL_Rect (s.power_x, s.power_y, s.power_w, s.power_h)

    s.won_imgs = [sdl2.sdlimage.IMG_Load (
        bytes (os.path.join ('data', 'won' + str(i) + '.png'), 'utf-8'))
        for i in range(s.won_imgs_n)]
    x = s.won_imgs[0].contents.w
    y = s.won_imgs[0].contents.h
    s.won_rect = sdl2.SDL_Rect (
        s.win_w // 2 - x // 2,
        s.win_h // 2 - y // 2)
    s.won_img_c = 0

    sdl2.sdlmixer.Mix_OpenAudio (
        sdl2.sdlmixer.MIX_DEFAULT_FREQUENCY,
        sdl2.sdlmixer.MIX_DEFAULT_FORMAT,
        sdl2.sdlmixer.MIX_DEFAULT_CHANNELS,
        4096)
    sdl2.sdlmixer.Mix_Init (sdl2.sdlmixer.MIX_INIT_OGG)

    s.snds = [sdl2.sdlmixer.Mix_LoadWAV (
        bytes (os.path.join ('data', fn + '.ogg'), 'utf-8'))
        for fn in s.snds_s]

    s.slide_snds = [sdl2.sdlmixer.Mix_LoadWAV (
        bytes (os.path.join ('data', 'sl' + str(i) + '.ogg'), 'utf-8'))
        for i in range(s.slide_snds_n)]

    s.state = s.STATE_STOPPED

    s.puzzle_x = (s.win_w - s.puzzle_w) // 2
    s.puzzle_y = (s.win_h - s.puzzle_h) // 2
    s.puzzle_surface = sdl2.SDL_CreateRGBSurface (0, s.win_w, s.win_h,
        32, 0, 0, 0, 0)
    set_puzzle_dim (2)

    s.mouse_x, s.mouse_y = (0, 0)
    set_arrow ()

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

    if s.state == s.STATE_STOPPED:
        pass

    elif s.state == s.STATE_START:
        rnd_slide ()
        s.state_tick = 0
        s.state_level = 0
        s.state = s.STATE_SCRAMBLE

    elif s.state == s.STATE_SCRAMBLE:
        s.state_tick += 1
        if not (s.state_tick % s.state_scram_speed):
            if s.state_tick // s.state_scram_speed is s.state_level + 1:
                s.state_tick = 0
                s.state = s.STATE_ACTIVE
                set_arrow ()
            else:
                rnd_slide ()

    elif s.state == s.STATE_STOP:
        set_puzzle_dim (2)
        s.state = s.STATE_STOPPED

    elif s.state == s.STATE_WIN:
        s.state_tick += 1
        if not (s.state_tick % s.state_won_len):
            s.state_tick = 0
            s.won_img_c += 1
            if s.won_img_c is s.won_imgs_n:
                s.won_img_c = 0
            s.state_level += 1
            if s.state_level is s.puzzle_dim:
                set_puzzle_dim (s.puzzle_dim + 1)
                s.state_level = 0
            rnd_slide ()
            s.state = s.STATE_SCRAMBLE

def paint ():
    sdl2.SDL_BlitSurface (s.puzzle_surface, None, s.windowsurface, None)

    if s.state == s.STATE_WIN:
        sdl2.SDL_BlitSurface (s.won_imgs[s.won_img_c], None, s.windowsurface,
            s.won_rect)

    if s.state == s.STATE_STOPPED:
        sdl2.SDL_BlitSurface (s.power_imgs[1], None, s.windowsurface,
            s.power_rect)
    else:
        sdl2.SDL_BlitSurface (s.power_imgs[0], None, s.windowsurface,
            s.power_rect)

    sdl2.SDL_BlitSurface (s.arrow_imgs[s.arrow_dir], None, s.windowsurface,
        s.arrow_rect)

    sdl2.SDL_UpdateWindowSurface (s.window)

def paint_puzzle ():
    for i in range(s.piece_n):
        sdl2.SDL_BlitSurface (s.imgs[s.IMG_PUZZLE], s.piece_srcrects[i],
            s.puzzle_surface, s.piece_dstrects[i])

    grid_color = 0xffa0a0a0
    for i in range((s.puzzle_dim - 1) * 2):
       sdl2.SDL_FillRect (s.puzzle_surface, s.grid_dstrects[i], grid_color)

    sdl2.SDL_BlitSurface (s.imgs[s.IMG_BOARD], None, s.puzzle_surface, None)

def on_click (mx, my):
    s.mouse_x = mx
    s.mouse_y = my

    if in_box (mx, my, s.power_x, s.power_y, s.power_w, s.power_h):
        if s.state == s.STATE_STOPPED:
            s.state = s.STATE_START
        else:
            s.state = s.STATE_STOP
        return

    if s.state != s.STATE_ACTIVE:
        sdl2.sdlmixer.Mix_PlayChannel (0, s.snds[s.SND_BUZZ], 0)
        return

    i, dr = mouse_i_dir ()
    if i < 0:
        sdl2.sdlmixer.Mix_PlayChannel (0, s.snds[s.SND_BUZZ], 0)
        return

    col, row = s.piece_pos[i]
    slide (col, row, dr)
    if is_win ():
        win ()

def on_move (mx, my):
    s.mouse_x = mx
    s.mouse_y = my

    set_arrow ()

def calc_piece_dstrects ():
    s.piece_dstrects = []
    for i in range(s.piece_n):
        s.piece_dstrects += [sdl2.SDL_Rect (
            s.puzzle_x + (s.piece_pos[i][0] * s.piece_w),
            s.puzzle_y + (s.piece_pos[i][1] * s.piece_h),
            s.piece_w,
            s.piece_h )]

def set_puzzle_dim (n):
    s.puzzle_dim = n
    s.piece_n = s.puzzle_dim ** 2
    s.piece_w = s.puzzle_w // s.puzzle_dim
    s.piece_h = s.puzzle_h // s.puzzle_dim
    s.piece_pos = []
    s.piece_srcrects = []
    for y in range(s.puzzle_dim):
        for x in range(s.puzzle_dim):
            s.piece_pos += [[x, y]]
            s.piece_srcrects += [sdl2.SDL_Rect (
                x * s.piece_w,
                y * s.piece_h,
                s.piece_w,
                s.piece_h)]

    grid_hw = 2
    s.grid_dstrects = []
    for i in range(1, s.puzzle_dim):
        s.grid_dstrects += [sdl2.SDL_Rect (
            s.puzzle_x + (i * s.piece_w) - grid_hw,
            s.puzzle_y,
            grid_hw * 2,
            s.puzzle_h )]
        s.grid_dstrects += [sdl2.SDL_Rect (
            s.puzzle_x,
            s.puzzle_y + (i * s.piece_h) - grid_hw,
            s.puzzle_w,
            grid_hw * 2)]

    calc_piece_dstrects ()
    paint_puzzle ()

def mouse_i_dir ():
    x = s.mouse_x - s.puzzle_x
    y = s.mouse_y - s.puzzle_y
    col = x // s.piece_w
    row = y // s.piece_h

    try:
        i = s.piece_pos.index ([col, row])
    except:
        return (-1, -1)

    if x < s.puzzle_w * s.puzzle_border:
        dr = s.DIR_LEFT
    elif y < s.puzzle_h * s.puzzle_border:
        dr = s.DIR_UP
    elif x > s.puzzle_w * (1.0 - s.puzzle_border):
        dr = s.DIR_RIGHT
    elif y > s.puzzle_h * (1.0 - s.puzzle_border):
        dr = s.DIR_DOWN
    else:
        return (-1, -1)

    return (i, dr)

def in_box (x, y, bx, by, bw, bh):
    if x >= bx and x < bx + bw and y >= by and y < by + bh:
        return True
    return False

def set_arrow ():
    s.arrow_rect.x = s.mouse_x - s.arrow_hw
    s.arrow_rect.y = s.mouse_y - s.arrow_hw

    if in_box (s.mouse_x, s.mouse_y, s.power_x, s.power_y,
            s.power_w, s.power_h):
        s.arrow_dir = s.DIR_BUTTON
        return

    if s.state == s.STATE_ACTIVE:
        i, s.arrow_dir = mouse_i_dir ()
        if i < 0:
            s.arrow_dir = s.DIR_INVALID

    elif s.state == s.STATE_STOPPED:
        s.arrow_dir = s.DIR_INVALID

    else:
        s.arrow_dir = s.DIR_BUTTON

def is_win ():
    i = j = 0
    for y in range(s.puzzle_dim):
        for x in range(s.puzzle_dim):
            if s.piece_pos[i] == [x, y]:
                j += 1
            i += 1

    if j == i:
        return True
    return False

def win ():
    sdl2.sdlmixer.Mix_PlayChannel (0, s.snds[s.SND_WON], 0)
    s.state = s.STATE_WIN
    set_arrow ()

def move_piece (col, row, d):
    if d == s.DIR_LEFT:
        for p in s.piece_pos:
            if p[1] != row:
                continue
            p[0] -= 1
            if p[0] < 0:
                p[0] = s.puzzle_dim - 1

    elif d == s.DIR_RIGHT:
        for p in s.piece_pos:
            if p[1] is not row:
                continue
            p[0] += 1
            if p[0] >= s.puzzle_dim:
                p[0] = 0

    elif d == s.DIR_UP:
        for p in s.piece_pos:
            if p[0] is not col:
                continue
            p[1] -= 1
            if p[1] < 0:
                p[1] = s.puzzle_dim - 1

    elif d == s.DIR_DOWN:
        for p in s.piece_pos:
            if p[0] is not col:
                continue
            p[1] += 1
            if p[1] >= s.puzzle_dim:
                p[1] = 0

def slide (col, row, d):
    sdl2.sdlmixer.Mix_PlayChannel (0,
        s.slide_snds[random.randrange (s.slide_snds_n)], 0)
    move_piece (col, row, d)
    calc_piece_dstrects ()
    paint_puzzle ()

def rnd_slide ():
    d = random.randrange (4);
    col, row = s.piece_pos[random.randrange (s.piece_n)]

    saved_pp = [list(pp) for pp in s.piece_pos]

    move_piece (col, row, d)
    if is_win ():
        if d == s.DIR_LEFT or d == s.DIR_RIGHT:
            row += 1
            if row >= s.puzzle_dim:
                row = 0
        else:
            col += 1
            if col >= s.puzzle_dim:
                col = 0

    s.piece_pos = [list(pp) for pp in saved_pp]

    slide (col, row, d)

if __name__ == '__main__':
    sys.exit (main ())

