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
"""
Hydrus settings that most users would have no reason to change and/or would
just be confusing to have in the .yml or .cfg files.
"""

# Set to False to not use Numba.
JIT = True

# Set to False to turn off multiprocessing (e.g. for use with cProfile).
MULTIPROCESSING = True

# Number of quadrature points to use in "old" integral:
QCOUNT = 30

# Convergence criteria for LVM minimization:
TOL = 1e-15

# Initial values for mu, gamma, and err in the optimization:
INITIAL_LVM_PARAMS = 0.025, 0.500, 0.880

# Limits for mu, gamma, and err:
# SEARCH_BOUNDS = ((None, None), (None, None), (1e-4, None))
QUAD_BOUNDS = ((None, None), (None, None), (1e-3, None))
EXACT_BOUNDS = ((None, None), (None, None), (1e-3, None))

# Set to True to skip saving output to disk.
WRITE_NOTHING = False

# Output file names.
EST_FILE = 'model_parameters_{}'
STAR_FILE = 'star_ratings'

# Mapping for column names in the SAS file or created within the script:
FRIENDLY_NAMES = (
    ('PROVIDER_ID', 'Provider ID'),
    ('mortality', 'Group Score: Mortality'),
    ('safety', 'Group Score: Safety of Care'),
    ('read', 'Group Score: Readmissions'),
    ('patientexp', 'Group Score: Patient Experience'),
    ('efficiency', 'Group Score: Efficient Use of Medical Imaging'),
    ('timeliness', 'Group Score: Timeliness of Care'),
    ('effectiveness', 'Group Score: Effectiveness of Care'),
    ('summary', 'Summary Score'),
    ('summary_win', 'Winsorized Summary Score'),
    ('cluster_name', 'Star Rating'),
    )

# Labels for the five star groups:
# CLUSTER_NAMES = ['1*', '2*', '3*', '4*', '5*']
CLUSTER_NAMES = list(range(1, 6))

# Save Hydrus' configuration information along with the script results
SAVE_DEBUG = False

# Directories for input/output files:
IN, OUT = 'input', 'output'
