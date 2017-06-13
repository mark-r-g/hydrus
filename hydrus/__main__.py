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
import os
import logging
import pickle
from time import time
from functools import reduce

from numpy import vstack, where, nan
from pandas import DataFrame, merge
from sklearn.cluster import KMeans

from hydrus import constants
from hydrus.utility import set_config, winsorize, dump_pickle
from hydrus.preprocess import preprocess
from hydrus.model import oserial, oparallel
from hydrus.rapidclus import rapidclus


def merge_on_index(df1, df2):
    return merge(df1, df2, left_index=True, right_index=True)


def save(df, folder, outfile):
    f = os.path.join(folder, f'{outfile}.csv')
    df.to_csv(f, float_format='%.5f')


def summarize(df, group_weights):
    """Combine LVM group scores into hospital summary scores."""
    # Add CMS's predefined group-level weights.
    w = DataFrame(index=df.index)
    for k, v in group_weights:
        w[k] = v

    # Rebalance group weights for hospitals that have missing scores.
    # E.g. if efficiency is missing, change mortality from 22/100 to 22/96.
    nn = df.notnull()
    nnw = w[nn]
    wdf = DataFrame(
        where(nn, w.values / vstack(nnw.sum(axis=1)), nan),
        columns=df.columns,
        index=df.index,
        )

    # Combine the weighted group scores.
    weighted = where(wdf.notnull(), wdf * df, 0)
    df['summary'] = weighted.sum(axis=1)

    # Winsorize summary scores at 0.5 and 99.5 percentiles.
    lo = df['summary'].quantile(.005, interpolation='lower')
    hi = df['summary'].quantile(.995, interpolation='higher')
    df['summary_win'] = df['summary'].map(lambda x: winsorize(x, lo=lo, hi=hi))

    return df


def cluster_kmeans(scores, cfg=None):
    """Calculate star ratings via k-means."""
    if cfg is None:
        cfg = constants
    kmeans = KMeans(n_clusters=5, tol=1e-6, n_init=500)
    kfit = kmeans.fit(vstack(scores))
    centers = [x[0] for x in kfit.cluster_centers_]
    names = dict(zip(sorted(centers), cfg.CLUSTER_NAMES))
    cid_to_name = {i: names[x] for i, x in enumerate(centers)}
    return [cid_to_name[x] for x in kfit.labels_]


def cluster_scs(scores, cfg=None):
    """Calculate star ratings via Simple Cluster Seeking."""
    if cfg is None:
        cfg = constants
    cluster_assignments = rapidclus(scores)
    sorted_centers = sorted(set(cluster_assignments))
    names = dict(zip(sorted_centers, cfg.CLUSTER_NAMES))
    return [names[x] for x in cluster_assignments]


def main(outdir=None, cfg=None):
    STARTTIME = int(time())
    if cfg is None:
        cfg = set_config()
    std_data, final_meas = preprocess(cfg=cfg)

    # Calculate group-level hospital scores.
    # with CfgTempfile(cfg) as tmpcfg:
    outcf = oparallel if cfg.MULTIPROCESSING else oserial
    edfs, pdfs = outcf(std_data, final_meas, cfg=cfg)

    # If a hospital has no data in a group, replace their score with NAN.
    for g, pdf in zip(cfg.GROUPS, pdfs):
        grp_nums = std_data[final_meas[g][0]]
        gt0 = grp_nums.notnull().sum(axis=1).map(bool)  # hosps with >=1 meas
        pdf[g] = where(vstack(~gt0), nan, pdf)

    # Calculate hospital summary scores and star ratings.
    all_group_scores = reduce(merge_on_index, pdfs)
    summ_scores = summarize(all_group_scores, cfg.GROUP_WEIGHTS)
    cfunc = cluster_scs if cfg.RAPIDCLUS else cluster_kmeans
    summ_scores['cluster_name'] = cfunc(summ_scores['summary_win'], cfg=cfg)

    # Write results to disk.
    if cfg.WRITE_NOTHING:
        return summ_scores
    if outdir is None:
        outdir = str(STARTTIME)
    if not os.path.exists(cfg.OUT):
        os.mkdir(cfg.OUT)
    OUTFOLDER = os.path.join(cfg.OUT, outdir)
    os.mkdir(OUTFOLDER)

    for name, edf in zip(cfg.GROUPS, edfs):
        save(edf, OUTFOLDER, cfg.EST_FILE.format(name))

    output = summ_scores.copy()
    output.columns = [dict(cfg.FRIENDLY_NAMES)[x] for x in output.columns]
    save(output, OUTFOLDER, cfg.STAR_FILE)
    if cfg.SAVE_DEBUG:
        dump_pickle(cfg, os.path.join(OUTFOLDER, 'config.pkl'))

    full_duration = int(time()) - STARTTIME
    logging.info(f'script completed in {full_duration:,} seconds')
    return summ_scores


if __name__ == '__main__':
    from sys import argv
    try:
        _, outdir = argv
    except ValueError:
        outdir = None
    main(outdir)
