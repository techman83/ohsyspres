#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='openhab-syslog-parser',
    version='0.1',
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
            'pylint',
            'autopep8',
            'mypy',
        ]
    },
)
