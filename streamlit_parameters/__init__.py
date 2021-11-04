#
# License: BSD
#   https://raw.githubusercontent.com/stonier/streamlit_parameters/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""
Assistance for initialising and exporting the page configuration across the
user provided defaults, session state, url query string and streamlit widgets.
"""

##############################################################################
# Imports
##############################################################################

from . import demos  # noqa
from . import hello  # noqa
from . import parameters  # noqa

##############################################################################
# Version
##############################################################################

import pkg_resources

__version__ = pkg_resources.require('streamlit_parameters')[0].version
