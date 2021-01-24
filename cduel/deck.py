''' © 2014 Richard A. Benson <richardbenson91477@protonmail.com> '''
import math, os, random
import sdl2.sdlimage

NCARDS=52

class ids:
    SUIT_SPADES, SUIT_CLUBS, SUIT_HEARTS, SUIT_DIAMONDS =\
        range (4)

    _2S, _3S, _4S, _5S, _6S, _7S, _8S, _9S, _10S, _JS, _QS, _KS, _AS,\
    _2C, _3C, _4C, _5C, _6C, _7C, _8C, _9C, _10C, _JC, _QC, _KC, _AC,\
    _2H, _3H, _4H, _5H, _6H, _7H, _8H, _9H, _10H, _JH, _QH, _KH, _AH,\
    _2D, _3D, _4D, _5D, _6D, _7D, _8D, _9D, _10D, _JD, _QD, _KD, _AD =\
        range (NCARDS)

def get_suit (_id):
    if _id >= ids._2S and _id <= ids._AS:
        return ids.SUIT_SPADES
    elif _id >= ids._2C and _id <= ids._AC:
        return ids.SUIT_CLUBS
    elif _id >= ids._2H and _id <= ids._AH:
        return ids.SUIT_HEARTS
    else:
        return ids.SUIT_DIAMONDS

class Card:
    # _id
    # suit
    # rect
    # vis, back
    # moving
    # mov_x, mov_y, mov_xo, mov_yo, mov_ray_x, mov_ray_y
    # mov_tlen, mov_t

    def __init__ (self, _id):
        self._id = _id
        self.suit = get_suit (_id)
        self.vis = True
        self.back = False
        self.moving = False
        self.rect = sdl2.rect.SDL_Rect (0, 0)

    def set_pos (self, x, y):
        self.rect.x = x
        self.rect.y = y

class Deck:
    cards = []
    # cards_mov, cards_mov_n
    # w, h, hw, hh
    imgs = []
    # imgs_s
    # img_back

    def __init__ (self, imgs_s = 'default'):
        self.imgs_s = imgs_s
        self.load_imgs ()

        self.cards = [Card(n) for n in range (NCARDS)]
        self.cards_mov = []
        self.cards_mov_n = 0

    def shuffle (self, pile = []):
        if not pile:
            pile = self.cards
        random.shuffle (pile)

    def get_card (self, _id, pile = []):
        if not pile:
            pile = self.cards
        c = 0
        for card in pile:
            if card and card._id == _id:
                return c
            c += 1
        return None

    def tick (self, t):
        if self.cards_mov_n != 0:
            cards_mov_del = []
            for card in self.cards_mov:
                card.mov_t += t

                card.set_pos (
                    int (card.mov_xo + card.mov_ray_x * card.mov_t),
                    int (card.mov_yo + card.mov_ray_y * card.mov_t))

                if card.mov_t >= card.mov_tlen:
                    card.set_pos (card.mov_x, card.mov_y)
                    card.moving = False
                    cards_mov_del.append (card)

            for card in cards_mov_del:
                self.cards_mov.remove (card)
                self.cards_mov_n -= 1

    def paint (self, windowsurface):
        if not self.imgs:
            return

        for card in self.cards:
            if not card.vis:
                continue

            if card.back:
                sdl2.SDL_BlitSurface (self.img_back, None, windowsurface,
                    card.rect)
            else:
                sdl2.SDL_BlitSurface (self.imgs[card._id], None,
                    windowsurface, card.rect)

    def move_to (self, card, p, t, top = True, vis = True):
        card.moving = True
        card.mov_tlen = t
        card.mov_t = 0.0
        card.mov_x = p[0]
        card.mov_y = p[1]
        card.mov_xo = card.rect.x
        card.mov_yo = card.rect.y
        card.mov_ray_x = (card.mov_x - card.mov_xo) / float(t)
        card.mov_ray_y = (card.mov_y - card.mov_yo) / float(t)
        self.cards_mov.append (card)
        self.cards_mov_n += 1
        if top:
            self.cards.remove (card)
            self.cards.append (card)
        if vis:
            card.vis = True

    def p_in_r (self, x, y, pile = []):
        ''' returns index or None '''
        if not pile:
            pile = self.cards

        c = len (pile)
        while (c != 0):
            c -= 1
            card = pile[c]
            if not card:
                continue

            if \
                    x >= card.rect.x and x < card.rect.x + self.w and\
                    y >= card.rect.y and y < card.rect.y + self.h:
                return c
        return None

    def load_imgs (self):
        if self.imgs:
            del self.imgs

        self.imgs = [sdl2.sdlimage.IMG_Load (
            bytes (os.path.join ('data', 'decks', self.imgs_s + '-' + str(n)
            + '.png'), 'utf-8'))
            for n in range (NCARDS + 1)]
        self.w = self.imgs[0].contents.w
        self.h = self.imgs[0].contents.h
        self.hw = self.w // 2
        self.hh = self.h // 2

        self.img_back = self.imgs[NCARDS]

