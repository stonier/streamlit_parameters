import streamlit as st
from streamlit_parameters.parameters import Parameters
import pytest


@pytest.fixture
def mock_query_params(mocker):
    """pytest fixture that returns a function that mocks query params"""

    def func(key: str, value: str):
        sut = "streamlit_parameters.parameters"
        session_state = mocker.patch(sut + ".streamlit.session_state")
        session_state._parameters = {"Parameters": Parameters}
        get_query_params = mocker.patch(sut + ".streamlit.experimental_get_query_params")
        get_query_params.return_value = {key: [value]}

    return func


@pytest.fixture
def parameters():
    return Parameters()


def test_register_bool_parameter_True_in_url(mock_query_params, parameters):
    mock_query_params(key="foo", value="True")
    parameters.register_bool_parameter(key="foo", default_value=False)
    parameter = st.session_state._parameters["foo"]
    assert parameter.default is True
    assert parameter.value is True


def test_register_bool_parameter_False_in_url(mock_query_params, parameters):
    mock_query_params(key="foo", value="False")
    parameters.register_bool_parameter(key="foo", default_value=False)
    parameter = st.session_state._parameters["foo"]
    assert parameter.default is False
    assert parameter.value is False
