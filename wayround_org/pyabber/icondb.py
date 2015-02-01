
import os.path

from gi.repository import GdkPixbuf

import wayround_org.utils.path

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

        for i in ['.svg', '.png']:
            filename = wayround_org.utils.path.join(_dir, name + i)
            if os.path.isfile(filename):
                _icon_db[name] = GdkPixbuf.Pixbuf.new_from_file(
                    filename
                    )
                break

    return _icon_db[name]
