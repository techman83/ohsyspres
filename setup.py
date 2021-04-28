#!/usr/bin/env python

from setuptools import setup, find_packages
from ohsyspres import __version__

setup(
    name='openhab-syslog-parser',
    version=__version__,
    description='Openhab Syslog Presence Listener',
    author='Leon Wright',
    author_email='techman83@gmail.com',
    packages=find_packages(),
    install_requires=[
        'click',
        'requests',
        'pyparsing',
    ],
    entry_points={
        'console_scripts': [
            'ohsyspres=ohsyspres.cli:run',
        ],
    },
    extras_require={
        'development': [
            'autopep8',
            'pytest',
            'pytest-mypy',
            'mypy',
            'pytest-pylint',
            'pylint',
            'pytest-flake8',
        ],
        'test': [
            'pytest',
            'pytest-mypy',
            'mypy',
            'pytest-pylint',
            'pylint',
            'pytest-flake8',
        ]
    }
)
