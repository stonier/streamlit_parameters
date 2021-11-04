#
# License: BSD
#   https://raw.githubusercontent.com/stonier/streamlit_parameters/devel/LICENSE
#
##############################################################################
# Imports
##############################################################################

import streamlit_parameters

##############################################################################
# Entry Points
##############################################################################


# Entry point via `streamlit run ...`. This currently needs to be at the
# root of the repo so that Streamlit Cloud can discover the
# streamlit_parameters import. There might be a way to configure the
# python environment for the streamlit cloud, but I do not know of that way
# yet!

if __name__ == "__main__":
    streamlit_parameters.demos.parameters.main()
