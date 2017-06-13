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
import numpy as np
from numpy.testing import assert_almost_equal as aae
from scipy.stats import norm
from hypothesis import given, assume

from hydrus.norm import lpdf, lpdf_1d, lpdf_3d, lpdf_std, nsum, nsum_row
from tests import strat_1d, strat_3d
from tests import strat_pos_1d, strat_pos_3d
from tests import strat_nan_1d, strat_nan_2d


@given(strat_1d, strat_1d, strat_pos_1d)
def test_lpdf(x, loc, scale):
    aae(lpdf(x, loc, scale), norm.logpdf(x, loc, scale))


@given(strat_1d, strat_1d, strat_pos_1d)
def test_lpdf_1d(x, loc, scale):
    aae(lpdf_1d(x, loc, scale), norm.logpdf(x, loc, scale))


@given(strat_3d, strat_3d, strat_pos_3d)
def test_lpdf_3d(x, loc, scale):
    aae(lpdf_3d(x, loc, scale), norm.logpdf(x, loc, scale))


@given(strat_1d)
def test_lpdf_std(x):
    aae(lpdf_std(x), norm.logpdf(x))


@given(strat_nan_1d)
def test_nsum(x):
    assume(np.max(x[np.isfinite(x)]) < 1e4)
    assume(np.min(x[np.isfinite(x)]) > -1e4)
    aae(nsum(x), np.nansum(x))


@given(strat_nan_2d)
def test_nsum_row(x):
    assume(np.max(x[np.isfinite(x)]) < 1e4)
    assume(np.min(x[np.isfinite(x)]) > -1e4)
    aae(nsum_row(x), np.nansum(x, axis=1))
