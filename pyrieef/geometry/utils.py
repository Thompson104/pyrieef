#!/usr/bin/env python

# Copyright (c) 2018, University of Stuttgart
# All rights reserved.
#
# Permission to use, copy, modify, and distribute this software for any purpose
# with or without   fee is hereby granted, provided   that the above  copyright
# notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS  SOFTWARE INCLUDING ALL  IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR  BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR  ANY DAMAGES WHATSOEVER RESULTING  FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION,   ARISING OUT OF OR IN    CONNECTION WITH THE USE   OR
# PERFORMANCE OF THIS SOFTWARE.
#
#                                        Jim Mainprice on Sunday June 13 2018

import numpy as np
from scipy.optimize import fsolve


def normalize(v):
    # norm=np.linalg.norm(v, ord=1)
    norm = np.linalg.norm(v)
    if norm == 0:
        print("norm is 0")
        norm = np.finfo(v.dtype).eps
    return v / norm


def line_parameters(p1, p2):
    """
    Extract 2D line parameters from two points
     where the line equation is y = ax + b

         Parameters
         ----------
         p1, p2 : 2d arrays
    """
    a = (p1[1] - p2[1]) / (p1[0] - p2[0])
    b = p1[1] - a * p1[0]
    return a, b


def line_line_intersection(p1, p2, p3, p4):
    """
    Determines the intersection point between two lines L1 and L2

        Parameters
        ----------
        p1, p2 : points on L1
        p3, p4 : points on L2

        see https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
        """
    a, b = line_parameters(p1, p2)
    c, d = line_parameters(p3, p4)
    return np.array([(d - c) / (a - b), (a * d - b * c) / (a - b)])


def lw(x):
    """Lambert W function, for real x >= 0."""
    def func(w, x):
        return np.log(x) - np.log(w) - w

    if x == 0:
        return 0
    if x > 2.5:
        lnx = np.log(x)
        w0 = lnx - np.log(lnx)
    elif x > 0.25:
        w0 = 0.8 * np.log(x + 1)
    else:
        w0 = x * (1.0 - x)

    return fsolve(func, w0, args=(x,))[0]
