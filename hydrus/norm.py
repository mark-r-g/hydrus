# Mark Gatheman <markrg@protonmail.com>
#
# This file is part of Hydrus.
#
# Hydrus is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Hydrus is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Hydrus.  If not, see <http://www.gnu.org/licenses/>.
from warnings import filterwarnings

from numpy import log, nansum, pi, sqrt
from numba import jit, f8


# from scipy.stats._continuous_distns import _norm_pdf_logC
_norm_pdf_logC = log(sqrt(2 * pi))


filterwarnings('ignore', '.*encountered in log', RuntimeWarning)


def lpdf(x, loc, scale):
    """
    Log of the probability density function at x of a normal RV.

    This is a much faster version of `scipy.stats.norm.logpdf` that skips type
    checking and conversions.
    """
    return -((x-loc)/scale)**2 / 2.0 - _norm_pdf_logC - log(scale)


lpdf_1d = jit(f8[:](f8[:], f8[:], f8[:]))(lpdf)


lpdf_3d = jit(f8[:,:,:](f8[:,:,:], f8[:,:,:], f8[:,:,:]))(lpdf)


@jit(f8[:](f8[:]))
def lpdf_std(x):
    """
    Log of the probability density function at x of a standard normal RV.

    This is a variant of `lpdf` that assumes loc=0 and scale=1.
    """
    return -x**2 / 2.0 - _norm_pdf_logC


@jit(f8(f8[:]))
def nsum(a):
    """JIT-compiled version of `numpy.nansum` for 1-D arrays of floats."""
    return nansum(a)


@jit(f8[:](f8[:,:]))
def nsum_row(a):
    return nansum(a, axis=1)
