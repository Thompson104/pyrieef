#!/usr/bin/env python

# Copyright (c) 2020, University of Stuttgart
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
#                                        Jim Mainprice on Sunday June 13 2020

import __init__
from kinematics.homogenous_transform import *
from numpy.testing import assert_allclose


def test_planar_rotation():

    kinematic_map = PlanarRotation(np.ones(2))
    assert check_jacobian_against_finite_difference(kinematic_map)

    kinematic_map = PlanarRotation(np.array([.23, 12.]))
    assert check_jacobian_against_finite_difference(kinematic_map)


def test_homogenous_transform():

    kinematic_map = HomogenousTransform()
    assert_allclose(kinematic_map(np.zeros(3)), np.zeros(2))

    kinematic_map = HomogenousTransform(np.ones(2))
    assert_allclose(kinematic_map(np.zeros(3)), np.ones(2))

    kinematic_map = HomogenousTransform(np.ones(2))
    p1 = kinematic_map(np.array([1., 1., 0.]))
    p2 = np.array([2., 2.])
    assert_allclose(p1, p2)

    kinematic_map = HomogenousTransform(np.ones(2))
    p1 = kinematic_map(np.array([1., 1., 0.785398]))
    p2 = np.array([1., 2.41421])
    assert_allclose(p1, p2, 1e-4)


def test_homogenous_jacobian():

    kinematic_map = HomogenousTransform(np.random.rand(2))

    print("----------------------")
    print("Check identity (J implementation) : ")
    assert check_jacobian_against_finite_difference(kinematic_map)


if __name__ == "__main__":
    test_planar_rotation()
    test_homogenous_transform()
    test_homogenous_jacobian()