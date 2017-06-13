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
from numpy.testing import assert_approx_equal
from scipy.stats import norm

from hypothesis import given

from hydrus.model import Lvm
from tests import strat_1d, strat_pos_1d


@given(strat_1d, strat_1d, strat_1d, strat_1d, strat_pos_1d, strat_1d)
def test_preds_ll(alpha, mu, gamma, err, num, w):
    current_impl = Lvm.preds_ll(alpha, mu, gamma, err, num, w)
    simple_impl = np.nansum(w * norm.logpdf(num, mu+gamma*alpha, err))
    simple_impl += np.sum(norm.logpdf(alpha))
    assert_approx_equal(current_impl, simple_impl)
