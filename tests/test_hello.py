#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# License: BSD
#   https://raw.githubusercontent.com/stonier/streamlit_parameters/devel/LICENSE
#
##############################################################################
# Imports
##############################################################################

import streamlit_parameters

##############################################################################
# Tests
##############################################################################


def test_gday():
    print("Test - Gday")
    assert "G'day!" == streamlit_parameters.hello.gday()
