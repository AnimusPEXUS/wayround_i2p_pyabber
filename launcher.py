
import logging

logging.basicConfig(level='DEBUG')

from gi.repository import Gtk

import org.wayround.pyabber.mainwindow

w = org.wayround.pyabber.mainwindow.MainWindow()
w.run()


ret = 0
exit(ret)
