#ifndef NITRO_DRAW_INCLUDED

#include <cstdlib>
#include <cstdint>
#include <ctime>
#include <cmath>

extern "C" {
    extern uint32_t *draw_p;
    extern int32_t draw_w, draw_h, draw_ps;
    extern int32_t draw_hw, draw_hh;

    extern void draw_init (uint32_t *p, int32_t w, int32_t h);
    extern void draw_clear (uint32_t c);
    extern void draw_point (int32_t x, int32_t y, uint32_t c);
    extern void draw_effect (uint32_t w, uint32_t d1, uint32_t d2);
    extern void draw_line (int32_t x1, int32_t y1, int32_t x2, int32_t y2,
        uint32_t c);
    extern void draw_rect (int32_t x, int32_t y, int32_t w, int32_t h,
        uint32_t c);
    extern void draw_get_rect (uint32_t *_dst_p, int32_t x, int32_t y,
        int32_t w, int32_t h);
    extern void draw_put_rect (uint32_t *_src_p, uint32_t do_alpha,
        int32_t x, int32_t y, int32_t w, int32_t h);
    extern void draw_put_src_rect (uint32_t *_src_p, uint32_t do_alpha,
            int32_t x, int32_t y, int32_t w, int32_t h,
            int32_t src_x, int32_t src_y, int32_t src_w);
}

#define NITRO_DRAW_INCLUDED
#endif

