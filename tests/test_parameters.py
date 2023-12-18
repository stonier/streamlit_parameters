import datetime

import streamlit as st
from streamlit_parameters.parameters import Parameters
import pytest

sut = "streamlit_parameters.parameters"


@pytest.fixture
def mock_session_state(mocker):
    """pytest fixture that mocks streamlit.session_state"""

    session_state = mocker.patch(sut + ".streamlit.session_state")
    session_state._parameters = {}
    session_state._parameters_set_all = False


@pytest.fixture
def mock_query_params(mocker):
    """pytest fixture that returns a function that mocks query params"""

    def func(key: str, value: str):
        get_query_params = mocker.patch(
            sut + ".streamlit.experimental_get_query_params"
        )
        get_query_params.return_value = {key: [value]}

    return func


@pytest.fixture
def parameters():
    return Parameters()


def test_register_bool_parameter_True_in_url(
    mock_query_params,
    mock_session_state,
    parameters,
):
    mock_query_params(key="foo", value="True")
    parameters.register_bool_parameter(key="foo", default_value=False)
    parameters.register_bool_parameter(key="foo", default_value=False)
    parameter = st.session_state._parameters["foo"]
    assert parameter.default is True
    assert parameter.value is True
    assert repr(parameter) == "Parameter(default=True,value=True,touched=True)"


def test_register_bool_parameter_False_in_url(
    mock_query_params,
    mock_session_state,
    parameters,
):
    mock_query_params(key="foo", value="False")
    parameters.register_bool_parameter(key="foo", default_value=False)
    parameters.register_bool_parameter(key="foo", default_value=False)
    parameter = st.session_state._parameters["foo"]
    assert parameter.default is False
    assert parameter.value is False
    assert repr(parameter) == "Parameter(default=False,value=False,touched=True)"


def test_register_bool_parameter_not_in_url(mock_session_state, parameters):
    parameters.register_bool_parameter(key="foo", default_value=False)
    parameters.register_bool_parameter(key="foo", default_value=False)
    assert parameters.foo.value is False


def test_register_int_parameter(
    mock_query_params,
    mock_session_state,
    parameters,
):
    mock_query_params(key="foo", value="14")
    parameters.register_int_parameter(key="foo", default_value=0)
    parameter = st.session_state._parameters["foo"]
    assert parameter.default == 14
    assert parameter.value == 14
    parameters.foo.update(new_value=4)
    assert parameter.default == 14
    assert parameter.value == 4
    assert parameters.foo.value == 4
    assert repr(parameter) == "Parameter(default=14,value=4,touched=True)"


def test_register_int_parameter_not_in_url(
    mock_session_state,
    parameters,
):
    parameters.register_int_parameter(key="foo", default_value=16)
    parameters.register_int_parameter(key="foo", default_value=16)
    parameter = st.session_state._parameters["foo"]
    assert parameter.default == 16
    assert parameter.value == 16


def test_register_int_range_parameter(
    mock_query_params,
    mock_session_state,
    parameters,
):
    mock_query_params(key="foo", value="(10, 20)")
    parameters.register_int_range_parameter(key="foo", default_value=(0, 0))
    parameters.register_int_range_parameter(key="foo", default_value=(0, 0))
    parameter = st.session_state._parameters["foo"]
    assert parameter.default == (10, 20)
    assert parameter.value == (10, 20)
    assert repr(parameter) == "Parameter(default=(10, 20),value=(10, 20),touched=True)"


def test_register_int_range_parameter_not_in_url(
    mock_session_state,
    parameters,
):
    parameters.register_int_range_parameter(key="foo", default_value=(10, 20))
    parameters.register_int_range_parameter(key="foo", default_value=(10, 20))
    parameter = st.session_state._parameters["foo"]
    assert parameter.default == (10, 20)
    assert parameter.value == (10, 20)


