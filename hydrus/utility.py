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
import pickle
from types import SimpleNamespace
from configparser import ConfigParser

# import yaml  # only import this when needed (it's slow)

from hydrus import constants


def read_pickle(filepath):
    """Load a pickled Python object from a file."""
    with open(filepath, 'rb') as infile:
        return pickle.load(infile)


def dump_pickle(x, filepath):
    """Pickle a Python object and save it to a file."""
    with open(filepath, 'wb') as outfile:
        pickle.dump(x, outfile)


def read_config(cfgfile='settings.cfg', section='DEFAULT'):
    """Parse the Hydrus configuration file."""
    cfg = SimpleNamespace()
    parser = ConfigParser()
    parser.read(cfgfile)

    cfg.RAPIDCLUS = parser.getboolean(section, 'RAPIDCLUS')
    cfg.QUADRATURE = parser.getboolean(section, 'QUADRATURE')
    cfg.INFILE = parser.get(section, 'INFILE')
    cfg.MEASURE_SETTINGS = parser.get(section, 'MEASURE_SETTINGS')

    return cfg


def inject_yml(ymlfile, namespace):
    """Parse a YAML file.  Add the result to a Python namespace."""
    import yaml
    with open(ymlfile) as infile:
        for name, value in yaml.load(infile).items():
            setattr(namespace, name, value)


def inject_constants(namespace):
    """
    Add the contents of of the `constants` namespace to a second Python
    namespace.
    """
    # This protects against changes to `constants.py` when running multiple
    # processes, each of which will import constants.py separately, possibly at
    # significantly different times.  It also makes testing a heck of a lot
    # easier.
    for name, value in constants.__dict__.items():
        if not name.startswith('_'):
            setattr(namespace, name, value)


def set_config(settingsfile='settings.cfg'):
    """
    Return the Hydrus application configuration and the quarter's measure
    configuration as a single namespace.
    """
    cfg = read_config(settingsfile)
    inject_yml(os.path.join(constants.IN, cfg.MEASURE_SETTINGS), cfg)
    inject_constants(cfg)
    return cfg


def winsorize(x, lo=-3., hi=3.):
    if x < lo:
        return lo
    if x > hi:
        return hi
    return x
