#
# License: BSD
#   https://raw.githubusercontent.com/stonier/streamlit_parameters/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""Parameter management for intialising and exporting the page configuration."""

##############################################################################
# Imports
##############################################################################

from . import demos  # noqa
from . import hello  # noqa
from . import parameters  # noqa

##############################################################################
# Version
##############################################################################

# Update in setup.py as well
__version__ = "0.1.4"

# import pkg_resources

# Streamlit Cloud doesn't handle this one.
# __version__ = pkg_resources.require('streamlit_parameters')[0].version
