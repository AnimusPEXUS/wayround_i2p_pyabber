

import org.wayround.utils.factory

import org.wayround.xmpp.xcard_temp


XCARD_FIELDS = [
     'source', 'kind', 'xml', 'fn', 'n', 'nickname', 'photo', 'bday',
     'anniversary', 'gender', 'adr', 'tel', 'email', 'impp', 'lang',
     'tz', 'geo', 'title', 'role', 'logo', 'org', 'member', 'related',
     'categories', 'note', 'prodid', 'rev', 'sound', 'uid',
     'clientpidmap', 'url', 'key', 'fburl', 'caladruri', 'caluri'
     ]


class XCard:

    def __init__(self, **kwargs):

        for i in XCARD_FIELDS:
            set_func = getattr(self, 'set_{}'.format(i))
            set_func(kwargs.get(i))

        return

    @classmethod
    def new_from_vcard_temp(cls, element):
        return

    @classmethod
    def new_from_xcard4(cls, element):
        return

    def gen_vcard_temp(self):
        return

    def gen_xcard4(self):
        return

org.wayround.utils.factory.class_generate_attributes(
    XCard,
    XCARD_FIELDS
    )
