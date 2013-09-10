
from gi.repository import GdkPixbuf

import org.wayround.utils.path

_icon_db = {}
_dir = None

def set_dir(path):
    global _dir
    _dir = path

def get(name):

    global _icon_db
    global _dir

    if not _dir:
        raise Exception("Set dir befor calling this function")

    if not name in _icon_db:
        _icon_db[name] = GdkPixbuf.Pixbuf.new_from_file(
            org.wayround.utils.path.join(_dir, name + '.png')
            )

    return _icon_db[name]
