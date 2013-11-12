
import glob

import org.wayround.utils.path
import org.wayround.utils.crypto


def open_pfl(filename, password):
    f = open(filename)
    by = f.read()
    f.close()
    ret = org.wayround.utils.crypto.decrypt_data(
        by, password
        )
    return ret


def list_pfl(profiles_path):
    return org.wayround.utils.path.bases(
        glob.glob(org.wayround.utils.path.join(profiles_path, '*.pfl'))
        )


def save_pfl(filename, password, data):
    by = org.wayround.utils.crypto.encrypt_data(data, password)
    f = open(filename, 'w')
    f.write(by)
    f.close()
    return
