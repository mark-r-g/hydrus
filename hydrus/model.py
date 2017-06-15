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
import datetime
import itertools
import multiprocessing

import numpy as np
from pandas import DataFrame
from scipy.optimize import minimize
from scipy.misc import logsumexp
from scipy.stats import norm

from hydrus import constants
if constants.JIT:
    from hydrus.norm import lpdf_1d, lpdf_3d, lpdf_std, nsum, nsum_row
else:
    from functools import partial
    lpdf_1d = lpdf_3d = lpdf_std = norm.logpdf
    nsum = np.nansum
    nsum_row = partial(np.nansum, axis=1)


logging.basicConfig(level=logging.INFO)

QX, QW = np.polynomial.hermite.hermgauss(constants.QCOUNT)  # location, weight
QC1 = QX * np.sqrt(2)
QC2 = np.exp(QX**2) * QW * np.sqrt(2)
LOG2PI = np.log(2 * np.pi)
ESTS_OPTS = {'maxfun': 1e10, 'maxiter': 1e10, 'maxls': 50}


def pack(itr, nmeas):
    """Pack values to the form required by `minimize()`."""
    return list(itertools.chain.from_iterable([x] * nmeas for x in itr))


def unpack_res(res):
    """Unpack the results object returned by `minimize()`."""
    return np.split(res.x, 3)


def log_result(name, res, t0=None):
    if res['success']:
        try:
            t = datetime.datetime.now() - t0
            logging.info(f'{name}: success - {t}')
        except TypeError:
            logging.info(f'{name}: success')
    else:
        msg = res['message']
        logging.info(f'{name}: {msg}')


class Lvm:
    """
    Find values for mu, gamma, err, and alpha that best fit CMS's latent
    variable model for a measure group.  Do this by maximizing the likelihood
    function (i.e. minimizing the negative of the log of the likelihood
    function) of these parameters given the hospital data for the measures
    in the group.
    """
    def __init__(self, z, w, name='', quadrature=None, cfg=None):
        self.t0 = datetime.datetime.now()

        # If given a namespace of configuration settings, use it.
        # Otherwise fall back to whatever is in `constants.py`.
        self.cfg = cfg or constants

        # If w or z are DataFrames, convert them to ndarrays.
        self.w = w.values if hasattr(w, 'values') else w
        self.z = z.values if hasattr(z, 'values') else z

        self.w2 = np.nan_to_num(self.w)
        self.num2 = np.nan_to_num(self.z)

        self.name, self.n = name, w.shape[0]
        self.ests_init = np.array(pack(self.cfg.INITIAL_LVM_PARAMS, w.shape[1]))

        if quadrature or (cfg is not None and cfg.QUADRATURE):
            self.ests_ll = self.ests_ll_quad
            self.ests_bounds = pack(self.cfg.QUAD_BOUNDS, w.shape[1])
        else:
            self.ests_ll = self.ests_ll_exact
            self.ests_bounds = pack(self.cfg.EXACT_BOUNDS, w.shape[1])

    def ests_ll_quad(self, params):
        """
        Calculate the loglikelihood given model parameters `params`.

        This method uses Gaussian quadrature, and thus returns an *approximate*
        integral.
        """
        mu0, gamma0, err0 = np.split(params, 3)
        x = np.tile(self.z, (self.cfg.QCOUNT, 1, 1))  # (QCOUNTXnhospXnmeas)
        loc = mu0 + np.outer(QC1, gamma0)
        loc = np.tile(loc, (self.n, 1, 1))
        loc = np.transpose(loc, (1, 0, 2))
        scale = np.tile(err0, (self.cfg.QCOUNT, self.n, 1))
        zs = lpdf_3d(x=x, loc=loc, scale=scale)

        w2 = np.tile(self.w, (self.cfg.QCOUNT, 1, 1))
        wted = np.nansum(w2 * zs, axis=2).T  # (nhosp X QCOUNT)
        qh = np.tile(QC1, (self.n, 1))  # (nhosp X QCOUNT)
        combined = wted + norm.logpdf(qh)  # (nhosp X QCOUNT)

        return logsumexp(np.nan_to_num(combined), b=QC2, axis=1)  # (nhosp)

    def _ests_ll_exact(self, params):
        """
        Calculate the loglikelihood given model parameters `params`.

        This method uses an exact integral and returns exact ll values, i.e.
        it does not use quadrature to approximate the integral.
        """
        mu, gamma, err = np.split(params, 3)
        err, err2, gamma2 = abs(err), err ** 2, gamma ** 2
        num_mu = self.z - mu

        # Many thanks to github.com/huangrh for figuring this part out.  All I
        # did was convert his solution to code.
        h = nsum_row(self.w * (LOG2PI + 2 * np.log(err)) / 2)
        a = nsum_row(self.w * gamma2 / err2) + 1
        b = nsum_row(self.w / err2 * num_mu * gamma)
        c = nsum_row(self.w / err2 * num_mu**2 / 2)

        return np.log(2*np.pi/a)/2 + b**2/a/2 - LOG2PI/2 - h - c

    def ests_ll_exact(self, params):
        """
        Calculate the loglikelihood given model parameters `params`.

        This method uses an exact integral and returns exact ll values, i.e.
        it does not use quadrature to approximate the integral.
        """
        # Many thanks to github.com/huangrh for figuring this part out.  All I
        # did was convert his solution to code.
        mu, gamma, err = np.split(params, 3)
        d = self.num2 - mu
        q = self.w2 / err**2
        r = d * q

        f = self.w2 @ (2 * np.log(abs(err)) + LOG2PI)
        a = q @ gamma**2
        b = r @ gamma
        c = nsum_row(d * r)

        return .5 * (b * b / (a+1) - c - f - np.log1p(a))

    def ests_obj(self, params):
        """The objective function to minimize for the model parameters."""
        # return -nsum(self.ests_ll(params))
        return -np.nansum(self.ests_ll(params))

    def estimate(self):
        """Minimize the objective function to estimate the model parameters."""
        res = minimize(
            self.ests_obj, self.ests_init, method='L-BFGS-B',
            tol=self.cfg.TOL, bounds=self.ests_bounds, options=ESTS_OPTS,
            )
        self.final_ests = unpack_res(res)
        log_result(self.name, res, self.t0)
        return self.final_ests

    @staticmethod
    def preds_ll(alpha: np.ndarray, mu, gamma, err, z, w) -> np.float64:
        """Calculate the loglikelihood for the predictions."""
        ll = nsum(w * lpdf_1d(z, mu+gamma*alpha, err))
        ll += np.sum(lpdf_std(alpha))
        return ll

    def preds_obj(self, alpha, other):
        """The objective function to minimize to predict the random effects."""
        return -self.preds_ll(alpha, *other)

    def predict(self):
        """Predict the random effects."""
        out = []
        for num0, w0 in zip(self.z, self.w):
            res = minimize(
                self.preds_obj, [0.],
                ([*self.final_ests, num0, w0],), "L-BFGS-B",
                )
            out.append(res.x[0])
        self.final_preds = np.array(out)
        return self.final_preds


