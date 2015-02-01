#!/usr/bin/python3

import logging

logging.basicConfig(level='INFO')

import wayround_org.pyabber.main

ret = wayround_org.pyabber.main.main(None, None)

exit(ret)
