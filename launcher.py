#!/usr/bin/python3

import logging

logging.basicConfig(level='DEBUG')

import org.wayround.pyabber.main

ret = org.wayround.pyabber.main.main(None, None)

exit(ret)
