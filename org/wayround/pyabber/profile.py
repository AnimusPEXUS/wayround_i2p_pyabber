
import glob

import org.wayround.pyabber.storage
import org.wayround.utils.crypto
import org.wayround.utils.path


def open_pfl(filename, password):
    ret = org.wayround.pyabber.storage.Storage(
        'sqlite:///{}'.format(filename),
        connect_args={'check_same_thread': False},
        echo=True
        )
    ret.create()
    return ret


def list_pfl(profiles_path):
    return org.wayround.utils.path.bases(
        glob.glob(org.wayround.utils.path.join(profiles_path, '*.sqlite'))
        )


#def save_pfl(filename, password, data):
#    by = org.wayround.utils.crypto.encrypt_data(data, password)
#    f = open(filename, 'w')
#    f.write(by)
#    f.close()
#    return
