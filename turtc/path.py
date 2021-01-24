''' © 2014 Richard A. Benson <richardbenson91477@protonmail.com> '''
class Path:
    # curves, curves_n

    def __init__ (self):
        self.curves = []
        self.curves_n = 0

    def curve_eval (self, t):
        # NOTE: returns ints
        if not self.curves_n:
            return

        curve_c = int(t)
        t2 = t - float(curve_c)

        t2p3 = t2 ** 3
        t2p2 = t2 ** 2
        c1 = -1 * t2p3 + 3 * t2p2 + -3 * t2 + 1
        c2 = 3 * t2p3 + -6 * t2p2 + 3 * t2
        c3 = -3 * t2p3 + 3 * t2p2
        c4 = t2p3
        return (
            int(c1 * self.curves[curve_c][0][0] +\
                c2 * self.curves[curve_c][1][0] +\
                c3 * self.curves[curve_c][2][0] +\
                c4 * self.curves[curve_c][3][0]),
            int(c1 * self.curves[curve_c][0][1] +\
                c2 * self.curves[curve_c][1][1] +\
                c3 * self.curves[curve_c][2][1] +\
                c4 * self.curves[curve_c][3][1]))

    def curve_add (self, p1, p2, p3, p4):
        self.curves += [[p1, p2, p3, p4]]
        self.curves_n += 1

