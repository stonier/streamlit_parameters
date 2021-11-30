# Streamlit Parameters

## About

_Weave in interaction..._

This is one of streamlit's strengths, but it does create a challenge, namely
"How do I share my application view after I've interacted with it?".

Streamlit provides the machinery that make this possible - input widget configuration,
session state and access to the URL query string so that at the end of the day,
it merely requires copy-pasting an automagically modified URL string to share your view. 
However, wiring these disparate parts together can be a non-trivial exercise.

This package endeavours to simplify that exercise for the app developer.

![Demo](resources/demo.gif?raw=true "Demo")

## Overview

The basic premise is to reduce your view to a few unique parameters that can
both be used to directly reproduce your current view in another user's
streamlit session. 

* Parameters representative of your view typically come from input widgets
* Initial and current values need to be preserved in the session state to be always available
* Getting and setting the URL query string requires shims for type &#8660; string conversions

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
    on_change=functools.partial(  # <-- 4
        parameters.update_parameter_from_session_state,
        key="start_date"
    )
)
parameters.set_url_fields()  # <-- 5 (sets all fields in one batch call)

streamlit.write("**Start Date**: {parameters.start_date.value}")  # <-- 6
```

## Types

Supported parameter types include:

* `bool`
* `int`
* `float`
* `date`
* `string`
* `pair[int]`
* `pair[float]`
* `pair[date]`
* `list[string]`
* `list[bool]`

Pairs work well with slider widgets that specify ranges of values. Lists with, e.g. multiselects. See the demo
for a reference example.

## Modes

In general, there are two modes to support - partial or full embedding of parameters
in the URL query string.

* partial - only set url query string fields if the parameter has been modified
* full - set url query string fields for all parameters

Suppose you have an application with an *end_date* parameter which has a default that
is programmatically determined on the first time the app is loaded
(e.g. datetime.date.today()). Today that might return `11-02-2021`, tomorrow `11-03-2021`.

Now suppose you want to copy the url for someone today and they will receive
the email in the morning tomorrow. A question arises:

1. Do you want them to **experience** exactly what you experienced? In this case, you
  never overrode that variable and you wish them to have that same experience,
  i.e. you want them to see the latest view of that dashboard too -> you don't want to
  have the *end_date* in the URL string.

2. Do you want them to **see** exactly what you saw? In this case, you need to capture
   a snapshot of every single parameter -> all parameters must go to the URL string.

This class provides a toggle for the user to choose their mode of operation. It can
either be accessed directly via the streamlit session state
(`session_state._parameters_set_all`) or toggleable via a checkbox, e.g.:

```
parameters = streamlit_parameters.parameters.Parameters()
with streamlit.sidebar:
    parameters.create_set_all_checkbox()
```
