
from gi.repository import Gtk

import wayround_org.xmpp.core


def stanza_error_message(parent, stanza, message=None):

    if not isinstance(stanza, wayround_org.xmpp.core.Stanza):
        raise TypeError("`stanza' must be wayround_org.xmpp.core.Stanza")

    if stanza.is_error():

        stanza_error_error_message(parent, stanza.gen_error(), message)

    return


def stanza_error_error_message(parent, stanza_error, message=None):

    if not isinstance(stanza_error, wayround_org.xmpp.core.StanzaError):
        raise TypeError("`stanza' must be wayround_org.xmpp.core.StanzaError")

    message2 = ''
    if message:
        message2 = '{}\n\n'.format(message)

    d = wayround_org.utils.gtk.MessageDialog(
        parent,
        0,
        Gtk.MessageType.ERROR,
        Gtk.ButtonsType.OK,
        "{}{}".format(
            message2,
            stanza_error.to_text()
            )
        )
    d.run()
    d.destroy()

    return
