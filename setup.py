#!/usr/bin/python3

import os.path

from setuptools import setup


setup(
    name='wayround_org_pyabber',
    version='0.1.3',
    description='XMPP Client Implementation',
    url='https://github.com/AnimusPEXUS/wayround_org_pyabber',
    packages=[
        'wayround_org.pyabber'
        ],
    install_requires=[
        'wayround_org_utils',
        'wayround_org_xmpp'
        ],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX'
        ],
    package_data={
        'wayround_org.pyabber': [
            os.path.join('icons', '*')
            ]
        },
    entry_points={
        'console_scripts': 'pyabber = wayround_org.pyabber.launcher'
        }
    )
