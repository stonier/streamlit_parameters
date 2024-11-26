#
# License: BSD
#   https://raw.githubusercontent.com/stonier/streamlit_parameters/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""Machinery for initialisation and export of parameters relating to page configuration."""

##############################################################################
# Imports
##############################################################################

import datetime
from distutils import util
from typing import Any, Callable, List, Tuple

import dateutil.parser

import streamlit

##############################################################################
# Helper Methods
##############################################################################


def _convert_list_or_tuple(values, to_str=str):
    return "(" + ",".join(to_str(value) for value in values) + ")"


##############################################################################
# Data Structures
##############################################################################


class Parameter(object):
    """Stores default, current and metadata about a parameter."""

    def __init__(
        self,
        key: str,
        default: Any,
        touched: bool = False,
        to_str: Callable[[Any], str] = str,
    ):
        """
        Initialise the parameter with defaults, state and metadata.

        Args:
            key: name of this parameter
            default: initial value
            touched: flagged for export or otherwise
            to_str: Custom string conversion function. Defaults to str()
        """
        self.key = key
        self.default: Any = default
        self.value: Any = default
        self.touched: bool = touched
        self.to_str = to_str

    def update(self, new_value: Any):
        """Override the current value.

        Since it's no longer the default, flag it
        as touched so it gets embedded in URL queries.

        Args:
            new_value: duh, new value
        """
        self.value = new_value
        self.touched = True

    def __repr__(self) -> str:
        """Return the unique representation for the class.

        Returns:
            The unqiue string representation for the class.
        """
        return f"Parameter(default={self.default},value={self.value},touched={self.touched})"


class AttrDict(dict):
    """Convenience class that enables attribute access for dictionaries."""

    def __init__(self, *args, **kwargs):
        """Pass through initialisation to the dict class."""
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


##############################################################################
# Classes & Methods
##############################################################################


