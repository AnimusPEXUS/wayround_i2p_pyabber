#!/usr/bin/python3

import os.path

from setuptools import setup


setup(
    name='org_wayround_pyabber',
    version='0.1',
    description='XMPP Implementation',
    packages=[
        'org.wayround.pyabber'
        ],
    install_requires=[
        'org_wayround_utils',
        'org_wayround_xmpp'
        ],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX'
        ],
    package_data={
        'org.wayround.pyabber': [
            os.path.join('icons', '*')
            ]
        },
    entry_points={
        'console_scripts': 'pyabber = org.wayround.pyeditor.launcher'
        }
    )
