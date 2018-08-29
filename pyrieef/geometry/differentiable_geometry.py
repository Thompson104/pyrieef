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

import numpy as np
import copy
from abc import abstractmethod


class DifferentiableMap:

    @abstractmethod
    def output_dimension(self):
        raise NotImplementedError()

    @abstractmethod
    def input_dimension(self):
        raise NotImplementedError()

    def __call__(self, q):
        """ Method called when call object """
        return self.forward(q)

    @abstractmethod
    def forward(self, q):
        """ Should return an array or single value"""
        raise NotImplementedError()

    def gradient(self, q):
        """ Should return an array or single value
                n : input dimension
            Convienience function to get numpy gradients in the same shape
            as the input vector
            for addition and substraction, of course gradients are
            only availables if the output dimension is one."""
        assert self.output_dimension() == 1
        return np.array(self.jacobian(q)).reshape(self.input_dimension())

    def jacobian(self, q):
        """ Should return a matrix or single value of 
                m x n : ouput x input (dimensions)
            by default the method returns the finite difference jacobian.
            WARNING the object returned by this function is a numpy matrix.
            Thhe Jacobian matrix is allways a numpy matrix object."""
        return finite_difference_jacobian(self, q)

    def evaluate(self, q):
        """ Evaluates the map and jacobian simultaneously. The default
            implementation simply calls both forward and Getjacobian()
            separately but overriding this method can make the evaluation
            more efficient """
        x = self.forward(q)
        J = self.jacobian(q)
        return [x, J]


class Compose(DifferentiableMap):

    def __init__(self, f, g):
        """
            f round g : f(g(x))

            This function should be called pullback if we approxiate
            higher order (i.e., hessians) derivaties by pullback, here it's
            computing the true 1st order derivative of the composition.

            """
        # Make sure the composition makes sense
        assert g.output_dimension() == f.input_dimension()
        self._f = f
        self._g = g

    def output_dimension(self):
        return self._f.output_dimension()

    def input_dimension(self):
        return self._g.input_dimension()

    def forward(self, q):
        return self._f(self._g(q))

    def jacobian(self, q):
        [y, J] = self.evaluate(q)
        return J

    def evaluate(self, q):
        """  d/dq f(g(q)), applies chain rule.

            If J is the jacobian of a function f(x), J_f = d/dx f(x)
            then the jacobian of the "pullback" of f defined on the
            range space of a map g, f(g(q)) is
                    d/dq f(g(q)) = J_f(g(q)) J_g
            This method computes and
            returns this "pullback gradient" J_f (g(q)) J_g(q).
            WARNING: J_f is assumed to be a jacobian np.matrix object
        """
        x = self._g(q)
        [y, J_f] = self._f.evaluate(x)
        J = J_f * self._g.jacobian(q)
        return [y, J]


class Scale(DifferentiableMap):
    """Scales a function by a constant"""

    def __init__(self, f, alpha):
        self._f = f
        self._alpha = alpha

    def output_dimension(self):
        return self._f.output_dimension()

    def input_dimension(self):
        return self._f.input_dimension()

    def forward(self, q):
        return self._alpha * self._f.forward(q)

    def jacobian(self, q):
        return self._alpha * self._f.jacobian(q)


class RangeSubspaceMap(DifferentiableMap):
    """Take only some outputs"""

    def __init__(self, n, indices):
        """n is the input dimension
           indices are the output"""
        self._indices = indices
        self._dim = n

    def output_dimension(self):
        return len(self._indices)

    def input_dimension(self):
        return self._dim

    def forward(self, q):
        return q[self._indices]

    def jacobian(self, q):
        I = np.matrix(np.eye(self._dim))
        return I[self._indices, :]


class ProductFunction(DifferentiableMap):
    """Take the product of functions"""

    def __init__(self, g, h):
        """ f(x) = g(x)h(x)
            n is the input dimension
           indices are the output"""
        self._g = g
        self._h = h
        # print "self._g.input_dimension() : ", self._g.input_dimension()
        # print "self._h.input_dimension() : ", self._h.input_dimension()
        assert self._g.input_dimension() == self._h.input_dimension()
        assert self._g.output_dimension() == 1
        assert self._h.output_dimension() == 1

    def output_dimension(self):
        return 1

    def input_dimension(self):
        return self._g.input_dimension()

    def forward(self, x):
        v1 = self._g.forward(x)
        v2 = self._h.forward(x)
        return v1 * v2

    def jacobian(self, x):
        v1 = self._g.forward(x)
        v2 = self._h.forward(x)
        J1 = self._g.jacobian(x)
        J2 = self._h.jacobian(x)
        return v1 * J2 + v2 * J1


