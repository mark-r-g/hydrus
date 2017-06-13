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
from bisect import bisect, insort
from collections import defaultdict


def close_inner(itr):
    """
    Return the indices of the values in sorted iterable `itr` closest to each
    other, Also return the values themselves and the distance between them.
    """
    i = min(range(1, len(itr)), key=lambda x: itr[x] - itr[x - 1])
    v, vp = itr[i], itr[i - 1]
    return i - 1, i, vp, v, v - vp


def close_outer(itr, b):
    """
    For sorted iterable `itr` and numeric `b`, return the index of the value in
    itr that is closest to b.  Also return the value itself and the distance
    between itr and b.
    """
    i, length, first, last = bisect(itr, b), len(itr), itr[0], itr[-1]
    if i == length:
        return length - 1, last, b - last
    if i == 0:
        return 0, first, first - b
    vnext, vprev = itr[i], itr[i - 1]
    dnext, dprev = vnext - b, b - vprev
    if dnext < dprev:
        return i, vnext, dnext
    return i - 1, vprev, dprev


def valclose(itr, b):
    return close_outer(itr, b)[1]


def dmin(itr, b):
    return close_outer(itr, b)[2]


def choose_initial_seeds(data, maxclusters):
    # Set the seeds to the first 'maxclusters' items.
    seeds = sorted(data[:maxclusters])

    # For each of the rest of the items...
    for x in data[maxclusters:]:

        # Replace an old seed with x if the distance between x and the closest
        # seed is g.t. the smallest distance between any two seeds.
        x_close_idx, x_close_val, x_dist = close_outer(seeds, x)
        ia, ib, va, vb, d = close_inner(seeds)
        if x_dist > d:
            # Replace one of the two seeds closest to each other.  Choose the
            # seed with the shortest distance to the closest of the remaining
            # seeds when that other seed is replaced by x.
            others = seeds.copy()
            others.pop(ia)
            others.pop(ia)
            insort(others, x)
            i = ia if dmin(others, va) < dmin(others, vb) else ib
            seeds.pop(i)
            insort(seeds, x)

        # Else, replace the closest seed with x if the smallest distance from x
        # to all seeds (other than the closest one) is g.t. the shortest
        # distance from the closest seed to all other seeds.
        else:
            others = seeds.copy()
            others.remove(x_close_val)
            if dmin(others, x) > dmin(others, x_close_val):
                seeds.pop(x_close_idx)
                insort(seeds, x)

    return seeds


def rapidclus(data, maxclusters=5, maxiter=1):
    """
    Cluster the one-dimensional `data` via Simple Cluster Seeking (SCS).   This
    is the same algorithm used by SAS's "FASTCLUS" and SPSS's "QUICK CLUSTER".

    SCS roughly approximates k-means clustering, but trades accuracy of results
    for computation speed.

    Increasing the maximum number of iterations `maxiter` may yield results
    more similar to those found via k-means clustering.
    """
    seeds = choose_initial_seeds(data, maxclusters)

    for _ in range(maxiter):

        # Assign each observation to its closest seed.
        clusters = defaultdict(list)
        for x in data:
            close_seed = valclose(seeds, x)
            clusters[close_seed].append(x)

        # Replace cluster seeds with new means.
        seeds = sorted(sum(v) / len(v) for v in clusters.values())

    # Assign each observation to its closest seed one last time.
    data_clusters = [valclose(seeds, x) for x in data]

    return data_clusters
