
from gi.repository import Gtk

import org.wayround.xmpp.core


def stanza_error_message(parent, stanza, message=None):

    if not isinstance(stanza, org.wayround.xmpp.core.Stanza):
        raise TypeError("`stanza' must be org.wayround.xmpp.core.Stanza")

    if stanza.is_error():

        stanza_error_error_message(parent, stanza.gen_error(), message)

    return


def stanza_error_error_message(parent, stanza_error, message=None):

    if not isinstance(stanza_error, org.wayround.xmpp.core.StanzaError):
        raise TypeError("`stanza' must be org.wayround.xmpp.core.StanzaError")

    message2 = ''
    if message:
        message2 = '{}\n\n'.format(message)

    d = org.wayround.utils.gtk.MessageDialog(
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
