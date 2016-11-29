#!/usr/bin/python3

import os.path

from setuptools import setup


setup(
    name='wayround_i2p_pyabber',
    version='0.1.3',
    description='XMPP Client Implementation',
    url='https://github.com/AnimusPEXUS/wayround_i2p_pyabber',
    packages=[
        'wayround_i2p.pyabber'
        ],
    install_requires=[
        'wayround_i2p_utils',
        'wayround_i2p_xmpp'
        ],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX'
        ],
    package_data={
        'wayround_i2p.pyabber': [
            os.path.join('icons', '*')
            ]
        },
    entry_points={
        'console_scripts': 'pyabber = wayround_i2p.pyabber.launcher'
        }
    )
