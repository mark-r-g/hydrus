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
import random
from collections import Counter

import numpy as np

from hydrus.rapidclus import close_outer, close_inner, choose_initial_seeds
from hydrus.rapidclus import rapidclus


def test_close_inner():
    assert close_inner([1, 3, 6, 10, 11]) == (3, 4, 10, 11, 1)
    assert close_inner(range(1, 100, 5)) == (0, 1, 1, 6, 5)


def test_close_outer():
    assert close_outer([1, 3, 6, 10, 11], 7) == (2, 6, 1)
    assert close_outer([1, 3, 6, 10, 11], 0) == (0, 1, 1)
    assert close_outer([1, 3, 6, 10, 11], 111) == (4, 11, 100)


def test_choose_initial_seeds():
    assert choose_initial_seeds([1, 3, 6, 10, 11, 100], 3) == [1, 11, 100]
    assert choose_initial_seeds([1, 3, 6, 10, 11, 100], 5) == [1, 3, 6, 11, 100]

    random.seed(36261837)
    data = [int(random.gauss(0,1000)) for _ in range(100)]
    assert choose_initial_seeds(data, 5) == [-2376, -862, 521, 1948, 3239]


def test_rapidclus():
    random.seed(12521184)
    data = [random.gauss(0,1) for _ in range(1000)]
    assert sorted(Counter(rapidclus(data)).values()) == [34, 41, 233, 251, 441]
    assert rapidclus(data) == rapidclus(np.array(data))
