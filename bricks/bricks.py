#!/usr/bin/env python3
import sys, time, io, random, math, os
import ctypes
import sdl2, sdl2.sdlmixer, sdl2.sdlimage

class s:
    win_s = 'bricks'
    win_w, win_h = (500, 500)
    # win_rect_ref
    bg_color = 0xff2a2a2a
    mouse_btns = [False] * 3
    run_fps = 30
    # run_t_end, run_t_begin, run_frame_t, run_frame_t_ms
    # window, windowsurface, event, event_ref
    # draw

    game_over = False
    # game_over_t
    game_over_max_t = 5.0
    # game_try
    game_init_try = 5
    # game_level

    # brick_rows
    # brick_cols
    brick_init_rows = 3
    brick_max_rows = 6
    brick_h = win_h // 24
    brick_begin_y = win_h // 12
    brick_row_colors = (0xffff0000, 0xffff8000, 0xffffff00, 0xff00ff00,\
        0xff0000ff, 0xffc000ff)
    bricks = []
    # brick_n

    paddle_w = win_w // 7
    paddle_hw = paddle_w // 2
    paddle_tw = paddle_w // 3
    paddle_ttw = paddle_w - paddle_tw
    paddle_h = win_h // 30
    paddle_x = paddle_prev_x = 0
    paddle_max_x = win_w - paddle_w - 1
    paddle_y = win_h - paddle_h * 3
    paddle_color = 0xfff0f0a0

    # ball_x, ball_y, ball_prev_x, ball_prev_y
    ball_h = 6
    ball_w = ball_h * 2
    ball_hw, ball_hh = (ball_w // 2, ball_h // 2)
    # ball_vx, ball_vy
    # ball_dir_x, ball_dir_y
    # ball_steep
    # ball_brick_level
    ball_max_x, ball_max_y = (win_w - ball_w - 1, win_h - ball_h - 1)
    # ball_col_paddle, ball_col_brick
    ball_init_x = win_w // 2 - ball_hw // 2
    # ball_init_y
    ball_on = False
    ball_color = 0xffa0a0ff
    ball_color_prev = 0xff303050

    img_font_w, img_font_h = (32, 32)
    img_font_n = 10
    img_font_try_x = win_w // 2 - img_font_w // 2
    # img_font_try_y
    img_font_p = []

    img_gover_w, img_gover_h = (360, 40)
    img_gover_x = win_w // 2 - img_gover_w // 2
    img_gover_y = win_h // 2 - img_gover_h
    # img_gover_p
    
    SND_BRICK, SND_PADDLE, SND_FAIL, SND_WALLS =\
        range(4)
    snds_fnames_s = ['brick', 'paddle', 'fail', 'walls']
    # slide_snds

def init (which):
    if which:
        random.seed ()
        
        f_in = io.open ('data/gameover.bgra', 'rb')
        if not f_in:
            return -1
        s.img_gover_p = f_in.read (s.img_gover_w * s.img_gover_h * 4)
        f_in.close ()

        f_in = io.open ('data/font.bgra', 'rb')
        if not f_in:
            return -1
        for i in range (s.img_font_n):
            s.img_font_p.append(f_in.read (s.img_font_w * s.img_font_h * 4))
        f_in.close ()

        s.draw = ctypes.cdll.LoadLibrary ('./draw.so')
        if not s.draw:
            return -1
    
        if sdl2.SDL_Init (sdl2.SDL_INIT_VIDEO | sdl2.SDL_INIT_AUDIO):
            return -2

        s.window = sdl2.SDL_CreateWindow (bytes(s.win_s, 'utf-8'),
            sdl2.SDL_WINDOWPOS_CENTERED, sdl2.SDL_WINDOWPOS_CENTERED,
            s.win_w, s.win_h, sdl2.SDL_WINDOW_SHOWN)
        if not s.window:
            return -3

        s.windowsurface = sdl2.SDL_GetWindowSurface (s.window)
        s.win_rect_ref = ctypes.byref (sdl2.SDL_Rect (0, 0, s.win_w, s.win_h))
        s.event = sdl2.SDL_Event ()
        s.event_ref = ctypes.byref (s.event)
        
        sdl2.sdlmixer.Mix_OpenAudio (
            sdl2.sdlmixer.MIX_DEFAULT_FREQUENCY,
            sdl2.sdlmixer.MIX_DEFAULT_FORMAT,
            sdl2.sdlmixer.MIX_DEFAULT_CHANNELS,
            4096)
        sdl2.sdlmixer.Mix_Init (sdl2.sdlmixer.MIX_INIT_OGG)

        s.snds = [sdl2.sdlmixer.Mix_LoadWAV (
            bytes (os.path.join ('data', fn + '.ogg'), 'utf-8'))
            for fn in s.snds_fnames_s]

        s.draw.draw_init (ctypes.c_void_p (s.windowsurface.contents.pixels),
            s.win_w, s.win_h)
        sdl2.SDL_UpdateWindowSurface (s.window)

        game_init ()

        s.run_frame_t = 1.0 / s.run_fps
        s.run_frame_t_ms = int(s.run_frame_t * 1000.0)
        s.run_t_begin = s.run_t_end = sdl2.SDL_GetTicks ()
    else:
        sdl2.SDL_DestroyWindow (s.window)
        sdl2.SDL_Quit ()

    return 0

def game_init ():
    s.game_level = 0
    s.game_over = False
    s.game_over_t = 0.0
    s.game_try = s.game_init_try
    game_level_init ()

def game_level_init ():
    s.brick_cols = 6 + (s.game_level * 2)
    rr = s.brick_max_rows - s.brick_init_rows + 1
    s.brick_rows = s.brick_init_rows + (s.game_level % rr)
    if s.brick_rows > s.brick_max_rows:
        s.brick_rows = s.brick_max_rows
    s.brick_end_y = s.brick_begin_y + (s.brick_h * s.brick_rows)
    fw = s.win_w / s.brick_cols
    s.bricks = []
    y = s.brick_begin_y
    for r in range(s.brick_rows):
        for c in range(s.brick_cols):
            x = int(fw * c)
            if c < s.brick_cols - 1:
                w = int(fw * (c + 1)) - x
            else:
                w = s.win_w - x
            s.bricks.append([True, x, y, w, s.brick_h, s.brick_row_colors[r]])
        y += s.brick_h
    s.brick_n = s.brick_rows * s.brick_cols

    s.ball_init_y = s.brick_end_y + s.brick_h - s.ball_hh
    ball_init ()

    s.img_font_try_y = s.ball_init_y + s.ball_h + s.img_font_h

def ball_init ():
    s.ball_on = False
    s.ball_x = s.ball_prev_x = s.ball_init_x
    s.ball_y = s.ball_prev_y = s.ball_init_y

    s.ball_col_brick = False
    s.ball_col_paddle = True

    s.ball_dir_x, s.ball_dir_y = (1, 1)
    s.ball_steep = False
    s.ball_brick_level = 0
    ball_calc_v ()

def ball_calc_v ():
    if s.ball_steep:
        s.ball_vy = s.ball_dir_y * (10 + s.ball_brick_level * 2)
        s.ball_vx = s.ball_dir_x * (8 + s.ball_brick_level * 2)
    else:
        s.ball_vy = s.ball_dir_y * (6 + s.ball_brick_level * 2)
        s.ball_vx = s.ball_dir_x * (12 + s.ball_brick_level * 2)

def tick ():
    while sdl2.SDL_PollEvent (s.event_ref) != 0:
        if s.event.type == sdl2.SDL_QUIT:
            return False

        elif s.event.type == sdl2.SDL_KEYDOWN:
            if s.event.key.keysym.sym == sdl2.keycode.SDLK_ESCAPE:
                return False

        elif s.event.type == sdl2.SDL_MOUSEBUTTONDOWN:
            on_click (s.event.button.button, s.event.button.x, s.event.button.y)
        
        elif s.event.type == sdl2.SDL_MOUSEBUTTONUP:
            on_declick (s.event.button.button,
                    s.event.button.x, s.event.button.y)

        elif s.event.type == sdl2.SDL_MOUSEMOTION:
            on_move (s.event.motion.x, s.event.motion.y)
    
    s.run_t_end = sdl2.SDL_GetTicks ()
    _t = s.run_t_begin - s.run_t_end + s.run_frame_t_ms
    if _t > 0:
        sdl2.SDL_Delay (_t)
    s.run_t_begin = sdl2.SDL_GetTicks ()

    if s.game_over:
        s.game_over_t += s.run_frame_t
        if s.game_over_t > s.game_over_max_t:
            game_init ()

    if s.ball_on:
        ball_tick ()
            
    paint ()
    return True

def ball_in_paddle ():
    if not s.ball_col_paddle:
        return False

    bx2 = s.ball_x + s.ball_w
    by2 = s.ball_y + s.ball_h
    px2 = s.paddle_x + s.paddle_w
    py2 = s.paddle_y + s.paddle_h

    if s.ball_x >= s.paddle_x and s.ball_x < px2 and\
        by2 >= s.paddle_y and by2 < py2:
        return True
    elif bx2 >= s.paddle_x and bx2 < px2 and\
        by2 >= s.paddle_y and by2 < py2:
        return True
    elif s.ball_x >= s.paddle_x and s.ball_x < px2 and\
        s.ball_y >= s.paddle_y and s.ball_y < py2:
        return True
    elif bx2 >= s.paddle_x and bx2 < px2 and\
        s.ball_y >= s.paddle_y and s.ball_y < py2:
        return True
    return False

def ball_tick ():
    s.ball_prev_x, s.ball_prev_y = (s.ball_x, s.ball_y)

    s.ball_x += s.ball_vx
    s.ball_y += s.ball_vy

    if s.ball_x < 0:
        s.ball_x = 0
        s.ball_dir_x = -s.ball_dir_x

        sdl2.sdlmixer.Mix_PlayChannel (-1, s.snds[s.SND_WALLS], 0)
        ball_calc_v ()

    elif s.ball_x > s.ball_max_x:
        s.ball_x = s.ball_max_x
        s.ball_dir_x = -s.ball_dir_x
        
        sdl2.sdlmixer.Mix_PlayChannel (-1, s.snds[s.SND_WALLS], 0)
        ball_calc_v ()

    if s.ball_y < 0:
        s.ball_y = 0
        s.ball_dir_y = -s.ball_dir_y

        s.ball_col_brick = True
        s.ball_col_paddle = True

        sdl2.sdlmixer.Mix_PlayChannel (-1, s.snds[s.SND_WALLS], 0)
        ball_calc_v ()
        return

    elif s.ball_y > s.ball_max_y:
        s.game_try -= 1
        if s.game_try == 0:
            s.game_over = True
        else:
            ball_init ()

        sdl2.sdlmixer.Mix_PlayChannel (-1, s.snds[s.SND_FAIL], 0)
        return

    if ball_in_paddle ():
        s.ball_dir_y = -s.ball_dir_y
        if s.ball_x + s.ball_hw < s.paddle_x + s.paddle_tw:
            if s.ball_dir_x > 0:
                s.ball_dir_x = -s.ball_dir_x
            else:
                s.ball_steep = False
        elif s.ball_x - s.ball_hw >= s.paddle_x + s.paddle_ttw:
            if s.ball_dir_x < 0:
                s.ball_dir_x = -s.ball_dir_x
            else:
                s.ball_steep = False
        else:
            s.ball_steep = True

        s.ball_col_brick = True
        s.ball_col_paddle = False

        sdl2.sdlmixer.Mix_PlayChannel (-1, s.snds[s.SND_PADDLE], 0)
        ball_calc_v ()
        return

    elif s.ball_col_brick and\
            s.ball_y >= s.brick_begin_y and s.ball_y < s.brick_end_y:
        r = (s.ball_y - s.brick_begin_y) // s.brick_h

        found = False
        for c in range(s.brick_cols):
            b = s.bricks[r * s.brick_cols + c]
            if s.ball_x >= b[1] and s.ball_x < b[1] + b[3]:
                if not b[0]:
                    return
                found = True
                break
        if not found:
            return

        b[0] = False

        b_level = s.brick_rows - 1 - r
        if b_level > s.ball_brick_level:
            s.ball_brick_level = b_level

        s.ball_dir_y = -s.ball_dir_y

        s.ball_col_brick = False
        s.ball_col_paddle = True
        sdl2.sdlmixer.Mix_PlayChannel (-1, s.snds[s.SND_BRICK], 0)
        
        s.brick_n -= 1
        if s.brick_n == 0:
            s.game_level += 1
            game_level_init ()
            return

        ball_calc_v ()

def paint ():
    s.draw.draw_clear (s.bg_color)

    for b in s.bricks:
        if b[0]:
            s.draw.draw_rect (b[1], b[2], b[3], b[4], b[5])

    s.draw.draw_rect (s.paddle_x, s.paddle_y, s.paddle_w, s.paddle_h,
        s.paddle_color)

    if s.game_over:
        s.draw.draw_put_rect (s.img_gover_p, True,
            s.img_gover_x, s.img_gover_y, s.img_gover_w, s.img_gover_h)
    else:
        s.draw.draw_rect (s.ball_x, s.ball_y, s.ball_w, s.ball_h,
            s.ball_color)
        if not s.ball_on:
            s.draw.draw_put_rect (s.img_font_p[s.game_try], True,
                s.img_font_try_x, s.img_font_try_y, s.img_font_w, s.img_font_h)
        else:
            s.draw.draw_rect (s.ball_prev_x, s.ball_prev_y,
                s.ball_w, s.ball_h, s.ball_color_prev)

    s.draw.draw_effect (1, 6, 7)
    s.draw.draw_effect (0, 20, 50)
    s.draw.draw_effect (2, 2, 100)
    sdl2.SDL_UpdateWindowSurface (s.window)

def on_click (mb, mx, my):
    s.mouse_btns[mb - 1] = True

def on_declick (mb, mx, my):
    s.mouse_btns[mb - 1] = False
    if mb == 1:
        if s.game_over:
            game_init ()
        elif not s.ball_on:
            s.ball_on = True

def on_move (mx, my):
    if mx == s.paddle_prev_x:
        return

    s.paddle_prev_x = s.paddle_x

    x = mx - s.paddle_hw
    if x < 0:
        x = 0
    elif x > s.paddle_max_x:
        x = s.paddle_max_x
    s.paddle_x = x

def main ():
    res = init (True)
    if res:
        return res

    while tick ():
        pass

    return init (False)

if __name__ == '__main__':
    sys.exit (main ())

