
import glob

import wayround_i2p.pyabber.storage
import wayround_i2p.utils.crypto
import wayround_i2p.utils.path


def open_pfl(filename, password):
    ret = wayround_i2p.pyabber.storage.Storage(
        'sqlite:///{}'.format(filename)
        #, connect_args={'check_same_thread': False}
        )
    ret.create()
    return ret


def list_pfl(profiles_path):
    return wayround_i2p.utils.path.bases(
        glob.glob(wayround_i2p.utils.path.join(profiles_path, '*.sqlite'))
        )


#def save_pfl(filename, password, data):
#    by = wayround_i2p.utils.crypto.encrypt_data(data, password)
#    f = open(filename, 'w')
#    f.write(by)
#    f.close()
#    return
