#
# License: BSD
#   https://raw.githubusercontent.com/stonier/streamlit_parameters/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""Demonstrates parameter reflection between widgets and the url query string."""

##############################################################################
# Imports
##############################################################################

import datetime
import functools
import sys

import streamlit
import streamlit.web.cli

import streamlit_parameters

##############################################################################
# Implementation
##############################################################################


def main():
    ####################
    # Page
    ####################
    title = "Parameter Reflection"
    streamlit.set_page_config(
        page_title=title, layout="wide", initial_sidebar_state="expanded"
    )
    streamlit.write(f"# {title}")

    ####################
    # Parameters
    ####################
    today = datetime.date.today()
    seven_days_ago = today - datetime.timedelta(days=7)
    string_list_params = ["flying", "spaghetti", "monster"]
    bool_options = [True, False]

    parameters = streamlit_parameters.parameters.Parameters()
    parameters.register_bool_parameter(key="foo", default_value=False)
    parameters.register_int_parameter(key="bar", default_value=5)
    parameters.register_date_parameter(key="start_date", default_value=seven_days_ago)
    parameters.register_date_parameter(key="end_date", default_value=today)
    parameters.register_string_parameter(key="category", default_value="carbonara")
    parameters.register_float_parameter(key="floating", default_value=5.0)
    parameters.register_int_range_parameter(key="int_range", default_value=[10, 20])
    parameters.register_float_range_parameter(
        key="float_range", default_value=[0.1, 10.0]
    )
    parameters.register_string_list_parameter(
        key="string_list", default_value=string_list_params
    )
    parameters.register_boolean_list_parameter(
        key="bool_list", default_value=[True, False]
    )
    parameters.register_date_range_parameter(
        key="date_range", default_value=[seven_days_ago, today]
    )

    ####################
    # Widgets
    ####################
    streamlit.sidebar.checkbox(
        label="Foo",
        value=parameters.foo.value,
        key=parameters.foo.key,
        on_change=functools.partial(
            parameters.update_parameter_from_session_state, key=parameters.foo.key
        ),
    )
    streamlit.sidebar.number_input(
        label="Bar",
        min_value=3,
        max_value=7,
        value=parameters.bar.default,
        step=1,
        key=parameters.bar.key,
        on_change=functools.partial(
            parameters.update_parameter_from_session_state, key=parameters.bar.key
        ),
    )
    streamlit.sidebar.date_input(
        label="Start Date",
        value=parameters.start_date.default,
        min_value=today - datetime.timedelta(weeks=4),
        max_value=today,
        key=parameters.start_date.key,
        on_change=functools.partial(
            parameters.update_parameter_from_session_state,
            key=parameters.start_date.key,
        ),
    )
    streamlit.sidebar.date_input(
        label="End Date",
        value=parameters.end_date.default,
        min_value=today - datetime.timedelta(weeks=4),
        max_value=today,
        key=parameters.end_date.key,
        on_change=functools.partial(
            parameters.update_parameter_from_session_state, key=parameters.end_date.key
        ),
    )
    category_indices = {"lasagne": 0, "carbonara": 1, "macaroni": 2}
    streamlit.sidebar.selectbox(
        label="Choose a Category",
        index=category_indices[parameters.category.value],
        options=["lasagne", "carbonara", "macaroni"],
        key=parameters.category.key,
        on_change=functools.partial(
            parameters.update_parameter_from_session_state, key=parameters.category.key
        ),
    )

    streamlit.sidebar.slider(
        label="Choose a float value",
        min_value=0.0,
        max_value=5.2,
        step=0.1,
        value=parameters.floating.default,
        key=parameters.floating.key,
        on_change=functools.partial(
            parameters.update_parameter_from_session_state, key=parameters.floating.key
        ),
    )

    streamlit.sidebar.slider(
        label="Choose an integer range",
        min_value=0,
        max_value=100,
        value=parameters.int_range.default,
        key=parameters.int_range.key,
        on_change=functools.partial(
            parameters.update_parameter_from_session_state, key=parameters.int_range.key
        ),
    )

    streamlit.sidebar.slider(
        label="Choose a float range",
        min_value=0.1,
        max_value=10.3,
        step=0.1,
        value=parameters.float_range.default,
        key=parameters.float_range.key,
        on_change=functools.partial(
            parameters.update_parameter_from_session_state,
            key=parameters.float_range.key,
        ),
    )

    streamlit.sidebar.multiselect(
        label="Choose a string list",
        options=string_list_params,
        default=parameters.string_list.default,
        key=parameters.string_list.key,
        on_change=functools.partial(
            parameters.update_parameter_from_session_state,
            key=parameters.string_list.key,
        ),
    )

    streamlit.sidebar.multiselect(
        label="Choose boolean list",
        options=bool_options,
        default=parameters.bool_list.default,
        key=parameters.bool_list.key,
        on_change=functools.partial(
            parameters.update_parameter_from_session_state, key=parameters.bool_list.key
        ),
    )

    streamlit.sidebar.date_input(
        label="Choose date range",
        min_value=seven_days_ago,
        max_value=today,
        value=parameters.date_range.default,
        key=parameters.date_range.key,
        on_change=functools.partial(
            parameters.update_parameter_from_session_state,
            key=parameters.date_range.key,
        ),
    )

    with streamlit.sidebar:
        parameters.create_set_all_checkbox()

    ####################
    # Set URL
    ####################
    parameters.set_url_fields()

    ####################
    # Usage
    ####################
    streamlit.write("## Usage")
    usage = f"**Foo**: {parameters.foo.value}  \n"
    usage += f"**Bar**: {parameters.bar.value}  \n"
    usage += f"**Start Date**: {parameters.start_date.value}  \n"
    usage += f"**End Date**: {parameters.end_date.value}  \n"
    usage += f"**Category**: {parameters.category.value}"
    streamlit.write(usage)

    ####################
    # Debugging
    ####################
    streamlit.write("## Debugging")

    streamlit.write("#### Query String")
    streamlit.write(streamlit.query_params)

    streamlit.write("#### Parameters")
    streamlit.write(parameters.as_dict())

    streamlit.write("#### Session State")
    streamlit.write(streamlit.session_state)


##############################################################################
# Entry Points
##############################################################################


# Needed to enable console_main(). If you have a completely configured env.
# you can run this directly via `streamlit run`. If not (e.g. Streamlit Cloud)
# then you'll have to use the entry point in demo.py in the root of this package.
if __name__ == "__main__":
    main()


# Entry point as a python console script. Not just for convenience, this
# enables a runnable demo to be packaged with e.g. a pip package.
def console_main():
    filename = __file__
    sys.argv = ["streamlit", "run", filename]
    streamlit.web.cli.main()
