#include "draw.hpp"

uint32_t *draw_p;
int32_t draw_w, draw_h, draw_ps;
int32_t draw_hw, draw_hh;
uint8_t alpha_tbl [256][256];

void draw_init (uint32_t *p, int32_t w, int32_t h) {
    draw_p = p;
    draw_w = w;
    draw_h = h;

    draw_hw = w / 2;
    draw_hh = h / 2;
    draw_ps = w * h;

    for (auto a = 0; a < 256; a ++)
        for (auto b = 0; b < 256; b ++)
            alpha_tbl [a][b] = ((uint8_t)((a * b) / 256));

    srand (time (nullptr));
}

void draw_clear (uint32_t c) {
    auto _p = draw_p;
    for (auto p_c = 0; p_c < draw_ps; p_c ++)
        *_p++ = c;
}

void draw_point (int32_t x, int32_t y, uint32_t c) {
    if ((x < 0) || (y < 0) || (x >= draw_w) || (y >= draw_h))
        return;

    draw_p [y * draw_w + x] = c;
}

void draw_effect (uint32_t w, uint32_t d1, uint32_t d2) {
    uint32_t tmp_u32, tmp2_u32;

    auto _p_b = (uint8_t *)draw_p;

    // static: d1 = chance, d2 = brigtness range
    if (w == 0) {
        for (auto pixel_c = 0; pixel_c < draw_ps; pixel_c ++) {
            tmp2_u32 = rand ();
            if (! (tmp2_u32 % d1)) {
                tmp2_u32 = rand ();
                tmp_u32 = _p_b [0] + ((tmp2_u32 & 255) % d2);
                if (tmp_u32 < 256)
                    _p_b [0] = tmp_u32;
                else
                    _p_b [0] = 255;

                tmp_u32 = _p_b [1] + (((tmp2_u32 >> 8) & 255) % d2);
                if (tmp_u32 < 256)
                    _p_b [1] = tmp_u32;
                else
                    _p_b [1] = 255;

                tmp_u32 = _p_b [2] + (((tmp2_u32 >> 16) & 255) % d2);
                if (tmp_u32 < 256)
                    _p_b [2] = tmp_u32;
                else
                    _p_b [2] = 255;
            }
            _p_b += 4;
        }
    }
    // ghosting: d1 = offset, d2 = depth
    else if (w == 1) {
        for (auto line_c = 0; line_c < draw_h; line_c ++) {
            for (auto pixel_c = 0; pixel_c < draw_w - d1; pixel_c ++) {
                tmp_u32 = _p_b [0] + _p_b [d1 * 4] / d2;
                if (tmp_u32 < 256)
                    _p_b [0] = tmp_u32;
                else
                    _p_b [0] = 255;

                tmp_u32 = _p_b [1] + _p_b [d1 * 4 + 1] / d2;
                if (tmp_u32 < 256)
                    _p_b [1] = tmp_u32;
                else
                    _p_b [1] = 255;

                tmp_u32 = _p_b [2] + _p_b [d1 * 4 + 2] / d2;
                if (tmp_u32 < 256)
                    _p_b [2] = tmp_u32;
                else
                    _p_b [2] = 255;

                _p_b += 4;
            }
            _p_b += d1 * 4;
        }
    }
    // scanlines: d1 = freq, d2 = pix depth
    else if (w == 2) {
        for (auto line_c = 0; line_c < draw_h; line_c ++) {
            if (! (line_c % d1)) {
                for (auto pixel_c = 0; pixel_c < draw_w; pixel_c ++) {
                    if (_p_b [0] >= d2)
                        _p_b [0] -= d2;
                    else
                        _p_b [0] = 0;

                    if (_p_b [1] >= d2)
                        _p_b [1] -= d2;
                    else
                        _p_b [1] = 0;

                    if (_p_b [2] >= d2)
                        _p_b [2] -= d2;
                    else
                        _p_b [2] = 0;
                        
                    _p_b += 4;
                }
            }
            else {
                _p_b += draw_w * 4;
            }
        }
    }
}

void draw_line (int32_t x1, int32_t y1, int32_t x2, int32_t y2, uint32_t c) {
    if ((x1 < 0) || (y1 < 0) || (x2 < 0) || (y2 < 0) || 
            (x1 >= draw_w) || (y1 >= draw_h) || 
            (x2 >= draw_w) || (y2 >= draw_h))
        return;

    int32_t dx = x2 - x1;
    int32_t dy = y2 - y1;
    if ((! dx) && (! dy))
        return;

    float fdx = (float)dx;
    float fdy = (float)dy;

    float fdxm = fabs(fdx);
    float fdym = fabs(fdy);

    float t_step = 1.0 / (1.00001 * (fdxm > fdym ? fdxm : fdym));

    for (float t = 0.0; t <= 1.0f; t += t_step) {
        uint16_t x = (uint16_t)(fdx * t + (float)x1);
        uint16_t y = (uint16_t)(fdy * t + (float)y1);
        if ((x < draw_w) && (y < draw_h))
            draw_p [y * draw_w + x] = c;
    }
}