class AffineMap(DifferentiableMap):
    """Simple map of the form: f(x)=ax + b"""

    def __init__(self, a, b):
        self._a = np.matrix(a)  # Make sure that a is matrix
        self._b = np.matrix(b.reshape(b.size, 1))

    def output_dimension(self):
        return self._b.shape[0]

    def input_dimension(self):
        return self._a.shape[1]

    def forward(self, x):
        x_tmp = x.reshape(self.input_dimension(), 1)
        tmp = self._a * x_tmp
        y = tmp + self._b
        return np.array(y).reshape(self.output_dimension())

    def jacobian(self, x):
        return self._a


class QuadricFunction(DifferentiableMap):
    """ Here we implement a quadric funciton of the form:
        f(x) = x^T A x + bx + c """

    def __init__(self, a, b, c):
        assert a.shape[0] == a.shape[1]
        assert b.size == a.shape[1]
        self._a = np.matrix(a)
        self._b = np.matrix(b.reshape(b.size, 1))
        self._c = c
        self._symmetric = np.allclose(self._a, self._a.T, atol=1e-8)
        self._posdef = np.all(np.linalg.eigvals(self._a) > 0)

    def output_dimension(self):
        return 1

    def input_dimension(self):
        return self._b.size

    def forward(self, x):
        x_tmp = np.matrix(x.reshape(self._b.size, 1))
        v = (0.5 *
             x_tmp.transpose() * self._a * x_tmp +
             self._b.transpose() * x_tmp +
             self._c)
        return v

    def jacobian(self, x):
        """ when the matrix is positive this can be simplified
            see matrix cookbook """
        x_tmp = np.matrix(x.reshape(self._b.size, 1))
        if self._symmetric and self._posdef:
            a_term = self._a.transpose() * x_tmp
        else:
            a_term = 0.5 * (self._a + self._a.transpose()) * x_tmp
        return (a_term + self._b).transpose()


class SquaredNorm(DifferentiableMap):
    """ Simple squared norm : f(x)= | x - x_0 | ^2 """

    def __init__(self, x_0):
        self.x_0 = x_0

    def output_dimension(self):
        return 1

    def input_dimension(self):
        return self.x_0.size

    def forward(self, x):
        delta_x = np.array(x).reshape(x.size) - self.x_0
        return 0.5 * np.dot(delta_x, delta_x)

    def jacobian(self, x):
        delta_x = x - self.x_0
        return np.matrix(delta_x)


class IdentityMap(DifferentiableMap):
    """Simple identity map : f(x)=x"""

    def __init__(self, n):
        self._dim = n

    def output_dimension(self):
        return self._dim

    def input_dimension(self):
        return self._dim

    def forward(self, q):
        return q

    def jacobian(self, q):
        return np.matrix(np.eye(self._dim))


class ZeroMap(DifferentiableMap):
    """Simple identity map : f(x)=0"""

    def __init__(self, m, n):
        self._n = n
        self._m = m

    def output_dimension(self):
        return self._m

    def input_dimension(self):
        return self._n

    def forward(self, q):
        return np.zeros(self._m)

    def jacobian(self, q):
        return np.matrix(np.zeros((self._m, self._n)))


def finite_difference_jacobian(f, q):
    """ Takes an object f that has a forward method returning
    a numpy array when querried. """
    dt = 1e-4
    dt_half = dt / 2.
    J = np.zeros((
        f.output_dimension(), f.input_dimension()))
    for j in range(q.size):
        q_up = copy.deepcopy(q)
        q_up[j] += dt_half
        x_up = f.forward(q_up)
        q_down = copy.deepcopy(q)
        q_down[j] -= dt_half
        x_down = f.forward(q_down)
        J[:, j] = (x_up - x_down) / dt
    return np.matrix(J)


def check_is_close(a, b, tolerance=1e-10):
    """ Returns True of all variable are close."""
    results = np.isclose(
        np.array(a),
        np.array(b),
        atol=tolerance)
    return results.all()


def check_jacobian_against_finite_difference(phi, verbose=True):
    """ Makes sure the jacobian is close to the finite difference """
    q = np.random.rand(phi.input_dimension())
    J = phi.jacobian(q)
    J_diff = finite_difference_jacobian(phi, q)
    if verbose:
        print "J : "
        print J
        print "J_diff : "
        print J_diff
    return check_is_close(J, J_diff, 1e-4)