def test_register_float_parameter(
    mock_query_params,
    mock_session_state,
    parameters,
):
    mock_query_params(key="foo", value="2.345")
    parameters.register_float_parameter(key="foo", default_value=0.0)
    parameter = st.session_state._parameters["foo"]
    assert parameter.default == 2.345
    assert parameter.value == 2.345
    assert repr(parameter) == "Parameter(default=2.345,value=2.345,touched=True)"
    parameters.foo.update(new_value=3.456)
    assert parameter.default == 2.345
    assert parameter.value == 3.456
    assert repr(parameter) == "Parameter(default=2.345,value=3.456,touched=True)"


def test_register_float_parameter_not_in_url(
    mock_session_state,
    parameters,
):
    parameters.register_float_parameter(key="foo", default_value=2.345)
    parameters.register_float_parameter(key="foo", default_value=2.345)
    parameter = st.session_state._parameters["foo"]
    assert parameter.default == 2.345
    assert parameter.value == 2.345


def test_register_float_range_parameter(
    mock_query_params,
    mock_session_state,
    parameters,
):
    mock_query_params(key="foo", value="(2.345, 3.456)")
    parameters.register_float_range_parameter(key="foo", default_value=(0.0, 0.0))
    parameters.register_float_range_parameter(key="foo", default_value=(0.0, 0.0))
    parameter = st.session_state._parameters["foo"]
    assert parameter.default == (2.345, 3.456)
    assert parameter.value == (2.345, 3.456)


def test_register_string_parameter(
    mock_query_params,
    mock_session_state,
    parameters,
    mocker,
):
    mock_query_params(key="foo", value="G'day!")
    parameters.register_string_parameter(key="foo", default_value="")
    parameter = st.session_state._parameters["foo"]
    assert parameter.default == "G'day!"
    assert parameter.value == "G'day!"
    assert repr(parameter) == "Parameter(default=G'day!,value=G'day!,touched=True)"
    parameters.foo.update(new_value="Hello")
    assert parameter.default == "G'day!"
    assert parameter.value == "Hello"
    assert repr(parameter) == "Parameter(default=G'day!,value=Hello,touched=True)"
    set_query_params = mocker.patch(sut + ".streamlit.experimental_set_query_params")
    Parameters.set_url_fields()
    set_query_params.assert_called_with(foo="Hello")


def test_register_string_parameter_not_in_url(
    mock_session_state,
    parameters,
):
    parameters.register_string_parameter(key="foo", default_value="G'day!")
    parameters.register_string_parameter(key="foo", default_value="G'day!")
    parameter = st.session_state._parameters["foo"]
    assert parameter.default == "G'day!"
    assert parameter.value == "G'day!"


def test_update_parameter_from_session_state(
    mock_query_params,
    mock_session_state,
    parameters,
):
    mock_query_params(key="foo", value="G'day!")
    parameters.register_string_parameter(key="foo", default_value="")
    parameter = st.session_state._parameters["foo"]
    assert parameter.default == "G'day!"
    assert parameter.value == "G'day!"
    st.session_state.foo = "Hello"
    Parameters.update_parameter_from_session_state("foo")
    assert parameter.default == "G'day!"
    assert parameter.value == "Hello"


def test_register_string_list_parameter(
    mock_query_params,
    mock_session_state,
    parameters,
    mocker,
):
    mock_query_params(key="foo", value="['flying', 'spaghetti', 'monster']")
    parameters.register_string_list_parameter(key="foo", default_value=[])
    parameter = st.session_state._parameters["foo"]
    assert parameter.default == ["flying", "spaghetti", "monster"]
    assert parameter.value == ["flying", "spaghetti", "monster"]
    assert (
        repr(parameter)
        == "Parameter(default=['flying', 'spaghetti', 'monster'],value=['flying', 'spaghetti', 'monster'],touched=True)"
    )
    set_query_params = mocker.patch(sut + ".streamlit.experimental_set_query_params")
    Parameters.set_url_fields()
    set_query_params.assert_called_with(foo="['flying', 'spaghetti', 'monster']")

    # Now update value and make sure new value properly serialized in query params
    parameters.foo.update(new_value=["Hello", "world"])
    Parameters.set_url_fields()
    set_query_params.assert_called_with(foo="['Hello', 'world']")


