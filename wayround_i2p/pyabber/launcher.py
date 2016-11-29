#!/usr/bin/python3

import logging

logging.basicConfig(level='INFO')

import wayround_i2p.pyabber.main

ret = wayround_i2p.pyabber.main.main(None, None)

exit(ret)
