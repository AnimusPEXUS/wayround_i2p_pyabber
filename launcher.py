
import signal

from gi.repository import Gtk

import org.wayround.pyabber.mainwindow


signal.signal(signal.SIGINT, signal.SIG_DFL)

w = org.wayround.pyabber.mainwindow.MainWindow()
w.window_elements.window.show_all()

Gtk.main()