def outcomes(data, meas_filter, name, cfg=None):
    logging.info(f'creating LVM for {name}')

    # Filter to measures in this group.
    grp_nums, grp_denoms = meas_filter
    num_df = data[grp_nums]
    denom_df = data[grp_denoms]

    # Calculate measure weights.
    meas_hosp_counts = num_df.notnull().sum()
    meas_weights = denom_df / denom_df.sum() * meas_hosp_counts.values

    # Run the LVM.
    lvm = Lvm(num_df, meas_weights, name, cfg=cfg)
    estimates = lvm.estimate()
    predictions = lvm.predict()

    # Parse the LVM results.
    mu, gamma, err = estimates
    est_df = DataFrame({'mu': mu, 'gamma': gamma, 'err': err}, grp_nums)
    est_df = est_df[['mu', 'gamma', 'err']]
    pred_df = DataFrame({name: predictions}, data.index)

    return est_df, pred_df


def oserial(std_data, final_meas, groups=None, cfg=None):
    # Serial run is needed to get anything useful from cProfile.
    if cfg is not None:
        groups = cfg.GROUPS
    est_dfs, pred_dfs = [], []
    for g in groups:
        est_df, pred_df = outcomes(std_data, final_meas[g], g, cfg)
        est_dfs.append(est_df)
        pred_dfs.append(pred_df)
    return est_dfs, pred_dfs


def worker(group_data):
    return outcomes(*group_data)


def oparallel(std_data, final_meas, groups=None, cfg=None):
    """Calculate the hospital group scores for each LVM."""
    if cfg is not None:
        groups = cfg.GROUPS

    cpus = os.cpu_count()
    # nproc = 1 if cpus is None else cpus - 1 or 1  # leave one CPU unused
    nproc = 1 if cpus is None else cpus  # use all CPUs

    pool = multiprocessing.Pool(nproc)
    group_data = zip(
        [std_data for _ in groups],
        [final_meas[g] for g in groups],
        groups,
        [cfg for _ in groups]
        )
    r = pool.map(worker, group_data)
    return zip(*r)
