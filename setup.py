#!/usr/bin/env python

from setuptools import find_packages, setup


install_requires = [
    'streamlit>=1.11,<2'
]

tests_require = ['pytest', 'tox']
extras_require = {
    'test': tests_require,
}

setup(
    name='streamlit_parameters',
    version='0.1.3',
    packages=find_packages(exclude=['tests*', 'docs*']),
    install_requires=install_requires,
    extras_require=extras_require,
    author='Daniel Stonier',
    maintainer='Daniel Stonier <d.stonier@gmail.com>',
    url='http://github.com/stonier/streamlit_parameters',
    zip_safe=True,
    description="Streamlit parameter management for page configuration",
    long_description="Streamlit parameter management across widgets, session state & the url query string.",
    license='BSD',
    test_suite='tests',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'streamlit-demo-parameters = streamlit_parameters.demos.parameters:console_main',
        ],
    },
)