def test_register_string_list_parameter_not_in_url(
    mock_session_state,
    parameters,
):
    parameters.register_string_list_parameter(key="foo", default_value=["Hello", "world"])
    parameters.register_string_list_parameter(key="foo", default_value=["Hello", "world"])
    parameter = st.session_state._parameters["foo"]
    assert parameter.default == ["Hello", "world"]
    assert parameter.value == ["Hello", "world"]


def test_register_boolean_list_parameter(
    mock_query_params,
    mock_session_state,
    parameters,
):
    mock_query_params(key="foo", value="[true, false]")
    parameters.register_boolean_list_parameter(key="foo", default_value=[])
    parameter = st.session_state._parameters["foo"]
    assert parameter.default == [True, False]
    assert parameter.value == [True, False]


def test_register_boolean_list_parameter_not_in_url(
    mock_session_state,
    parameters,
):
    parameters.register_boolean_list_parameter(key="foo", default_value=[True, False])
    parameters.register_boolean_list_parameter(key="foo", default_value=[True, False])
    parameter = st.session_state._parameters["foo"]
    assert parameter.default == [True, False]
    assert parameter.value == [True, False]


def test_register_date_parameter(
    mock_query_params,
    mock_session_state,
    parameters,
    mocker,
):
    mock_query_params(key="foo", value="2021-11-01")
    parameters.register_date_parameter(key="foo", default_value=None)
    parameter = st.session_state._parameters["foo"]
    assert parameter.default == datetime.date(2021, 11, 1)
    assert parameter.value == datetime.date(2021, 11, 1)
    set_query_params = mocker.patch(sut + ".streamlit.experimental_set_query_params")
    Parameters.set_url_fields()
    set_query_params.assert_called_with(foo="2021-11-01")


def test_register_date_parameter_not_in_url(
    mock_session_state,
    parameters,
):
    parameters.register_date_parameter(key="foo", default_value=datetime.date(2020, 10, 5))
    parameters.register_date_parameter(key="foo", default_value=datetime.date(2020, 10, 5))
    parameter = st.session_state._parameters["foo"]
    assert parameter.default == datetime.date(2020, 10, 5)
    assert parameter.value == datetime.date(2020, 10, 5)


def test_register_date_range_parameter(
    mock_query_params,
    mock_session_state,
    parameters,
    mocker,
):
    mock_query_params(key="foo", value="(2021-11-01, 2021-11-03)")
    parameters.register_date_range_parameter(key="foo", default_value=None)
    parameter = st.session_state._parameters["foo"]
    assert parameter.default == (datetime.date(2021, 11, 1), datetime.date(2021, 11, 3))
    assert parameter.value == (datetime.date(2021, 11, 1), datetime.date(2021, 11, 3))

    # Now update value and make sure new value properly serialized in query params
    set_query_params = mocker.patch(sut + ".streamlit.experimental_set_query_params")
    parameters.foo.update(new_value=(datetime.date(2023, 11, 1), datetime.date(2023, 11, 3)))
    Parameters.set_url_fields()
    set_query_params.assert_called_with(foo='(2023-11-01,2023-11-03)')


def test_as_dict(
    mock_session_state,
    parameters,
):
    default_date_range_value = (datetime.date(2020, 10, 5), datetime.date(2021, 11, 3))
    parameters.register_date_range_parameter(
        key="date_range",
        default_value=default_date_range_value,
    )
    parameters.register_string_parameter(key="msg", default_value="G'day!")
    parameters.register_bool_parameter(key="checked", default_value=True)
    d = Parameters.as_dict()
    assert d["date_range"].default == default_date_range_value
    assert d["msg"].default == "G'day!"
    assert d["checked"].default is True


def test_create_set_all_checkbox(mock_session_state, parameters):
    set_all_checkbox = Parameters.create_set_all_checkbox()
    assert set_all_checkbox is False
    assert Parameters.is_set_all() is False


def test_is_set_all(
    mock_query_params,
    mock_session_state,
    parameters,
):
    mock_query_params(key="foo", value="14")
    assert parameters.is_set_all() is False
