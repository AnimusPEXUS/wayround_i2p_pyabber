
import glob

import wayround_org.pyabber.storage
import wayround_org.utils.crypto
import wayround_org.utils.path


def open_pfl(filename, password):
    ret = wayround_org.pyabber.storage.Storage(
        'sqlite:///{}'.format(filename)
        #, connect_args={'check_same_thread': False}
        )
    ret.create()
    return ret


def list_pfl(profiles_path):
    return wayround_org.utils.path.bases(
        glob.glob(wayround_org.utils.path.join(profiles_path, '*.sqlite'))
        )


#def save_pfl(filename, password, data):
#    by = wayround_org.utils.crypto.encrypt_data(data, password)
#    f = open(filename, 'w')
#    f.write(by)
#    f.close()
#    return
