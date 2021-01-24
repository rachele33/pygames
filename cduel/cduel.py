#!/usr/bin/env python3
''' Card Duel '''
''' © 2014 Richard A. Benson <richardbenson91477@protonmail.com> '''
import sys, math, os, random, ctypes
import sdl2, sdl2.sdlmixer, sdl2.sdlimage
import deck

class s:
    ''' global state '''
    win_s = 'Card Duel'
    win_w, win_h = (640, 640)
    win_bgcolor = 0xff30001a
    # win_rect_ref

    run_fps = 25
    # run_t_begin, run_t_end
    # run_frame_t, run_frame_t_ms

    score_init = 30

    dealer_t = 0.227
    switch_t = 0.5
    score_pre_t = 0.25
    score_t = 1.0
    reuse_t = 1.0

    # window, windowsurface

    # deck
    # deck_pile, deck_pile_n
    # disc_pile, disc_pile_n

    STATE_PAUSE, STATE_DEAL, STATE_PICK_A, STATE_PICK_B, STATE_REVEAL,\
            STATE_SCORE_A, STATE_SCORE_B, STATE_DISCARD_PLAYS,\
            STATE_DISCARD_HANDS, STATE_FINISH,\
            STATE_BOG_PRE, STATE_BOG_SCORE_B, STATE_BOG_SCORE_A =\
        range(13)

    # state
    # state_t, state_len, state_next

    # NOTE: these need to be zero and one
    PLAYER_A, PLAYER_B = (0, 1)

    # player_1
    # scores, hands, hands_n, plays, plays_n

    SCORE_PRE_ATTACK, SCORE_PRE_HEAL, SCORE_PRE_SHIELD =\
        range(3)
    # scores_pre

    LAYOUT_N = 10
    LAY_DECK, LAY_DISC, LAY_HAND_A, LAY_HAND_B, LAY_PLAY_A, LAY_PLAY_B,\
            LAY_COIN_A, LAY_COIN_B, LAY_SCORE_A, LAY_SCORE_B =\
        range(LAYOUT_N)
    layout = [[] for c in range(LAYOUT_N)]

    IMG_COIN = 0
    misc_imgs_s = ['coin']
    # misc_imgs, misc_img_sizes

    # font_g_imgs, font_y_imgs, font_r_imgs
    # font_w, font_h, font_hw, font_hh
    # font_rect, font_rect_n
    # font_surf_A, font_surf_B

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
        if done_:
            break
        tick ()
        paint ()

    deinit ()
    return 0