class Parameters(object):
    """Machinery for the parameters that define the viewing state of your app.

    This class connects the configuration
    of input widgets to the URL query string so that it
    can be copy/pasted and reproduced elsehwere without having to click through
    a sequence of steps that put the user into that state.

    Technically, this class hides the interactions with the session state
    and retrieval/insertion into the URL query string. All a user needs
    to interact with are the methods and attributes of this class.

    **Usage**

     * register a parameter
     * use the parameter default for the widget default
     * add a matching key to a widget
     * add an on_change hook to the widget.
     * set url fields
     * put on your peril-sensitive sunglasses and be froody!

    .. code-block::

        parameters = streamlit_parameters.parameters.Parameters()
        parameters.register_date_parameter(key="start_date", default_value=seven_days_ago)  # <-- 1
        streamlit.sidebar.date_input(
            value=parameters.start_date.default,  # <-- 2
            key=parameters.start_date.key,  # <-- 3
            on_change=functools.partial( # <-- 4
                parameters.update_parameter_from_session_state,
                key=parameters.start_date.key
            )
        )

        parameters.set_url_fields()  # <-- 5 (does all fields in one batch call)

        streamlit.write("**Start Date**: {parameters.start_date.value}")  # <-- 6

    **Modes**

    To enable a user to toggle between partial (overridden parameters only) or
    full (all parameters) embedding of parameters in the URL query string:
    .. code-block:: python

        parameters = streamlit_mercury_utilities.parameters.Parameters()
        with streamlit.sidebar:
            parameters.create_set_all_checkbox()

    *Type Support*

    Support exists for the following types:

    * bool
    * datetime.date
    * int
    * str

    This class also handles the problem described in
    https://github.com/streamlit/streamlit/issues/1532 by saving and reusing the
    initial default for a parameter on the session state.
    """

    def __init__(self):
        """Initialise required session state variables."""
        # using an AttrDict here for convenient attribute referencing on a dict
        if "_parameters" not in streamlit.session_state:
            streamlit.session_state._parameters = AttrDict(dict())
            streamlit.session_state._parameters_set_all = False

    def __getattr__(self, key: str) -> Parameter:
        """Return the parameter stored on the session state object.

        This is a convenience that lets you access parameters as
        attributes of the class:

        .. code-block:: python

            parameters = streamlit_parameters.parameters.Parameters()
            parameters.register_int_parameter(key="foo", default_value=5)
            parameters.foo.update(new_value=4)
            print(f"parameters.foo")

        @raise KeyError: if the parameter does not exist.
        """
        return streamlit.session_state._parameters[key]

    @staticmethod
    def is_set_all() -> bool:
        """
        Check the state of the flag that determines the export mode.

        Either partial (overridden parameters) or full (all parameters).
        """
        return streamlit.session_state._parameters_set_all

    @staticmethod
    def create_set_all_checkbox():
        """
        Return a convenience checkbox for interactively toggling the export mode.

        .. code-block:: python

            parameters = streamlit_parameters.parameters.Parameters()
            with streamlit.sidebar:
                parameters.create_set_all_checkbox()

        Returns
            A streamlit checkbox widget
        """
        return streamlit.sidebar.checkbox(
            label="Set All Params in URL Query",
            value=False,
            key="_parameters_set_all",
        )

    @staticmethod
    def as_dict():
        """
        Return a dictionary of all the parameters.

        Returns:
            An ordinary (attributeless) dictionary.
        """
        return dict(streamlit.session_state._parameters.__dict__)

    @staticmethod
    def register_int_parameter(key: str, default_value: int):
        """
        Register an int type parameter.

        Initialise it from the url query
        string, or as a fallback, with the provided default value if the key is
        not present in the url query string.

        @raises:
            ValueError if conversion from a provided str value in the url field fails
        """
        if Parameters._already_registered(key):
            return
        try:
            parameter = Parameter(
                key=key, default=int(Parameters._fetch_url_field(key)), touched=True
            )
        except KeyError:
            parameter = Parameter(key=key, default=default_value)
        streamlit.session_state._parameters[key] = parameter

    @staticmethod
    def _read_list_or_tuple(key, split_sequence=","):
        raw_str = Parameters._fetch_url_field(key)
        if raw_str[0] in ("(", "["):
            raw_str = raw_str[1:]
        if raw_str[-1] in (")", "]"):
            raw_str = raw_str[:-1]
        new_values = []
        if raw_str:
            values = raw_str.split(split_sequence)
            # Remove any quotes that may be added to the string.
            for value in values:
                new_value = value.strip()
                if new_value[0] == "'":
                    new_value = new_value[1:]
                if new_value[-1] == "'":
                    new_value = new_value[:-1]
                new_values.append(new_value)
        return new_values

    @staticmethod
    def _register_range_parameter(
        key: str, default_value: Tuple[Any, Any], convert_callable
    ):
        if Parameters._already_registered(key):
            return
        try:
            parts = [convert_callable(i) for i in Parameters._read_list_or_tuple(key)]
            assert len(parts) == 2, "Should have 2 parts for a range"
            parameter = Parameter(
                key=key,
                default=(parts[0], parts[1]),
                touched=True,
                to_str=_convert_list_or_tuple,
            )
        except KeyError:
            parameter = Parameter(
                key=key, default=default_value, to_str=_convert_list_or_tuple
            )
        streamlit.session_state._parameters[key] = parameter

    @staticmethod
    def register_int_range_parameter(key: str, default_value: Tuple[int, int]):
        """
        Register an int range type parameter.

        Initialise it from the url query
        string, or as a fallback, with the provided default value if the key is
        not present in the url query string.

        @raises:
            ValueError if conversion from a provided str value in the url field fails
        """
        Parameters._register_range_parameter(key, default_value, int)

    @staticmethod
    def register_float_parameter(key: str, default_value: float):
        """
        Register a float type parameter.

        Initialise it from the url query
        string, or as a fallback, with the provided default value if the key is
        not present in the url query string.

        @raises:
            ValueError if conversion from a provided str value in the url field fails
        """
        if Parameters._already_registered(key):
            return
        try:
            parameter = Parameter(
                key=key, default=float(Parameters._fetch_url_field(key)), touched=True
            )
        except KeyError:
            parameter = Parameter(key=key, default=default_value)
        streamlit.session_state._parameters[key] = parameter

    @staticmethod
    def register_float_range_parameter(key: str, default_value: Tuple[int, int]):
        """
        Register a float range type parameter.

        Initialise it from the url query
        string, or as a fallback, with the provided default value if the key is
        not present in the url query string.

        @raises:
            ValueError if conversion from a provided str value in the url field fails
        """
        Parameters._register_range_parameter(key, default_value, float)

    @staticmethod
    def register_string_parameter(key: str, default_value: str):
        """
        Register a string parameter.

        Initialise it from the url query
        string, or as a fallback, with the provided default value if the key is
        not present in the url query string.
        """
        if Parameters._already_registered(key):
            return
        try:
            parameter = Parameter(
                key=key, default=Parameters._fetch_url_field(key), touched=True
            )
        except KeyError:
            parameter = Parameter(key=key, default=default_value)
        streamlit.session_state._parameters[key] = parameter

    @staticmethod
    def register_string_list_parameter(key: str, default_value: List[str]):
        """
        Register a string list parameter.

        Initialise it from the url query
        string, or as a fallback, with the provided default value if the key is
        not present in the url query string.
        """
        if Parameters._already_registered(key):
            return
        try:
            # Remove the initial and trailing brackets and split it.
            values = Parameters._read_list_or_tuple(key)
            parameter = Parameter(key=key, default=values, touched=True)
        except KeyError:
            parameter = Parameter(key=key, default=default_value)
        streamlit.session_state._parameters[key] = parameter

    @staticmethod
    def register_boolean_list_parameter(key: str, default_value: List[bool]):
        """
        Register a boolean list parameter.

        Initialise it from the url query
        string, or as a fallback, with the provided default value if the key is
        not present in the url query string.
        """
        if Parameters._already_registered(key):
            return
        try:
            # Remove the initial and trailing brackets and split it.
            values = Parameters._read_list_or_tuple(key)
            new_values = [util.strtobool(value) for value in values]
            parameter = Parameter(key=key, default=new_values, touched=True)
        except KeyError:
            parameter = Parameter(key=key, default=default_value)
        streamlit.session_state._parameters[key] = parameter

    @staticmethod
    def register_date_parameter(key: str, default_value: datetime.date):
        """
        Register a date parameter.

        Default string conversion produces url query fields of the form
        YYYY-MM-DD, e.g. 2021-11-01. This is satisfactory and corresponds
        to a strftime format of '%Y-%m-%d'.

        For an alternative formatting, override the to_str callback in
        Parameter.
        """
        if Parameters._already_registered(key):
            return
        try:
            parameter = Parameter(
                key=key,
                default=dateutil.parser.parse(Parameters._fetch_url_field(key)).date(),
                touched=True,
            )
        except KeyError:
            parameter = Parameter(key=key, default=default_value)
        streamlit.session_state._parameters[key] = parameter

    @staticmethod
    def register_date_range_parameter(
        key: str, default_value: Tuple[datetime.date, datetime.date]
    ):
        """
        Register a date range type parameter.

        Initialise it from the url query
        string, or as a fallback, with the provided default value if the key is
        not present in the url query string.

        @raises:
            ValueError if conversion from a provided str value in the url field fails
        """
        Parameters._register_range_parameter(
            key, default_value, lambda x: dateutil.parser.parse(x).date()
        )

    @staticmethod
    def register_bool_parameter(key: str, default_value: bool):
        """Register a bool parameter."""
        if Parameters._already_registered(key):
            return
        try:
            s = Parameters._fetch_url_field(key)
            parameter = Parameter(
                key=key, default=s.lower() in ["true", "yes"], touched=True
            )
        except KeyError:
            parameter = Parameter(key=key, default=default_value)
        streamlit.session_state._parameters[key] = parameter

    @staticmethod
    def update_parameter_from_session_state(key: str):
        """Connect widget updates with parameter / url changes.

        Use this method with streamlit widget on_change arguments to
        automatically synchronise widget variable changes to parameter changes.

        .. code-block:: python

            streamlit.sidebar.selectbox(
                label="Choose a Category",
                index=category_indices[parameters.category.value],
                options=["lasagne", "carbonara", "macaroni"],
                key=parameters.category.key,
                on_change=functools.partial(
                    parameters.update_parameter_from_session_state,
                    key=parameters.category.key
                )
            )
        """
        value = getattr(streamlit.session_state, key)
        Parameters.update_parameter(key, value)

    @staticmethod
    def update_parameter(key: str, value: Any):
        """Update a single parameter.

        Args:
            key: parameter to update
            value: the update
        """
        streamlit.session_state._parameters[key].update(new_value=value)

    @staticmethod
    def set_url_fields():
        """Reflect parameters to the url query string."""
        values = {}
        for key, parameter in streamlit.session_state._parameters.items():
            if Parameters.is_set_all() or parameter.touched:
                values[key] = parameter.to_str(parameter.value)
        streamlit.query_params.from_dict(values)

    @staticmethod
    def _already_registered(key: str) -> bool:
        # It will already be registered if you've changed the parameter
        # configuration and reloaded the page, but not the session
        return key in streamlit.session_state._parameters

    @staticmethod
    def _fetch_url_field(key: str) -> str:
        """Fetch a single field from the url query string.

        Args:
            key: parameter name

        Returns:
            the parameter value as a string (prior to any necessary conversion)

        Raises:
            KeyError: if the field does not exist
        """
        return streamlit.query_params[key]
