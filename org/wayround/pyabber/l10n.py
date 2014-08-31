
import re

from gi.repository import Gtk


LANG_MODE_RE = re.compile(r'^(?P<mode>\w+)(-(?P<lang>\w+))?$')
LANG_RE = re.compile(r'^(?P<lang>\w+)?$')

MODE_LIST = Gtk.ListStore(str)
MODE_LIST.append(['plain'])
MODE_LIST.append(['xhtml'])
