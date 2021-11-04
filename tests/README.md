# Tests

Make sure you source the virtual environment.

## Tests Only

```
# run all tests in the current directory
$ pytest

# run all tests with full stdout (-s / --capture=no)
$ pytest -s

# run a test module
$ pytest -s test_hello.py

# run a single test
$ pytest -s test_hello.py::test_gday
```
# Linters Only

```
$ tox -e flake8
```

# All Tests & Linters

To run all tests, as well as linters, switch to the root directory:

```
# Choose one of py37, py38 depending on what version of python you use
$ cd ..
$ tox -e py38
```