void draw_rect (int32_t x, int32_t y, int32_t w, int32_t h, uint32_t c) {
    if ((x < 0) || (y < 0) || (x >= draw_w) || (y >= draw_h) || !w || !h)
        return;

    if (w < 0) {
        x = x + w;
        w = -w;
    }
    if ((x + w) > draw_w)
        w = (x + w) - draw_w;

    if (h < 0) {
        y = y + h;
        h = -h;
    }
    if ((y + h) > draw_h)
        h = (y + h) - draw_h;

    auto dst_line_d = draw_w - w;
    auto _dst_p = draw_p + (y * draw_w) + x;

    for (auto y_c = 0; y_c < h; y_c ++) {
        for (auto x_c = 0; x_c < w; x_c ++)
            *_dst_p++ = c;
        _dst_p += dst_line_d;
    }
}

void draw_get_rect (uint32_t *_dst_p, int32_t x, int32_t y,
        int32_t w, int32_t h) {
    auto dst_line_d = draw_w - w;
    auto _src_p = draw_p + (y * draw_w) + x;

    for (auto y_c = 0; y_c < h; y_c ++) {
        for (auto x_c = 0; x_c < w; x_c ++) {
            *_dst_p = *_src_p;
            _dst_p ++;
            _src_p ++;
        }
        _src_p += dst_line_d;
    }
}

void draw_put_rect (uint32_t *_src_p, uint32_t do_alpha,
        int32_t x, int32_t y, int32_t w, int32_t h) {
    auto dst_line_d = draw_w - w;
    auto _dst_p = draw_p + (y * draw_w) + x;

    if (! do_alpha) {
        for (auto y_c = 0; y_c < h; y_c ++) {
            for (auto x_c = 0; x_c < w; x_c ++) {
                *_dst_p ++ = *_src_p;
                _src_p ++;
            }
            _dst_p += dst_line_d;
        }
    }
    else {
        auto _dst_p_b = (uint8_t *)_dst_p;
        auto _src_p_b = (uint8_t *)_src_p;
        dst_line_d *= 4;
        for (auto y_c = 0; y_c < h; y_c ++) {
            for (auto x_c = 0; x_c < w; x_c ++) {
                auto a = _src_p_b [3];

                *_dst_p_b = alpha_tbl [255 - a][*_dst_p_b] +
                    alpha_tbl [a][*_src_p_b];
                _src_p_b ++;
                _dst_p_b ++;

                *_dst_p_b = alpha_tbl [255 - a][*_dst_p_b] +
                    alpha_tbl [a][*_src_p_b];
                _src_p_b ++;
                _dst_p_b ++;

                *_dst_p_b = alpha_tbl [255 - a][*_dst_p_b] +
                    alpha_tbl [a][*_src_p_b];
                _src_p_b ++;
                _dst_p_b ++;

                _src_p_b ++;
                _dst_p_b ++;
            }
            _dst_p_b += dst_line_d;
        }
    }
}

void draw_put_src_rect (uint32_t *_src_p, uint32_t do_alpha,
        int32_t x, int32_t y, int32_t w, int32_t h,
        int32_t src_x, int32_t src_y, int32_t src_w) {
    auto dst_line_d = draw_w - w;
    auto _dst_p = draw_p + (y * draw_w) + x;
    
    _src_p += src_y * src_w + src_x;
    auto src_line_d = src_w - w;

    if (! do_alpha) {
        for (auto y_c = 0; y_c < h; y_c ++) {
            for (auto x_c = 0; x_c < w; x_c ++) {
                *_dst_p ++ = *_src_p;
                _src_p ++;
            }
            _dst_p += dst_line_d;
            _src_p += src_line_d;
        }
    }
    else {
        auto _dst_p_b = (uint8_t *)_dst_p;
        dst_line_d *= 4;
        auto _src_p_b = (uint8_t *)_src_p;
        src_line_d *= 4;
        for (auto y_c = 0; y_c < h; y_c ++) {
            for (auto x_c = 0; x_c < w; x_c ++) {
                auto a = _src_p_b [3];

                *_dst_p_b = alpha_tbl [255 - a][*_dst_p_b] +
                    alpha_tbl [a][*_src_p_b];
                _src_p_b ++;
                _dst_p_b ++;

                *_dst_p_b = alpha_tbl [255 - a][*_dst_p_b] +
                    alpha_tbl [a][*_src_p_b];
                _src_p_b ++;
                _dst_p_b ++;

                *_dst_p_b = alpha_tbl [255 - a][*_dst_p_b] +
                    alpha_tbl [a][*_src_p_b];
                _src_p_b ++;
                _dst_p_b ++;

                _src_p_b ++;
                _dst_p_b ++;
            }
            _dst_p_b += dst_line_d;
            _src_p_b += src_line_d;
        }
    }
}