def init ():
    res = sdl2.SDL_Init (sdl2.SDL_INIT_VIDEO | sdl2.SDL_INIT_AUDIO)
    if res:
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

    s.misc_imgs = [sdl2.sdlimage.IMG_Load (
        bytes (os.path.join ('data', 'misc', fn + '.png'), 'utf-8'))
        for fn in s.misc_imgs_s]
    s.misc_img_sizes = [(i.contents.h, i.contents.w) for i in s.misc_imgs]

    s.font_g_imgs = [sdl2.sdlimage.IMG_Load (
        bytes (os.path.join ('data', 'font', 'font_g-' + str (fc) + '.png'),
        'utf-8'))
        for fc in range(10)]
    s.font_y_imgs = [sdl2.sdlimage.IMG_Load (
        bytes (os.path.join ('data', 'font', 'font_y-' + str (fc) + '.png'),
        'utf-8'))
        for fc in range(10)]
    s.font_r_imgs = [sdl2.sdlimage.IMG_Load (
        bytes (os.path.join ('data', 'font', 'font_r-' + str (fc) + '.png'),
        'utf-8'))
        for fc in range(10)]
    s.font_w = s.font_g_imgs[0].contents.w
    s.font_h = s.font_g_imgs[0].contents.h
    s.font_hw, s.font_hh = (s.font_w // 2, s.font_h // 2)
    s.font_rect = sdl2.SDL_Rect (0, 0, s.font_w * 3, s.font_h)
    s.font_rect_n = (
        sdl2.SDL_Rect (0, 0),
        sdl2.SDL_Rect (s.font_w, 0),
        sdl2.SDL_Rect (s.font_w * 2, 0))

    s.font_surf_A = sdl2.SDL_CreateRGBSurface (0, s.font_rect.w, s.font_rect.h,
        32, 0, 0, 0, 0)
    s.font_surf_B = sdl2.SDL_CreateRGBSurface (0, s.font_rect.w, s.font_rect.h,
        32, 0, 0, 0, 0)

    s.state = s.STATE_PAUSE
    s.state_next = s.STATE_PAUSE
    s.state_t = 0.0
    s.state_len = 0.0

    s.deck = deck.Deck ()

    init_layout ()
    init_game ()

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

    s.deck.tick (s.run_frame_t)

    if s.state_len > 0.0:
        s.state_t += s.run_frame_t
        if s.state_t >= s.state_len:
            s.state_t = 0.0
            set_state ()

def paint ():
    sdl2.SDL_FillRect (s.windowsurface, s.win_rect_ref, s.win_bgcolor)

    sdl2.SDL_BlitSurface (s.misc_imgs[s.IMG_COIN], None, s.windowsurface,
        s.layout[s.LAY_COIN_A + s.player_1])

    s.deck.paint (s.windowsurface)

    sdl2.SDL_BlitSurface (s.font_surf_A, None, s.windowsurface,
        s.layout[s.LAY_SCORE_A])
    sdl2.SDL_BlitSurface (s.font_surf_B, None, s.windowsurface,
        s.layout[s.LAY_SCORE_B])

    sdl2.SDL_UpdateWindowSurface (s.window)

def on_click (mx, my):
    if s.deck_pile_n:
        i = s.deck.p_in_r (mx, my, pile = s.deck_pile)
        if i != None:
            init_game ()
            return

    if s.state == s.STATE_PICK_A:
        i = s.deck.p_in_r (mx, my, pile = s.hands[s.PLAYER_A])
        if i != None:
            set_state (card = s.hands[s.PLAYER_A][i])
            return

        if s.player_1 == s.PLAYER_A and\
            p_in_r (mx, my, s.layout[s.LAY_COIN_A]):
                bog_pre ()

def init_layout ():
    win_hw, win_hh = (s.win_w // 2, s.win_h // 2)
    win_sw, win_sh = (s.win_w // 6, s.win_h // 6)
    win_ew, win_eh = (s.win_w // 8, s.win_h // 8)

    y = win_hh - s.deck.hh
    x1 = win_ew - s.deck.hw
    s.layout[s.LAY_DECK] = (x1, y)

    x2 = s.win_w - win_ew - s.deck.hw
    s.layout[s.LAY_DISC] = (x2, y)

    xsp = s.deck.hw // 4
    xw = s.deck.w * 5 + xsp * 4

    x1 = win_hw - xw // 2
    x2 = x1 + xsp + s.deck.w
    x3 = x2 + xsp + s.deck.w
    x4 = x3 + xsp + s.deck.w
    x5 = x4 + xsp + s.deck.w

    y = s.win_h - win_sh - s.deck.hh
    s.layout[s.LAY_HAND_A] = ((x1, y), (x2, y), (x3, y), (x4, y), (x5, y))

    y = win_sh - s.deck.hh
    s.layout[s.LAY_HAND_B] = ((x1, y), (x2, y), (x3, y), (x4, y), (x5, y))

    ysp = s.deck.hh // 3

    y1 = win_hh - s.deck.hh
    y2 = y1 + ysp
    y3 = y2 + ysp
    y4 = y3 + ysp
    y5 = y4 + ysp

    x = win_hw - (s.deck.hw * 3)
    s.layout[s.LAY_PLAY_A] = ((x, y1), (x, y2), (x, y3), (x, y4), (x, y5))

    y1 = win_hh - s.deck.hh
    y2 = y1 - ysp
    y3 = y2 - ysp
    y4 = y3 - ysp
    y5 = y4 - ysp

    x = win_hw + s.deck.hw
    s.layout[s.LAY_PLAY_B] = ((x, y1), (x, y2), (x, y3), (x, y4), (x, y5))

    coin_w, coin_h = (s.misc_img_sizes[s.IMG_COIN][0],
        s.misc_img_sizes[s.IMG_COIN][1])
    coin_hw, coin_hh = (coin_w // 2, coin_h // 2)
    x = win_hw - coin_hw
    y1 = win_hh + win_sh - coin_hh
    y2 = win_hh - win_sh - coin_hh
    s.layout[s.LAY_COIN_A] = sdl2.SDL_Rect (x, y1, coin_w, coin_h)
    s.layout[s.LAY_COIN_B] = sdl2.SDL_Rect (x, y2, coin_w, coin_h)

    x = win_hw - s.font_hw * 3
    y1 = s.win_h - s.font_h - s.font_hh // 2
    y2 = s.font_hh // 2
    s.layout[s.LAY_SCORE_A] = sdl2.SDL_Rect (x, y1)
    s.layout[s.LAY_SCORE_B] = sdl2.SDL_Rect (x, y2)

def p_in_r (x, y, r):
    if x >= r.x and y >= r.y and x < r.x + r.w and y < r.y + r.h:
        return True
    return False

def init_game ():
    for card in s.deck.cards:
        card.set_pos (s.layout[s.LAY_DECK][0], s.layout[s.LAY_DECK][1])
        card.vis = False
        card.back = True
        card.moving = False

    s.deck_pile = list (s.deck.cards)
    s.deck_pile_n = deck.NCARDS
    s.deck.shuffle (s.deck_pile)

    s.disc_pile = []
    s.disc_pile_n = 0

    s.player_1 = s.PLAYER_A

    s.scores = [s.score_init, s.score_init]
    s.hands = ([[], [], [], [], []], [[], [], [], [], []])
    s.hands_n = [0, 0]
    s.plays = ([], [])
    s.plays_n = [0, 0]

    render_score ()

    set_state (s.STATE_DEAL)

def reuse_disc ():
    if s.deck_pile_n == 0:
        deck_used = True
    else:
        deck_used = False

    s.deck_pile += s.disc_pile
    s.deck_pile_n += s.disc_pile_n

    s.disc_pile = []
    s.disc_pile_n = 0

    for i in range (s.deck_pile_n - 1):
        card = s.deck_pile[i]
        card.set_pos (s.layout[s.LAY_DECK][0], s.layout[s.LAY_DECK][1])
        card.vis = False

    if not deck_used:
        s.deck_pile[0].vis = True

    card = s.deck_pile[s.deck_pile_n - 1]
    s.deck.move_to (card, s.layout[s.LAY_DECK], s.reuse_t)

    # TODO: play shuffle sound
    s.deck.shuffle (s.deck_pile)

def deal ():
    if s.deck_pile_n == 0:
        reuse_disc ()
        return False

    card = s.deck_pile.pop ()
    s.deck_pile_n -= 1

    for player in (s.PLAYER_B, s.PLAYER_A):
        if s.hands_n[player] < 5:
            i = s.hands[player].index ([])
            s.hands[player][i] = card
            s.hands_n[player] += 1
            if player == s.PLAYER_A:
                card.back = False
            p = s.layout[s.LAY_HAND_A + player][i]
            break

    s.deck.move_to (card, p, s.dealer_t)

    # make (only) top deck_pile card visible
    n = s.deck_pile_n
    if n > 0:
        s.deck_pile[n - 1].vis = True
    if n > 1:
        s.deck_pile[n - 2].vis = False

    return True

def discard (card):
    card.back = True
    s.deck.move_to (card, s.layout[s.LAY_DISC], s.dealer_t)

    n = s.disc_pile_n
    if n > 0:
        s.disc_pile[n - 1].vis = True
    if n > 1:
        s.disc_pile[n - 2].vis = False

    s.disc_pile.append (card)
    s.disc_pile_n += 1

def discard_plays ():
    if s.plays_n[s.PLAYER_B] > 0:
        player = s.PLAYER_B
    elif s.plays_n[s.PLAYER_A] > 0:
        player = s.PLAYER_A
    else:
        return False

    card = s.plays[player].pop ()
    s.plays_n[player] -= 1

    discard (card)
    return True

def discard_hands ():
    if s.hands_n[s.PLAYER_B] > 0:
        player = s.PLAYER_B
    elif s.hands_n[s.PLAYER_A] > 0:
        player = s.PLAYER_A
    else:
        return False

    for card in s.hands[player]:
        if card: break

    i = s.hands[player].index (card)
    s.hands[player][i] = []
    s.hands_n[player] -= 1

    discard (card)
    return True

def pick (player, card = []):
    if player == s.PLAYER_A:
        i = s.hands[player].index (card)
        s.hands[player][i] = []
        s.hands_n[player] -= 1
    else:
        # TODO: more intelligence
        c = random.randrange (s.hands_n[player])
        c2 = 0
        for card in s.hands[player]:
            if card != []:
                if c2 == c: break
                c2 += 1
        i = s.hands[player].index (card)
        s.hands[player][i] = []
        s.hands_n[player] -= 1

    s.plays[player].append (card)
    s.plays_n[player] += 1

    s.deck.move_to (card,
        s.layout[s.LAY_PLAY_A + player][s.plays_n[player] - 1],
        s.dealer_t)

    s.state = s.STATE_PAUSE
    s.state_len = s.dealer_t

    card.back = False

    if card.suit == deck.ids.SUIT_CLUBS:
        if s.plays_n[player] == 5:
            if s.player_1 == player:
                card.back = True
        else:
            s.state_next = s.STATE_PICK_A + player
            return True

    elif s.plays_n[player] > 1:
        if s.player_1 == player:
            card.back = True

    return False

def score_pre ():
    scores_pre = ([0, 0, 0], [0, 0, 0])

    for player in (s.PLAYER_A, s.PLAYER_B):
        if player == s.PLAYER_A:
            pile = s.plays[s.PLAYER_A]
        else:
            pile = s.plays[s.PLAYER_B]

        attack = 0
        heal = 0
        shield = 0

        card = pile[0]
        if card.suit == deck.ids.SUIT_SPADES:
            attack = card._id - deck.ids._2S + 2
        elif card.suit == deck.ids.SUIT_HEARTS:
            heal = card._id - deck.ids._2H + 2
        elif card.suit == deck.ids.SUIT_DIAMONDS:
            shield = card._id - deck.ids._2D + 2
        else:
            wand = 0
            for card in pile:
                if card.suit == deck.ids.SUIT_SPADES:
                    attack = card._id - deck.ids._2S + 2
                    attack += wand
                    break
                elif card.suit == deck.ids.SUIT_CLUBS:
                    wand += card._id - deck.ids._2C + 2
                elif card.suit == deck.ids.SUIT_HEARTS:
                    break
                elif card.suit == deck.ids.SUIT_DIAMONDS:
                    shield = card._id - deck.ids._2D + 2
                    shield += wand
                    break

        scores_pre[player][s.SCORE_PRE_ATTACK] = attack
        scores_pre[player][s.SCORE_PRE_HEAL] = heal
        scores_pre[player][s.SCORE_PRE_SHIELD] = shield

    return scores_pre

def score (player):
    if player == s.PLAYER_A:
        player_o = s.PLAYER_B
    else:
        player_o = s.PLAYER_A

    heal = s.scores_pre[player][s.SCORE_PRE_HEAL]
    attack = s.scores_pre[player][s.SCORE_PRE_ATTACK]
    shield = s.scores_pre[player_o][s.SCORE_PRE_SHIELD]

    if heal > 0:
        s.scores[player] += heal
        render_score (player, +1)
    elif attack > 0:
        attack -= shield
        if attack > 0:
            s.scores[player_o] -= attack
            if s.scores[player_o] <= 0:
                s.scores[player_o] = 0
                render_score (player_o, -1)
                return True
            else:
                render_score (player_o, -1)

    return False

def render_score (who = [], _dir = 0):
    if _dir == 0:
        players = (s.PLAYER_A, s.PLAYER_B)
    else:
        players = (who,)

    for player in players:
        if player == s.PLAYER_A:
            font_surf = s.font_surf_A
        else:
            font_surf = s.font_surf_B

        if _dir > 0:
            font_imgs = s.font_y_imgs
        elif _dir < 0:
            font_imgs = s.font_r_imgs
        else:
            font_imgs = s.font_g_imgs

        d1 = s.scores[player] // 100
        d2 = s.scores[player] % 100 // 10
        d3 = s.scores[player] % 100 % 10

        sdl2.SDL_FillRect (font_surf, ctypes.byref (s.font_rect), s.win_bgcolor)
        sdl2.SDL_BlitSurface (font_imgs[d1], None, font_surf, s.font_rect_n[0])
        sdl2.SDL_BlitSurface (font_imgs[d2], None, font_surf, s.font_rect_n[1])
        sdl2.SDL_BlitSurface (font_imgs[d3], None, font_surf, s.font_rect_n[2])

def bog_pre ():
    for card in s.hands[s.PLAYER_B]:
        card.back = False
    set_state (s.STATE_BOG_PRE)

def bog_score_b ():
    heal = 0

    for card in s.hands[s.PLAYER_B]:
        if not card:
            continue

        if card.suit == deck.ids.SUIT_HEARTS:
            heal += card._id - deck.ids._2H + 2

    if heal > 0:
        s.scores[s.PLAYER_B] += heal
        render_score (s.PLAYER_B, +1)

def bog_score_a ():
    attack = 0
    shield = 0

    for card in s.hands[s.PLAYER_B]:
        if not card:
            continue

        if card.suit == deck.ids.SUIT_DIAMONDS:
            shield += card._id - deck.ids._2D + 2

    for card in s.hands[s.PLAYER_A]:
        if not card:
            continue

        attack += card._id - deck.ids._2S + 2

    if attack > 0:
        attack -= shield
        if attack > 0:
            s.scores[s.PLAYER_B] -= attack
            if s.scores[s.PLAYER_B] <= 0:
                s.scores[s.PLAYER_B] = 0
                render_score (s.PLAYER_B, -1)
                return True
            else:
                render_score (s.PLAYER_B, -1)

    s.scores[s.PLAYER_A] = 0
    render_score (s.PLAYER_A, -1)
    return False

def bog_discard ():
    card_d = []
    for player in (s.PLAYER_A, s.PLAYER_B):
        for card in s.hands[player]:
            if not card:
                continue

            if card.suit == deck.ids.SUIT_CLUBS:
                card_d = card
                break
            elif player == s.PLAYER_A:
                if card.suit == deck.ids.SUIT_DIAMONDS:
                    card_d = card
                    break
                elif card.suit == deck.ids.SUIT_HEARTS:
                    card_d = card
                    break
            elif player == s.PLAYER_B:
                if card.suit == deck.ids.SUIT_SPADES:
                    card_d = card
                    break
        if card_d:
            i = s.hands[player].index (card)
            s.hands[player][i] = []
            s.hands_n[player] -= 1
            discard (card_d)
            return True
    return False

def set_state (state = False, card = []):
    if state:
        s.state = state
    else:
        s.state = s.state_next

    if s.state == s.STATE_DEAL:
        if s.hands_n[s.PLAYER_A] < 5 or s.hands_n[s.PLAYER_B] < 5:
            if deal ():
                s.state_len = s.dealer_t
                s.state_next = s.STATE_DEAL
            else:
                s.state_len = s.reuse_t
                s.state_next = s.STATE_DEAL
        else:
            if s.player_1 == s.PLAYER_A:
                s.state = s.state_next = s.STATE_PICK_A
                s.state_len = 0.0
            else:
                s.state_len = s.switch_t
                s.state_next = s.STATE_PICK_B
        return

    elif s.state == s.STATE_PICK_A:
        if not card:
            # auto-triggered by tick ()
            s.state_len = 0.0
            return

        if pick (s.PLAYER_A, card):
            return

        if s.player_1 == s.PLAYER_A:
            s.state_len += s.switch_t
            s.state_next = s.STATE_PICK_B
        else:
            s.state_len += s.switch_t
            s.state_next = s.STATE_REVEAL
        return

    elif s.state == s.STATE_PICK_B:
        if pick (s.PLAYER_B, []):
            return

        if s.player_1 == s.PLAYER_A:
            s.state_len += s.switch_t
            s.state_next = s.STATE_REVEAL
        else:
            s.state_len += s.switch_t
            s.state_next = s.STATE_PICK_A
        return

    elif s.state == s.STATE_REVEAL:
        for card in s.plays[s.PLAYER_A] + s.plays[s.PLAYER_B]:
            if card.back:
                card.back = False

        s.scores_pre = score_pre ()

        s.state_len = s.score_pre_t
        if s.player_1 == s.PLAYER_A:
            s.state_next = s.STATE_SCORE_A
        else:
            s.state_next = s.STATE_SCORE_B
        return

    elif s.state == s.STATE_SCORE_A:
        if score (s.PLAYER_A):
            s.state_next = s.STATE_DISCARD_HANDS
            s.state_len = s.score_t
            return

        s.state_len = s.score_t
        if s.player_1 == s.PLAYER_A:
            s.state_next = s.STATE_SCORE_B
        else:
            s.state_next = s.STATE_DISCARD_PLAYS
        return

    elif s.state == s.STATE_SCORE_B:
        if score (s.PLAYER_B):
            s.state_next = s.STATE_DISCARD_HANDS
            s.state_len = s.score_t
            return

        s.state_len = s.score_t
        if s.player_1 == s.PLAYER_A:
            s.state_next = s.STATE_DISCARD_PLAYS
        else:
            s.state_next = s.STATE_SCORE_A
        return

    elif s.state == s.STATE_DISCARD_PLAYS:
        if discard_plays ():
            s.state_len = s.dealer_t
            s.state_next = s.STATE_DISCARD_PLAYS
            return

        render_score ()

        if s.player_1 == s.PLAYER_A:
            s.player_1 = s.PLAYER_B
        else:
            s.player_1 = s.PLAYER_A

        s.state_len = s.switch_t
        s.state_next = s.STATE_DEAL
        return

    elif s.state == s.STATE_DISCARD_HANDS:
        if discard_plays ():
            s.state_len = s.dealer_t
            s.state_next = s.STATE_DISCARD_HANDS
            return

        elif discard_hands ():
            s.state_len = s.dealer_t
            s.state_next = s.STATE_DISCARD_HANDS
            return

        reuse_disc ()

        s.state = s.state_next = s.STATE_FINISH
        s.state_len = s.reuse_t
        return

    elif s.state == s.STATE_FINISH:
        s.state = s.state_next = s.STATE_PAUSE
        s.state_len = 0.0
        return

    elif s.state == s.STATE_BOG_PRE:
        if bog_discard ():
            s.state_len = s.dealer_t
            s.state_next = s.STATE_BOG_PRE
            return

        s.state = s.state_next = s.STATE_BOG_SCORE_B
        s.state_len = s.score_t
        return

    elif s.state == s.STATE_BOG_SCORE_B:
        bog_score_b ()

        s.state_len = s.score_t
        s.state_next = s.STATE_BOG_SCORE_A
        return

    elif s.state == s.STATE_BOG_SCORE_A:
        if bog_score_a ():
            pass

        s.state_next = s.STATE_DISCARD_HANDS
        s.state_len = s.score_t
        return

if __name__ == '__main__':
    sys.exit (main())

