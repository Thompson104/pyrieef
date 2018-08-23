#!/usr/bin/env python

# Copyright (c) 2015 Max Planck Institute
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
# Jim Mainprice on Sunday June 17 2017

from test_common_imports import *
from graph.shortest_path import *
import numpy as np


def check_is_close(a, b, tolerance=1e-10):
    """ Returns True of all variable are close."""
    results = np.isclose(
        np.array(a),
        np.array(b),
        atol=tolerance)
    return results.all()


def test_symetrize():
    A_res = np.array([[0, 2, 1],
                      [2, 0, 0],
                      [1, 0, 0]])
    A = np.zeros((3, 3))
    A[0, 1] = 2
    A[0, 2] = 1
    A = symmetrize(A)
    print "A : \n", A
    print "A_res : \n", A_res
    assert(check_is_close(A, A_res))

if __name__ == "__main__":
    test_symetrize()