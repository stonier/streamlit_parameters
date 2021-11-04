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
import dateutil.parser
import typing

import streamlit

##############################################################################
# Support
##############################################################################


class Parameter(object):
    """Stores default, current and metadata about a parameter."""

    def __init__(self, key: str, default: typing.Any, touched: bool = False):
        """
        Initialise the parameter with defaults, state and metadata.

        Args:
            key: name of this parameter
            default: initial value
            touched: flagged for export or otherwise
        """
        self.key = key
        self.default: typing.Any = default
        self.value: typing.Any = default
        self.touched: bool = touched
        self.to_str = str

    def update(self, new_value: typing.Any):
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
    """
    What's in a URL? For a streamlit dashboard, not much.

    Once you've interacted
    with a dashboard in a myriad of way, sending someone the url for your
    dashboard doesn't help them very much - they won't see what you are seeing.

    Streamlit uses the URL query string to embed arguments into a URL so that you
    *can* send someone the URL and load widgets into the right configuration so
    they can exactly see what you were seeing. However, doing so is non-trivial.
    It requires non-trivial management and manipulation of streamlit widgets,
    streamlit's session state and the URL query string.

    This class hides the session state machinery and url query string
    manipulation from the user and automatically dictates the priority ordering
    of configuration (url query string > defaults) for parameters used in your
    application. It also provides convenient accessors to those parameters. End
    result, something quite pythonic that avoids the learning curve for
    session state handling in streamlit or url query string manipulation and
    redundant copy/pasta that otherwise results without centralising this machinery
    (e.g. datetime string conversions to and from the url query string).

    **Usage**

     * register a parameter
     * use the parameter default for the widget default
     * add a matching key to a widget
     * add an on_change hook to the widget.
     * set url fields
     * use and be froody!

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

    **Two Modes**

    In general, there are two modes to support - partial or full embedding of parameters
    in the URL query string.

    * partial - only set url query string fields if the parameter has been modified
    * full - set url query string fields for all parameters

    Suppose you have an application with an *end_date* parameter which has a default that
    is programmatically determined on the first time the app is loaded (e.g. datetime.date.today()).
    Today that might return 11-02-2021, tomorrow 11-03-2021.

    Now suppose you want to copy the url for someone today (11-02-2021) and they will receive
    the email in the morning tomorrow. A question arises:

    * Do you want them to **experience** exactly what you experienced? In this case, you
    never overrode that variable and you wish them to have that same experience, i.e. you want
    them to see the latest view of that dashboard too -> you don't want to have the *end_date*
    in the URL string.

    * Do you want them to **see** exactly what you saw? In this case, you need to capture
    a snapshot of every single parameter -> all parameters must go to the URL string.

    This class provides a toggle for the user to choose their mode of operation. It can
    either be accessed directly via the streamlit session state (session_state._parameters_set_all)
    or toggleable via a checkbox, e.g.:

    .. code-block:: python

        parameters = streamlit_parameters.parameters.Parameters()
        with streamlit.sidebar:
            parameters.create_set_all_checkbox()

    *Type Support*

    Support exists for the following types:

    * bool
    * datetime.date
    * int
    * str

    This class handles the problem described in
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
            key="parameters_set_all",
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
        """Register an int parameter.

        Register an int type parameter and initialise it from the url query
        string, or as a fallback, with the provided default value if the key is
        not present in the url query string.

        @raises:
            ValueError if conversion from a provided str value in the url field fails
        """
        if Parameters._already_registered(key):
            return
        try:
            parameter = Parameter(
                key=key,
                default=int(Parameters._fetch_url_field(key)),
                touched=True
            )
        except KeyError:
            parameter = Parameter(key=key, default=default_value)
        streamlit.session_state._parameters[key] = parameter

    @staticmethod
    def register_string_parameter(key: str, default_value: str):
        """
        Register a string parameter.

        Register a string parameter and initialise it from the url query
        string, or as a fallback, with the provided default value if the key is
        not present in the url query string.
        """
        if Parameters._already_registered(key):
            return
        try:
            parameter = Parameter(
                key=key,
                default=Parameters._fetch_url_field(key),
                touched=True
            )
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
                touched=True
            )
        except KeyError:
            parameter = Parameter(key=key, default=default_value)
        streamlit.session_state._parameters[key] = parameter

    @staticmethod
    def register_bool_parameter(key: str, default_value: bool):
        """Register a bool parameter."""
        if Parameters._already_registered(key):
            return
        try:
            s = Parameters._fetch_url_field(key)
            parameter = Parameter(
                key=key,
                default=s.lower() in ["true", "false", "yes", "no"],
                touched=True
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
    def update_parameter(key: str, value: typing.Any):
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
        streamlit.experimental_set_query_params(**values)

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
        # TODO: raise error if multiple values in the query_string exist
        return streamlit.experimental_get_query_params()[key][0]  # always a list, get the first
