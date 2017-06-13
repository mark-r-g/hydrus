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

from numpy import nan, where
from pandas import read_sas

from hydrus.utility import set_config, winsorize
from hydrus import constants


def preprocess(infile=None, settings_file=None, cfg=None):
    """
    Preprocess CMS's raw data file.  Remove non-qualifying data according to
    CMS's specifications, standardize each measure score, and winsorize the
    scores at three standard deviations.  Return the new DataFrame and a dict
    of the final measures for each measure group.
    """
    if cfg is None:
        if settings_file:
            cfg = set_config(settings_file)
        else:
            logging.warning("Using default configuration file.")
            cfg = set_config()
    if infile is None:
        infile = os.path.join(constants.IN, cfg.INFILE)

    # Load CMS's SAS data file.
    df = read_sas(infile, index='PROVIDER_ID')
    df.index = df.index.astype(str)

    # Combine measures IMM-3 and OP-27.
    mask = df['IMM_3'].notnull()
    df['IMM_3_OP_27'] = where(mask, df['IMM_3'], df['OP_27'])
    df['IMM_3_OP_27_DEN'] = where(mask, df['IMM_3_DEN'], df['OP_27_DEN'])
    for x in ['IMM_3', 'OP_27', 'IMM_3_DEN', 'OP_27_DEN']:
        df.drop(x, axis=1, inplace=True)

    # Remove columns where <= 100 hospitals have data.
    incl_meas, incl_den = [], []
    counts = df.count()  # nonnull hospitals per measure
    for k, v in counts.items():
        if k.endswith('_DEN'):
            continue
        if v <= 100:
            df.drop(k, axis=1, inplace=True)
            df.drop(k+'_DEN', axis=1, inplace=True)
            logging.info(f'dropped {k} (<=100 hospitals have data)')
        else:
            incl_meas.append(k)
            incl_den.append(k+'_DEN')

    # Create special denominators for patient experience group.
    patientexp_denom = df['H_NUMB_COMP'] * df['H_RESP_RATE_P'] / 100
    for col_name in cfg.PATIENTEXP_DENOM_COLS:
        df[col_name] = patientexp_denom

    # For each measure, if the denominator is NAN, make the numerator NAN too.
    for x, y in zip(incl_meas, incl_den):
        if y in df.columns:  # skips H_RESP_RATE_P and H_NUMB_COMP
            df.loc[df[y].isnull(), x] = nan

    # Create final list of measures for each measure group.
    final_meas = {}
    for g in cfg.GROUPS:
        final_meas[g] = (
            [x for x in incl_meas if x in cfg.MEAS_GROUPS[g]],
            [y for x, y in zip(incl_meas, incl_den) if x in cfg.MEAS_GROUPS[g]]
            )

    # Remove hospitals with no final measures.
    df = df.dropna(thresh=1)

    # Convert to z-scores.
    for col_name in incl_meas:
        col = df[col_name]
        df[col_name] = (col - col.mean()) / col.std()

    # Switch sign of measures for which a lower score is good.
    for col_name in cfg.FLIPPED_MEASURES:
        df[col_name] = -1 * df[col_name]

    # Winsorize z-scores at +/-3.
    for col_name in incl_meas:
        df[col_name] = df[col_name].map(winsorize)

    return df, final_meas
