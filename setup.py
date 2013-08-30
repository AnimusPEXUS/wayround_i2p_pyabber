#!/usr/bin/python3

#import subprocess

from distutils.core import setup
#from distutils.extension import Extension
#from Cython.Distutils import build_ext


setup(
    name='org_wayround_pyabber',
    description='XMPP Implementation',
    packages=[
        'org.wayround.pyabber'
        ],
#    ext_modules=[
#        Extension(
#            "org.wayround.pyabber.cell_rendering_routines",
#            ["org/wayround/pyabber/cell_rendering_routines.pyx"]
#            )
#        ],
#    cmdclass={'build_ext': build_ext},
    package_data={'org.wayround.pyabber': ['*.pxd', '*.pyx', '*.c']},
    )
