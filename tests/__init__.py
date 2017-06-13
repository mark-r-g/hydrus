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
import logging

import numpy as np
from numpy.testing import assert_almost_equal, assert_approx_equal
from scipy import stats

from hypothesis.strategies import floats
from hypothesis.extra.numpy import arrays


logging.disable(logging.CRITICAL)


strat_1d = arrays(
    np.float, (100,), floats(min_value=-9., max_value=9.)
    )

strat_3d = arrays(
    np.float, (5, 5, 5), floats(min_value=-9., max_value=9.)
    )

strat_pos_1d = arrays(
    np.float, (100,), floats(min_value=1e-6, max_value=9.)
    )

strat_pos_3d = arrays(
    np.float, (5, 5, 5), floats(min_value=1e-6, max_value=9.)
    )

strat_nan_1d = arrays(
    np.float, (100,), floats(allow_nan=True, allow_infinity=False)
    )

strat_nan_2d = arrays(
    np.float, (20, 20), floats(allow_nan=True, allow_infinity=False)
    )
