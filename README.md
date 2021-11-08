# Streamlit Parameters

## About

Weave in interaction...

This is one of streamlit's strengths, but it does create a challenge, namely
"How do I share my application view after I've interacted with it?".

Streamlit provides the machinery that make this possible - input widget configuration,
session state and access to the URL query string so that at the end of the day,
it merely requires copy-pasting an automagically modified URL string to share your view. 

![Demo](resources/demo.gif?raw=true "Demo")

However, wiring these disparate parts together can be a non-trivial exercise.

## Overview

The basic premise is to reduce your view to a few unique parameters that can
both be used to directly reproduce your current view in another user's
streamlit session. 

* Parameters representative of your view typically come from input widgets
* Initial and current values for these are stored in streamlit's session state
* Getting and setting the URL query string can become tricky on page (not session) reloads

This package hides the complexity of interactions with both the session state and
url query string behind a convenient interface that focuses on what is important -
those unique parameters representative of the state of your view.

## Demo

[https://share.streamlit.io/stonier/streamlit_parameters/devel/demo.py](https://share.streamlit.io/stonier/streamlit_parameters/devel/demo.py)

## Usage

1. register a parameter
2. use the parameter default for the widget default
3. add a matching key to a widget
4. add an on_change hook to the widget.
5. set url fields
6. put on your peril-sensitive sunglasses and be froody!

```
parameters = streamlit_parameters.parameters.Parameters()
parameters.register_date_parameter(key="start_date", default_value=seven_days_ago)  # <-- 1
streamlit.sidebar.date_input(
    ...,
    value=parameters.start_date.default,  # <-- 2
    key="start_date",  # <-- 3
    on_change=functools.partial(parameters.update_parameter_from_session_state, key="start_date")  # <-- 4
)
parameters.set_url_fields()  # <-- 5 (sets all fields in one batch call)

streamlit.write("**Start Date**: {parameters.start_date.value}")  # <-- 6
```
