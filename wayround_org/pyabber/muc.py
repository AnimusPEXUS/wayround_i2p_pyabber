
import json
import sys

from gi.repository import Gtk, Pango

import wayround_org.pyabber.misc
import wayround_org.pyabber.muc_roster_storage
import wayround_org.pyabber.xdata
import wayround_org.utils.error
import wayround_org.utils.gtk
import wayround_org.xmpp.muc
import wayround_org.xmpp.xdata


ROLE_LISTSTORE = Gtk.ListStore(str)
AFFILIATION_LISTSTORE = Gtk.ListStore(str)

for i in wayround_org.xmpp.muc.ROLES:
    ROLE_LISTSTORE.append([i])

for i in wayround_org.xmpp.muc.AFFILIATIONS:
    AFFILIATION_LISTSTORE.append([i])

del i

MODE_LIST = Gtk.ListStore(str)
MODE_LIST.append(['role'])
MODE_LIST.append(['affiliation'])


class MUCMiniIdentityEditorWindow:

    def __init__(self, controller):

        self._controller = controller

        self._iterated_loop = wayround_org.utils.gtk.GtkIteratedLoop()

        window = Gtk.Window()

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)
        b.set_spacing(5)
        b.set_margin_top(5)
        b.set_margin_start(5)
        b.set_margin_end(5)
        b.set_margin_bottom(5)

        room_jid_label = Gtk.Label("Room JID")

        room_jid_entry = Gtk.Entry()
        room_jid_entry.set_hexpand(True)
        room_jid_entry.set_vexpand(False)
        self._room_jid_entry = room_jid_entry

        jid_label = Gtk.Label("JID")

        jid_entry = Gtk.Entry()
        jid_entry.set_hexpand(True)
        jid_entry.set_vexpand(False)
        self._jid_entry = jid_entry

        role_sw_cb = Gtk.ComboBox()
        role_sw_cb.set_hexpand(True)
        role_sw_cb.set_vexpand(False)
        self._role_sw_cb = role_sw_cb
        renderer_text = Gtk.CellRendererText()
        role_sw_cb.pack_start(renderer_text, True)
        role_sw_cb.add_attribute(renderer_text, "text", 0)

        role_sw_cb.set_model(ROLE_LISTSTORE)
        role_sw_cb.set_active(0)

        affiliation_sw_cb = Gtk.ComboBox()
        affiliation_sw_cb.set_hexpand(True)
        affiliation_sw_cb.set_vexpand(False)
        self._affiliation_sw_cb = affiliation_sw_cb
        renderer_text = Gtk.CellRendererText()
        affiliation_sw_cb.pack_start(renderer_text, True)
        affiliation_sw_cb.add_attribute(renderer_text, "text", 0)

        affiliation_sw_cb.set_model(AFFILIATION_LISTSTORE)
        affiliation_sw_cb.set_active(0)

        g = Gtk.Grid()
        g.set_column_spacing(5)
        g.set_row_spacing(5)
        self._g = g

        role_cb = Gtk.CheckButton()
        role_cb.set_label("Role")
        self._role_cb = role_cb

        affiliation_cb = Gtk.CheckButton()
        affiliation_cb.set_label("Affiliation")
        self._affiliation_cb = affiliation_cb

        nick_cb = Gtk.CheckButton()
        self._nick_cb = nick_cb
        nick_cb.set_label("Nick")

        nick_entry = Gtk.Entry()
        nick_entry.set_hexpand(True)
        nick_entry.set_vexpand(False)
        self._nick_entry = nick_entry

        reason_cb = Gtk.CheckButton()
        reason_cb.set_label("Reason")
        self._reason_cb = reason_cb

        reason_tv = Gtk.TextView()
        reason_tv.set_hexpand(True)
        reason_tv.set_vexpand(True)
        reason_tv_sw = Gtk.ScrolledWindow()
        reason_tv_sw.add(reason_tv)
        self._reason_tv = reason_tv

        actor_cb = Gtk.CheckButton()
        actor_cb.set_label("Actor")
        self._actor_cb = actor_cb

        actor_entry = Gtk.Entry()
        actor_entry.set_hexpand(True)
        actor_entry.set_vexpand(False)
        self._actor_entry = actor_entry

        lst = [
            (room_jid_label, room_jid_entry),
            (jid_label, jid_entry),
            (nick_cb, nick_entry),
            (role_cb, role_sw_cb),
            (affiliation_cb, affiliation_sw_cb),
            (reason_cb, reason_tv_sw),
            (actor_cb, actor_entry)
            ]

        for i in range(len(lst)):
            for j in range(len(lst[i])):
                g.attach(lst[i][j], j, i, 1, 1)

        bb = Gtk.ButtonBox()
        bb.set_spacing(5)
        bb.set_orientation(Gtk.Orientation.HORIZONTAL)

        request_button = Gtk.Button("Request")
        request_button.connect('clicked', self._on_request_clicked)

        cancel_button = Gtk.Button("Cancel")
        cancel_button.connect('clicked', self._on_cancel_clicked)

        bb.pack_start(request_button, False, False, 0)
        bb.pack_start(cancel_button, False, False, 0)

        b.pack_start(g, True, True, 0)
        b.pack_start(bb, False, False, 0)

        window.add(b)
        window.connect('destroy', self._on_destroy)

        self._window = window
        return

    def run(self, room_jid, target_jid, editing_preset):

        self._room_jid_entry.set_text(room_jid)
        if target_jid:
            self._jid_entry.set_text(target_jid)

        aff = editing_preset.get_affiliation()
        for i in range(len(AFFILIATION_LISTSTORE)):
            if AFFILIATION_LISTSTORE[i][0] == aff:
                self._affiliation_sw_cb.set_active(i)
                break

        role = editing_preset.get_role()
        for i in range(len(ROLE_LISTSTORE)):
            if ROLE_LISTSTORE[i][0] == role:
                self._role_sw_cb.set_active(i)
                break

        self._nick_entry.set_text(editing_preset.get_nick()),

        self.show()

        self._iterated_loop.wait()

        return

    def show(self):
        self._window.show_all()

    def destroy(self):
        self._window.destroy()
        self._iterated_loop.stop()

    def _on_destroy(self, window):
        self.destroy()

    def _on_cancel_clicked(self, button):
        self.destroy()

    def _on_request_clicked(self, button):
        items = []

        actor = None
        if self._actor_cb.get_active():
            actor = self._actor_entry.get_text()
            if actor != None:
                actor = wayround_org.xmpp.muc.Actor(actor)

        affiliation = None
        if self._affiliation_cb.get_active():
            affiliation = \
                AFFILIATION_LISTSTORE[self._affiliation_sw_cb.get_active()][0]

        role = None
        if self._role_cb.get_active():
            role = \
                ROLE_LISTSTORE[self._role_sw_cb.get_active()][0]

        nick = None
        if self._nick_cb.get_active():
            nick = self._nick_entry.get_text()

        reason = None
        if self._reason_cb.get_active():
            buff = self._reason_tv.get_buffer()
            reason = buff.get_text(
                buff.get_start_iter(),
                buff.get_end_iter(),
                False
                )

        items.append(
            wayround_org.xmpp.muc.Item(
                affiliation=affiliation,
                jid=self._jid_entry.get_text(),
                nick=nick,
                role=role,
                reason=reason,
                actor=actor
                )
            )

        query = wayround_org.xmpp.muc.Query(
            xmlns='#admin',
            item=items
            )

        stanza = wayround_org.xmpp.core.Stanza('iq')

        stanza.set_from_jid(str(self._controller.jid))
        stanza.set_to_jid(self._room_jid_entry.get_text())
        stanza.set_typ('set')

        stanza.get_objects().append(query)

        res = self._controller.client.stanza_processor.send(stanza, wait=None)
        if isinstance(res, wayround_org.xmpp.core.Stanza):
            if res.is_error():
                wayround_org.pyabber.misc.stanza_error_message(
                    self._window,
                    res,
                    "Server Returned Error"
                    )
            else:
                d = wayround_org.utils.gtk.MessageDialog(
                    self._window,
                    0,
                    Gtk.MessageType.INFO,
                    Gtk.ButtonsType.OK,
                    "Processed. No Error Returned From Server."
                    )
                d.run()
                d.destroy()
        else:
            if res == False:
                d = wayround_org.utils.gtk.MessageDialog(
                    self._window,
                    0,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    "Timeout"
                    )
                d.run()
                d.destroy()

        return


class MUCVoiceRequestWindow:

    def __init__(self, controller):

        self._controller = controller

        self._iterated_loop = wayround_org.utils.gtk.GtkIteratedLoop()

        window = Gtk.Window()

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)
        b.set_spacing(5)
        b.set_margin_top(5)
        b.set_margin_start(5)
        b.set_margin_end(5)
        b.set_margin_bottom(5)

        target_entry = Gtk.Entry()
        self._target_entry = target_entry

        mode_sw_cb = Gtk.ComboBox()
        self._role_sw_cb = mode_sw_cb
        renderer_text = Gtk.CellRendererText()
        mode_sw_cb.pack_start(renderer_text, True)
        mode_sw_cb.add_attribute(renderer_text, "text", 0)

        mode_sw_cb.set_model(MODE_LIST)
        mode_sw_cb.set_active(0)

        value_sw_cb = Gtk.ComboBox()
        self._value_sw_cb = value_sw_cb
        renderer_text = Gtk.CellRendererText()
        value_sw_cb.pack_start(renderer_text, True)
        value_sw_cb.add_attribute(renderer_text, "text", 0)

        value_sw_cb.set_model(ROLE_LISTSTORE)

        for i in range(len(ROLE_LISTSTORE)):
            if ROLE_LISTSTORE[i][0] == 'participant':
                value_sw_cb.set_active(i)
                break

        g = Gtk.Grid()
        self._g = g
        g.set_column_spacing(5)

        l = Gtk.Label("Mode")
        l.set_hexpand(True)
        l.set_halign(Gtk.Align.START)
        g.attach(l, 0, 0, 1, 1)
        g.attach(mode_sw_cb, 1, 0, 1, 1)

        l = Gtk.Label("Value")
        l.set_hexpand(True)
        l.set_halign(Gtk.Align.START)
        g.attach(l, 0, 1, 1, 1)
        g.attach(value_sw_cb, 1, 1, 1, 1)

        bb = Gtk.ButtonBox()
        bb.set_spacing(5)
        bb.set_orientation(Gtk.Orientation.HORIZONTAL)

        request_button = Gtk.Button("Request")
        request_button.connect('clicked', self._on_request_clicked)

        cancel_button = Gtk.Button("Close")
        cancel_button.connect('clicked', self._on_cancel_clicked)

        mode_sw_cb.connect('changed', self._on_mode_sw_cb_changed)

        bb.pack_start(request_button, False, False, 0)
        bb.pack_start(cancel_button, False, False, 0)

        use_standard_cb = Gtk.CheckButton()
        use_standard_cb.set_label("Use Standard")
        use_standard_cb.connect('toggled', self._on_use_standard_cb_toggled)
        use_standard_cb.set_active(True)
        self._use_standard_cb = use_standard_cb

        b.pack_start(target_entry, False, False, 0)
        b.pack_start(use_standard_cb, False, False, 0)
        b.pack_start(g, True, True, 0)
        b.pack_start(bb, False, False, 0)

        window.add(b)
        window.connect('destroy', self._on_destroy)

        self._window = window

        return

    def run(self, room_jid):

        self._window.set_title(
            "Requesting voice in room `{}'".format(room_jid)
            )
        self._target_entry.set_text(room_jid)

        self.show()

        self._iterated_loop.wait()

        return

    def show(self):
        self._window.show_all()

    def destroy(self):
        self._window.destroy()
        self._iterated_loop.stop()

    def _on_destroy(self, window):
        self.destroy()

    def _on_cancel_clicked(self, button):
        self.destroy()

    def _on_request_clicked(self, button):

        mode = 'role'
        value = 'participant'

        if self._use_standard_cb.get_active() == False:

            mode = MODE_LIST[self._mode_sw_cb.get_active()][0]

            if mode == 'affiliation':
                value = \
                    AFFILIATION_LISTSTORE[self._value_sw_cb.get_active()][0]
            elif mode == 'role':
                value = ROLE_LISTSTORE[self._value_sw_cb.get_active()][0]

        fields = [
            wayround_org.xmpp.xdata.XDataField(
                var='FORM_TYPE',
                values=[
                    wayround_org.xmpp.xdata.XDataValue(
                        'http://jabber.org/protocol/muc#request'
                        )
                    ]
                ),
            wayround_org.xmpp.xdata.XDataField(
                var='muc#{}'.format(mode),
                typ='text-single',
                label="Requested {}".format(mode),
                values=[
                    wayround_org.xmpp.xdata.XDataValue(
                        value
                        )
                    ]
                )
            ]

        xdata = wayround_org.xmpp.xdata.XData(
            typ='submit',
            fields=fields
            )

        stanza = wayround_org.xmpp.core.Stanza(tag='message')
        stanza.set_from_jid(str(self._controller.jid))
        stanza.set_to_jid(self._target_entry.get_text())
        stanza.set_objects([xdata])

        self._controller.client.stanza_processor.send(
            stanza,
            wait=False
            )

        d = wayround_org.utils.gtk.MessageDialog(
            self._window,
            0,
            Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK,
            """\
Request is sent

Successful it or not - can't be determined.
Wait for administrator or server reactions.
"""
            )
        d.run()
        d.destroy()

        return

    def _on_mode_sw_cb_changed(self, cb):

        mode = MODE_LIST[self._mode_sw_cb.get_active()][0]

        if mode == 'affiliation':
            self._value_sw_cb.set_model(AFFILIATION_LISTSTORE)
        elif mode == 'role':
            self._value_sw_cb.set_model(ROLE_LISTSTORE)

        self._value_sw_cb.set_active(0)

        return

    def _on_use_standard_cb_toggled(self, cb):
        self._g.set_sensitive(not cb.get_active())


class MUCJoinDialog:
    """
    Dialog for explicit MUC opening
    """
    # TODO: do we really need this dialog?

    def __init__(self, controller):

        self._controller = controller

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)
        b.set_margin_top(5)
        b.set_margin_start(5)
        b.set_margin_end(5)
        b.set_margin_bottom(5)
        b.set_spacing(5)

        bb2 = Gtk.ButtonBox()
        bb2.set_orientation(Gtk.Orientation.HORIZONTAL)

        entry = Gtk.Entry()
        self._entry = entry

        e_f = Gtk.Frame()
        e_f.set_label("Complete MUC Room JID (resource is for nickname)")
        e_f.add(entry)

        entry.set_margin_top(5)
        entry.set_margin_start(5)
        entry.set_margin_end(5)
        entry.set_margin_bottom(5)

        b.pack_start(e_f, True, True, 0)
        b.pack_start(bb2, False, False, 0)

        join_button = Gtk.Button("Join")
        cancel_button = Gtk.Button("Cancel")

        bb2.pack_start(join_button, False, False, 0)

        bb2.pack_start(cancel_button, False, False, 0)

        window = Gtk.Window()
        window.connect('destroy', self._on_destroy)
        self._window = window

        self._iterated_loop = wayround_org.utils.gtk.GtkIteratedLoop()

        window.add(b)

        cancel_button.connect('clicked', self._on_cancel_clicked)
        join_button.connect('clicked', self._on_join_clicked)

        return

    def run(self, room_jid):

        self._window.set_title(
            "Joining room `{}'".format(room_jid)
            )
        self._entry.set_text(room_jid + '/')

        self.show()

        self._iterated_loop.wait()

        return

    def show(self):
        self._window.show_all()

    def destroy(self):
        self._window.destroy()
        self._iterated_loop.stop()

    def _on_destroy(self, window):
        self.destroy()

    def _on_cancel_clicked(self, button):
        self.destroy()

    def _on_join_clicked(self, button):
        raise Exception("Rework required")
        w = self._controller.get_chat_window()
        o = wayround_org.xmpp.core.JID.new_from_str(self._entry.get_text())

        if not o.is_full():
            d = wayround_org.utils.gtk.MessageDialog(
                self._window,
                0,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Please supply full JID (including resource)!"
                )
            d.run()
            d.destroy()
        else:

            w.chat_pager.add_groupchat(o)
            self._controller.show_presence_control_window(to_=str(o))
            self.destroy()

        return


class MUCJIDEntryDialog:

    def __init__(self):

        window = Gtk.Window()

        self._window = window

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)
        b.set_margin_start(5)
        b.set_margin_top(5)
        b.set_margin_end(5)
        b.set_margin_bottom(5)
        b.set_spacing(5)

        hb = Gtk.Box()
        hb.set_orientation(Gtk.Orientation.HORIZONTAL)
        hb.set_spacing(5)

        l = Gtk.Label("JID")
        e = Gtk.Entry()

        self._entry = e

        hb.pack_start(l, False, False, 0)
        hb.pack_start(e, True, True, 0)

        ok_button = Gtk.Button("Continue")
        ok_button.connect('clicked', self._on_ok_button_clicked)

        bb = Gtk.ButtonBox()
        bb.set_orientation(Gtk.Orientation.HORIZONTAL)

        bb.pack_start(ok_button, False, False, 0)

        b.pack_start(hb, True, True, 0)
        b.pack_start(bb, False, False, 0)

        window.add(b)

        self._iteration_loop = wayround_org.utils.gtk.GtkIteratedLoop()

        self._result = None

        window.connect('destroy', self._on_destroy)

    def run(self, jid, title):

        if not isinstance(jid, str):
            raise ValueError("`jid' must be str")

        if not isinstance(title, str):
            raise ValueError("`title' must be str")

        self.show()

        self._window.set_title(title)
        self._entry.set_text(jid)

        self._iteration_loop.wait()
        return self._result

    def show(self):
        self._window.show_all()

    def _on_destroy(self, window):
        self.destroy()

    def destroy(self):
        self._window.hide()
        self._window.destroy()
        self._iteration_loop.stop()

    def _on_ok_button_clicked(self, button):
        self._result = self._entry.get_text()
        self._iteration_loop.stop()
        self._window.destroy()


class MUCConfigWindow:

    def __init__(self, controller):

        if not isinstance(
            controller,
            wayround_org.pyabber.ccc.ClientConnectionController
            ):
            raise ValueError(
                "`controller' must be wayround_org.xmpp.client.XMPPC2SClient"
                )

        self._controller = controller

        self._own_jid = self._controller.jid
        self._client = self._controller.client

        self._window = Gtk.Window()
        w = self._window

        b = Gtk.Box()
        self._b = b
        b.set_orientation(Gtk.Orientation.VERTICAL)
        b.set_margin_start(5)
        b.set_margin_end(5)
        b.set_margin_top(5)
        b.set_margin_bottom(5)
        b.set_spacing(5)

        w.add(b)
        w.connect('destroy', self._on_destroy)

        self._iterated_loop = wayround_org.utils.gtk.GtkIteratedLoop()

        return

    def run(self, stanza):

        if not isinstance(stanza, wayround_org.xmpp.core.Stanza):
            raise ValueError(
                "`xdata' must be wayround_org.xmpp.core.Stanza inst"
                )

        b = self._b

        self._stanza = stanza

        xdata = None

        error_result = False

        q = stanza.get_element().find(
            '{http://jabber.org/protocol/muc#owner}query'
            )

        if q == None:
            error_result = "Returned stanza has not query result"

            if stanza.is_error():
                error_result += "\n\nBut instead it is an ERROR stanza:\n\n"
                error_result += stanza.gen_error().gen_text()

        else:

            query = wayround_org.xmpp.muc.Query.new_from_element(q)
            x = query.get_xdata()

            if x == None:
                error_result = \
                    "Returned stanza has not room configuration form"

                if stanza.is_error():
                    error_result += \
                        "\n\nBut instead it is an ERROR stanza:\n\n"
                    error_result += stanza.gen_error().gen_text()

            else:

                xdata = x

        if error_result:
            lab = Gtk.Label(error_result)
            b.pack_start(lab, True, True, 0)
        else:
            xdata_widget_ctl = (
                wayround_org.pyabber.xdata.XDataFormWidget(
                    self._controller,
                    xdata,
                    stanza
                    )
                )

            self._form_controller = xdata_widget_ctl

            f = Gtk.Frame()
            f.set_label("Suggested form")
            s = Gtk.ScrolledWindow()
            f.add(s)
            xdata_widget_ctl_widget = xdata_widget_ctl.get_widget()
            s.add(xdata_widget_ctl_widget)
            xdata_widget_ctl_widget.set_margin_start(5)
            xdata_widget_ctl_widget.set_margin_end(5)
            xdata_widget_ctl_widget.set_margin_top(5)
            xdata_widget_ctl_widget.set_margin_bottom(5)

            b.pack_start(f, True, True, 0)

            bb = Gtk.ButtonBox()
            bb.set_orientation(Gtk.Orientation.HORIZONTAL)

            submit_button = Gtk.Button("Submit")
            submit_button.connect('clicked', self._on_submit_pressed)

            bb.pack_start(submit_button, False, False, 0)

            b.pack_start(bb, False, False, 0)

        self._window.set_title(
            "Configuring room `{room}' as `{who}'".format(
                room=stanza.get_from_jid(),
                who=stanza.get_to_jid()
                )
            )

        self.show()

        self._iterated_loop.wait()

        return

    def show(self):
        self._window.show_all()

    def destroy(self):
        self._window.hide()
        self._window.destroy()
        self._iterated_loop.stop()

    def _on_destroy(self, window):
        if self._form_controller:
            self._form_controller.destroy()
        self.destroy()

    def _on_submit_pressed(self, button):

        if not self._form_controller:
            d = wayround_org.utils.gtk.MessageDialog(
                self._window,
                0,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Form controller not found"
                )
            d.run()
            d.destroy()
        else:

            x_data = self._form_controller.gen_stanza_subobject()
            if x_data == None:
                d = wayround_org.utils.gtk.MessageDialog(
                    self._window,
                    0,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    "Some error while getting x_data"
                    )
                d.run()
                d.destroy()
            else:
                x_data.set_typ('submit')

                wayround_org.xmpp.muc.submit_room_configuration(
                    room_bare_jid=self._stanza.get_from_jid(),
                    from_full_jid=self._own_jid.full(),
                    stanza_processor=self._client.stanza_processor,
                    x_data=x_data
                    )

                self._window.destroy()

        return


class MUCDestructionDialog:

    def __init__(self, controller):

        if not isinstance(
            controller,
            wayround_org.pyabber.ccc.ClientConnectionController
            ):
            raise ValueError(
                "`controller' must be wayround_org.xmpp.client.XMPPC2SClient"
                )

        self._controller = controller

        self._own_jid = self._controller.jid
        self._stanza_processor = self._controller.client.stanza_processor
        self._room_jid = None

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)
        b.set_margin_top(5)
        b.set_margin_start(5)
        b.set_margin_end(5)
        b.set_margin_bottom(5)
        b.set_spacing(5)

        reason_textarea_frame = Gtk.Frame()

        reason_textarea_frame_cb = Gtk.CheckButton("Include Reason")
        self._reason_textarea_frame_cb = reason_textarea_frame_cb
        reason_textarea_frame.set_label_widget(reason_textarea_frame_cb)

        reason_textarea = Gtk.TextView()
        self._reason_textarea = reason_textarea
        reason_textarea_sw = Gtk.ScrolledWindow()
        reason_textarea_sw.add(reason_textarea)
        reason_textarea_frame2 = Gtk.Frame()
        reason_textarea_frame2.set_margin_top(5)
        reason_textarea_frame2.set_margin_start(5)
        reason_textarea_frame2.set_margin_end(5)
        reason_textarea_frame2.set_margin_bottom(5)
        reason_textarea_frame2.add(reason_textarea_sw)
        reason_textarea_frame.add(reason_textarea_frame2)

        alter_jid_entry_frame = Gtk.Frame()
        alter_jid_entry_frame_cb = Gtk.CheckButton("Alternate Venue")
        self._alter_jid_entry_frame_cb = alter_jid_entry_frame_cb
        alter_jid_entry_frame.set_label_widget(alter_jid_entry_frame_cb)
        alter_jid_entry = Gtk.Entry()
        self._alter_jid_entry = alter_jid_entry
        alter_jid_entry.set_margin_top(5)
        alter_jid_entry.set_margin_start(5)
        alter_jid_entry.set_margin_end(5)
        alter_jid_entry.set_margin_bottom(5)
        alter_jid_entry_frame.add(alter_jid_entry)

        bb = Gtk.ButtonBox()
        bb.set_orientation(Gtk.Orientation.HORIZONTAL)

        submit_button = Gtk.Button("Submit")
        submit_button.connect('clicked', self._on_submit_button_clicked)

        bb.pack_start(submit_button, False, False, 0)

        b.pack_start(reason_textarea_frame, True, True, 0)
        b.pack_start(alter_jid_entry_frame, False, False, 0)
        b.pack_start(bb, False, False, 0)

        self._window = Gtk.Window()
        window = self._window

        window.add(b)
        window.connect('destroy', self._on_destroy)

        self._iterated_loop = wayround_org.utils.gtk.GtkIteratedLoop()

        return

    def run(self, room_jid):
        self._window.set_title(
            "Destroying room `{}' being `{}'".format(
                room_jid,
                self._own_jid
                )
            )
        self._room_jid = room_jid
        self.show()
        self._iterated_loop.wait()

    def show(self):
        self._window.show_all()

    def destroy(self):
        self._window.hide()
        self._window.destroy()
        self._iterated_loop.stop()

    def _on_destroy(self, window):
        self.destroy()

    def _on_submit_button_clicked(self, button):

        reason = None
        if self._reason_textarea_frame_cb.get_active():
            b = self._reason_textarea.get_buffer()
            reason = b.get_text(b.get_start_iter(), b.get_end_iter(), False)

        alternate_venue_jid = None
        if self._alter_jid_entry_frame_cb.get_active():
            alternate_venue_jid = self._alter_jid_entry.get_text()

        res = wayround_org.xmpp.muc.destroy_room(
            room_bare_jid=self._room_jid,
            from_full_jid=str(self._own_jid),
            stanza_processor=self._stanza_processor,
            reason=reason,
            alternate_venue_jid=alternate_venue_jid
            )

        if isinstance(res, wayround_org.xmpp.core.Stanza):
            if res.is_error():
                wayround_org.pyabber.misc.stanza_error_message(
                    self._window, res, message=None
                    )
            else:
                d = wayround_org.utils.gtk.MessageDialog(
                    self._window,
                    0,
                    Gtk.MessageType.INFO,
                    Gtk.ButtonsType.OK,
                    "Room `{}' destroyed".format(
                        self._room_jid
                        )
                    )
                d.run()
                d.destroy()

        self._window.hide()
        self._window.destroy()

        return


class MUCPopupMenu:

    def __init__(self, controller):

        if not isinstance(
            controller,
            wayround_org.pyabber.ccc.ClientConnectionController
            ):
            raise ValueError(
                "`controller' must be wayround_org.xmpp.client.XMPPC2SClient"
                )

        self._controller = controller
        self._stanza_processor = controller.client.stanza_processor

        self._own_jid = self._controller.jid
        self._client = self._controller.client

        menu = Gtk.Menu()

        join_muc_mi = Gtk.MenuItem("Join/[Change Nick]..")
        voice_request_muc_mi = Gtk.MenuItem("Request Voice..")

        new_muc_inst_mi = Gtk.MenuItem("New Instantly..")
        new_muc_conf_mi = Gtk.MenuItem("New Configuring..")

        configure_muc_mi = Gtk.MenuItem("Configure..")
        discover_nick_mi = Gtk.MenuItem("Discover Own Nickname..")
        register_nick_mi = Gtk.MenuItem("(un)Registration..")

        edit_owner_list_muc_mi = Gtk.MenuItem("Owner list..")
        edit_admin_list_muc_mi = Gtk.MenuItem("Admin List..")
        edit_mod_list_muc_mi = Gtk.MenuItem("Moderator List..")
        edit_member_list_muc_mi = Gtk.MenuItem("Member List..")
        edit_voice_list_muc_mi = Gtk.MenuItem("Voice List..")
        edit_ban_list_muc_mi = Gtk.MenuItem("Ban List..")

        destroy_muc_mi = Gtk.MenuItem("Destroy..")

        join_muc_mi.connect('activate', self._on_join_muc_mi_activated)

        new_muc_inst_mi.connect('activate', self._on_new_muc_inst_mi_activated)
        new_muc_conf_mi.connect('activate', self._on_new_muc_conf_mi_activated)
        configure_muc_mi.connect(
            'activate',
            self._on_configure_muc_mi_activated
            )
        discover_nick_mi.connect(
            'activate',
            self._on_discover_nick_mi_activated
            )
        register_nick_mi.connect(
            'activate',
            self._on_register_nick_mi_activated
            )

        edit_owner_list_muc_mi.connect(
            'activate', self._on_list_edit_mi_activated, 'owner'
            )
        edit_admin_list_muc_mi.connect(
            'activate', self._on_list_edit_mi_activated, 'admin'
            )
        edit_mod_list_muc_mi.connect(
            'activate', self._on_list_edit_mi_activated, 'moderator'
            )
        edit_member_list_muc_mi.connect(
            'activate', self._on_list_edit_mi_activated, 'member'
            )
        edit_ban_list_muc_mi.connect(
            'activate', self._on_list_edit_mi_activated, 'ban'
            )
        edit_voice_list_muc_mi.connect(
            'activate', self._on_list_edit_mi_activated, 'voice'
            )
        voice_request_muc_mi.connect(
            'activate', self._on_voice_request_muc_mi_activated
            )

        destroy_muc_mi.connect('activate', self._on_delete_muc_mi_activated)

        menu.append(join_muc_mi)
        menu.append(voice_request_muc_mi)
        menu.append(Gtk.SeparatorMenuItem())
        menu.append(new_muc_inst_mi)
        menu.append(new_muc_conf_mi)
        menu.append(Gtk.SeparatorMenuItem())
        menu.append(configure_muc_mi)
        menu.append(discover_nick_mi)
        menu.append(register_nick_mi)
        menu.append(Gtk.SeparatorMenuItem())
        menu.append(edit_owner_list_muc_mi)
        menu.append(edit_admin_list_muc_mi)
        menu.append(edit_mod_list_muc_mi)
        menu.append(edit_member_list_muc_mi)
        menu.append(edit_ban_list_muc_mi)
        menu.append(edit_voice_list_muc_mi)
        menu.append(Gtk.SeparatorMenuItem())
        menu.append(destroy_muc_mi)

        menu.show_all()

        self._menu = menu
        self._new_muc_conf_mi = new_muc_conf_mi
        self._new_muc_inst_mi = new_muc_inst_mi

        return

    def set(self, muc_jid):

        if not isinstance(muc_jid, str):
            raise ValueError("`muc_jid' must be str")

        self._muc_jid = muc_jid

        jid = wayround_org.xmpp.core.JID.new_from_string(muc_jid)

        jid_service = False
        if jid:
            jid_service = jid.user == None

        self._jid_service = jid_service
        self._new_muc_inst_mi.set_sensitive(jid_service)
        self._new_muc_conf_mi.set_sensitive(jid_service)

        return

    def show(self):

        self._menu.popup(
            None,
            None,
            None,
            None,
            0,
            Gtk.get_current_event_time()
            )

        return

    def destroy(self):
        self._menu.destroy()

    def get_widget(self):
        return self._menu

    def _on_new_muc_inst_mi_activated(self, menuitem):

        jid = self._controller.show_muc_jid_entry_dialog(
            '@{}'.format(self._muc_jid),
            "Instantly Creating New Room on `{}' as `{}'".format(
                self._muc_jid,
                self._own_jid.full()
                )
            )

        if jid != None:

            res = wayround_org.xmpp.muc.create_room_instantly(
                room_bare_jid=jid,
                from_full_jid=self._own_jid.full(),
                stanza_processor=self._client.stanza_processor
                )

            if isinstance(res, wayround_org.xmpp.core.Stanza):
                if res.is_error():
                    wayround_org.pyabber.misc.stanza_error_message(
                        parent=None,
                        stanza=res,
                        message="Can't create room `{}' instantly".format(jid)
                        )

        return

    def _on_new_muc_conf_mi_activated(self, menuitem):
        jid = self._controller.show_muc_jid_entry_dialog(
            '@{}'.format(self._muc_jid),
            "Configuring New Room on `{}' as `{}'".format(
                self._muc_jid,
                self._own_jid.full()
                )
            )

        if jid != None:

            res = wayround_org.xmpp.muc.request_room_configuration(
                room_bare_jid=jid,
                from_full_jid=self._own_jid.full(),
                stanza_processor=self._client.stanza_processor
                )

            self._controller.show_muc_config_window(res)

        return

    def _on_configure_muc_mi_activated(self, menuitem):

        jid = self._muc_jid
        if self._jid_service:
            jid = self._controller.show_muc_jid_entry_dialog(
                '@{}'.format(self._muc_jid),
                "Input JID to configure on `{}' as `{}'".format(
                    self._muc_jid,
                    self._own_jid.full()
                    )
                )

        if jid != None:

            res = wayround_org.xmpp.muc.request_room_configuration(
                room_bare_jid=jid,
                from_full_jid=self._own_jid.full(),
                stanza_processor=self._client.stanza_processor
                )

            self._controller.show_muc_config_window(res)

        return

    def _on_discover_nick_mi_activated(self, menuitem):

        jid = self._muc_jid
        if self._jid_service:
            jid = self._controller.show_muc_jid_entry_dialog(
                '@{}'.format(self._muc_jid),
                "Input room JID to discover own jid on `{}' as `{}'".format(
                    self._muc_jid,
                    self._own_jid.full()
                    )
                )

        if jid != None:

            res = wayround_org.xmpp.muc.discover_room_nickname(
                room_bare_jid=jid,
                from_full_jid=self._own_jid.full(),
                stanza_processor=self._stanza_processor
                )

            if isinstance(res, wayround_org.xmpp.core.Stanza):
                if res.is_error():
                    wayround_org.pyabber.misc.stanza_error_message(
                        parent=None,
                        stanza=res,
                        message="Can't get Your registered Nickname"
                        )
                else:
                    q = res.get_element().find(
                        "{http://jabber.org/protocol/disco#info}"
                        "query[@node='x-roomuser-item']"
                        )
                    if q != None:
                        q = wayround_org.xmpp.disco.IQDisco.new_from_element(q)

                        items = q.get_identity()
                        nicks = []
                        nicks_l = len(nicks)
                        for i in items:
                            nicks.append('   {}'.format(i.get_name()))

                        nicks.sort()
                        nicks = '\n'.join(nicks)

                        d = wayround_org.utils.gtk.MessageDialog(
                            None,
                            0,
                            Gtk.MessageType.INFO,
                            Gtk.ButtonsType.OK,
                            "You'r have {} nickname(s)"
                            " in room `{}':\n{}".format(
                                nicks_l,
                                jid,
                                nicks
                                )
                            )
                        d.run()
                        d.destroy()
                    else:
                        d = wayround_org.utils.gtk.MessageDialog(
                            None,
                            0,
                            Gtk.MessageType.ERROR,
                            Gtk.ButtonsType.OK,
                            "Result does not contains query response"
                            )
                        d.run()
                        d.destroy()
            else:
                d = wayround_org.utils.gtk.MessageDialog(
                    None,
                    0,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    "Timeout"
                    )
                d.run()
                d.destroy()

        return

    def _on_register_nick_mi_activated(self, menuitem):
        self._controller.show_registration_window(
            target_jid_obj=self._muc_jid,
            from_jid_obj=self._controller.jid
            )

        return

    def _on_delete_muc_mi_activated(self, menuitem):

        jid = self._muc_jid
        if self._jid_service:
            jid = self._controller.show_muc_jid_entry_dialog(
                '@{}'.format(self._muc_jid),
                "Input JID to delete on `{}' as `{}'".format(
                    self._muc_jid,
                    self._own_jid.full()
                    )
                )

        if jid != None:

            self._controller.show_muc_destruction_dialog(
                room_jid=jid
                )

        return

    def _on_list_edit_mi_activated(self, menuitem, mode):

        if not mode in [
            'owner', 'admin', 'member', 'ban', 'moderator', 'voice'
            ]:
            raise ValueError(
"`mode' must be in ['owner', 'admin', 'member', 'ban', 'moderator', 'voice']"
                )

        jid = self._muc_jid
        if self._jid_service:
            jid = self._controller.show_muc_jid_entry_dialog(
                '@{}'.format(self._muc_jid),
                "Input JID of room on `{}' to edit `{}' list as `{}'".format(
                    self._muc_jid,
                    mode,
                    self._own_jid.full()
                    )
                )

        if jid != None:

            self._controller.show_muc_identity_editor_window(
                target_jid=jid,
                mode=mode
                )

        return

    def _on_join_muc_mi_activated(self, mi):
        self._controller.show_presence_control_window(self._muc_jid)

    def _on_voice_request_muc_mi_activated(self, mi):
        self._controller.show_muc_voice_request_window(self._muc_jid)


class MUCIdentityEditorWindow:

    def __init__(self, controller):

        if not isinstance(
            controller,
            wayround_org.pyabber.ccc.ClientConnectionController
            ):
            raise ValueError(
                "`controller' must be wayround_org.xmpp.client.XMPPC2SClient"
                )

        self._controller = controller

        self._stanza_processor = self._controller.client.stanza_processor
        self._own_jid = self._controller.jid

        g_box_grid_jid_label = Gtk.Label("Room JID")
        g_box_grid_jid_entry = Gtk.Entry()
        self._g_box_grid_jid_entry = g_box_grid_jid_entry
        g_box_grid_jid_entry.connect(
            'key-release-event', self._on_target_jid_edited
            )

        g_box_grid_jid_box = Gtk.Box()
        g_box_grid_jid_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        g_box_grid_jid_box.set_spacing(5)
        g_box_grid_jid_box.pack_start(g_box_grid_jid_label, False, False, 0)
        g_box_grid_jid_box.pack_start(g_box_grid_jid_entry, True, True, 0)

        g_box_grid_query_edit_box = Gtk.Box()
        g_box_grid_query_edit_box.set_orientation(Gtk.Orientation.VERTICAL)
        g_box_grid_query_edit_box.set_margin_start(5)
        g_box_grid_query_edit_box.set_margin_top(5)
        g_box_grid_query_edit_box.set_margin_bottom(5)
        g_box_grid_query_edit_box.set_margin_end(5)
        g_box_grid_query_edit_box.set_spacing(5)

        g_box_query_bb_sw = Gtk.ScrolledWindow()
        g_box_query_bb = Gtk.ButtonBox()
        g_box_query_bb.set_orientation(Gtk.Orientation.HORIZONTAL)
        g_box_query_bb.set_spacing(2)
#        g_box_query_bb.set_homogeneous(False)
        g_box_query_bb_sw.add(g_box_query_bb)

        for i in [
            'owner', 'admin', 'moderator', 'member', 'voice', 'ban'
            ]:
            button = Gtk.Button(i.capitalize())
            button.connect('clicked', self._on_query_fast_mod_clicked, i)
            g_box_query_bb.pack_start(button, False, False, 0)

        g_box_grid_query_edit = Gtk.TextView()
        self._g_box_grid_query_edit = g_box_grid_query_edit

        g_box_grid_query_edit_scrolled = Gtk.ScrolledWindow()
        g_box_grid_query_edit_scrolled.add(g_box_grid_query_edit)

        g_box_grid_query_edit_box.pack_start(
            g_box_query_bb_sw, False, False, 0
            )

        g_box_grid_query_edit_box.pack_start(
            g_box_grid_query_edit_scrolled, True, True, 0
            )

        g_box_grid_query_edit_frame = Gtk.Frame()
        g_box_grid_query_edit_frame.add(g_box_grid_query_edit_box)
        g_box_grid_query_edit_frame.set_label("Query (JSON)")

        g_box_execute_query_button = Gtk.Button("Execute")
        g_box_execute_query_button.connect(
            'clicked',
            self._on_g_box_execute_query_button_clicked
            )

        g_box_grid = Gtk.Box()
        g_box_grid.set_orientation(Gtk.Orientation.VERTICAL)
        g_box_grid.set_margin_start(5)
        g_box_grid.set_margin_top(5)
        g_box_grid.set_margin_bottom(5)
        g_box_grid.set_margin_end(5)
        g_box_grid.set_spacing(5)
        g_box_grid.pack_start(g_box_grid_jid_box, False, False, 0)
        g_box_grid.pack_start(g_box_grid_query_edit_frame, True, True, 0)
        g_box_grid.pack_start(g_box_execute_query_button, False, False, 0)

        g_text_view_sw = Gtk.ScrolledWindow()
        g_text_view = Gtk.TextView()
        self._g_text_view = g_text_view

        g_tree_view_f = Gtk.Frame()
        g_tree_view_f.set_label("Query Result")
        g_tree_view_f.add(g_text_view_sw)

        g_text_view_sw.add(g_text_view)
        g_text_view_sw.set_margin_start(5)
        g_text_view_sw.set_margin_top(5)
        g_text_view_sw.set_margin_bottom(5)
        g_text_view_sw.set_margin_end(5)

        g_box_grid_f = Gtk.Frame()
        g_box_grid_f.set_label("Query")
        g_box_grid_f.add(g_box_grid)
        g_paned = Gtk.Paned()
        g_paned.set_orientation(Gtk.Orientation.VERTICAL)
        g_paned.add1(g_box_grid_f)
        g_paned.add2(g_tree_view_f)

        window = Gtk.Window()
        self._window = window

        g_box = Gtk.Box()
        g_box.set_orientation(Gtk.Orientation.VERTICAL)

        g_box.pack_start(g_paned, True, True, 0)

        example_expander = Gtk.Expander()
        example_expander.set_label("Examples")
        example_label = Gtk.Label(
            """\
List of dictionaries. Add to dictionaties only changes (delta)
(read XEP-0045 if want to know more)
[
{
 "jid":"wiccarocks@shakespeare.lit", # bare jid
 "affiliation": "admin", # standard affiliations
                         # admin, member, none, outcast, owner
 "role": "moderator", # standard roles (for online users)
                      # moderator, none, participant, visitor,
 "nick": "Some nickname",
 "actor": "crone1@shakespeare.lit",  # bare jid
 "reason": "text\ntext"
},
...
]
"""
            )
        font_desc = Pango.FontDescription.from_string("Clean 9")
#        font_desc.set_family('Clean')
#        font_desc.set_style(Pango.Style.NORMAL)
#        font_desc.set_variant(Pango.Variant.NORMAL)
#        font_desc.set_weight(Pango.Weight.NORMAL)
#        font_desc.set_stretch(Pango.Stretch.NORMAL)
#        font_desc.set_size(9)

        example_label.set_selectable(True)
        example_label.override_font(font_desc)
        example_expander.add(example_label)
        example_expander.set_expanded(False)

        set_text = Gtk.TextView()
        self._set_text = set_text
        set_text_sw = Gtk.ScrolledWindow()
        set_text_sw.add(set_text)

        set_bb = Gtk.ButtonBox()
        set_bb.set_orientation(Gtk.Orientation.HORIZONTAL)

        execute_set_query = Gtk.Button("Execute")
        execute_set_query.connect(
            'clicked',
            self._execute_set_query_button_clicked
            )
        set_bb.pack_start(execute_set_query, False, False, 0)

        set_b = Gtk.Box()
        set_b.set_orientation(Gtk.Orientation.VERTICAL)
        set_b.set_margin_start(5)
        set_b.set_margin_top(5)
        set_b.set_margin_bottom(5)
        set_b.set_margin_end(5)
        set_b.set_spacing(5)
        set_b.pack_start(set_text_sw, True, True, 0)
        set_b.pack_start(set_bb, False, False, 0)
        set_b.pack_start(example_expander, False, False, 0)

        set_b_f = Gtk.Frame()
        set_b_f.set_label("Editing Query")
        set_b_f.add(set_b)

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)
        b.set_margin_start(5)
        b.set_margin_top(5)
        b.set_margin_bottom(5)
        b.set_margin_end(5)
        b.set_spacing(5)

        paned = Gtk.Paned()
        paned.add1(g_box)
        paned.add2(set_b_f)

        b.pack_start(paned, True, True, 0)

        window.add(b)
        window.connect('destroy', self._on_destroy)

        self._iterated_loop = wayround_org.utils.gtk.GtkIteratedLoop()

        return

    def run(self, target_jid, mode=None, editing_preset=None):
        self.show()

        self._g_box_grid_jid_entry.set_text(target_jid)
        self._target_jid = target_jid
        if mode != None:
            self._on_query_fast_mod_clicked(None, mode)

        if editing_preset != None:

            data = []
            for i in [editing_preset]:
                data.append(
                    {
                     'jid': wayround_org.xmpp.core.JID.new_from_str(
                        i.get_jid()
                        ).bare(),
                     'affiliation': i.get_affiliation(),
                     'role': i.get_role(),
                     'nick': i.get_nick(),
                     'reason': '',
                     'actor': ''
                     }
                    )

            b = self._set_text.get_buffer()
            b.set_text(
                json.dumps(data, sort_keys=True,
                           indent=4, separators=(',', ': '))
                )

        self._iterated_loop.wait()

    def show(self):
        self._window.show_all()

    def destroy(self):
        self._window.hide()
        self._window.destroy()
        self._iterated_loop.stop()

    def _on_destroy(self, window):
        self.destroy()

    def _on_g_box_execute_query_button_clicked(self, button):

        b = self._g_box_grid_query_edit.get_buffer()
        text = b.get_text(b.get_start_iter(), b.get_end_iter(), False)
        try:
            data = json.loads(text)
        except:
            d = wayround_org.utils.gtk.MessageDialog(
                self._window,
                0,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Error Parsing JSON Text:\n\n{}".format(
                    wayround_org.utils.error.return_exception_info(
                        sys.exc_info()
                        )
                    )
                )
            d.run()
            d.destroy()
        else:
            b.set_text(
                json.dumps(data, sort_keys=True,
                           indent=4, separators=(',', ': '))
                )
            if not wayround_org.utils.types.struct_check(
                data,
                {'t': list, '.': {'t': dict}}
                ):
                d = wayround_org.utils.gtk.MessageDialog(
                    self._window,
                    0,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    "JSON data must be list of dicts"
                    )
                d.run()
                d.destroy()
            else:
                items = []
                error = False
                for i in data:
                    try:
                        items.append(
                            wayround_org.xmpp.muc.Item(
                                affiliation=i.get('affiliation'),
                                jid=i.get('jid'),
                                nick=i.get('affiliation'),
                                role=i.get('role'),
                                )
                            )
                    except:
                        error = True
                        d = wayround_org.utils.gtk.MessageDialog(
                            self._window,
                            0,
                            Gtk.MessageType.ERROR,
                            Gtk.ButtonsType.OK,
                            "Error Parsing JSON Text:\n\n{}".format(
                                wayround_org.utils.error.return_exception_info(
                                    sys.exc_info()
                                    )
                                )
                            )
                        d.run()
                        d.destroy()

                if not error:

                    query = wayround_org.xmpp.muc.Query(
                        xmlns='#admin',
                        item=items
                        )

                    stanza = wayround_org.xmpp.core.Stanza('iq')

                    stanza.set_from_jid(str(self._own_jid))
                    stanza.set_to_jid(self._target_jid)
                    stanza.set_typ('get')

                    stanza.get_objects().append(query)

                    res = self._stanza_processor.send(stanza, wait=None)

                    if isinstance(res, wayround_org.xmpp.core.Stanza):
                        if res.is_error():
                            wayround_org.pyabber.misc.stanza_error_message(
                                self._window,
                                res,
                                "Server Returned Error"
                                )

                        muc_q = res.get_element().find(
                            '{http://jabber.org/protocol/muc#admin}query'
                            )
                        if muc_q is None:
                            d = wayround_org.utils.gtk.MessageDialog(
                                self._window,
                                0,
                                Gtk.MessageType.ERROR,
                                Gtk.ButtonsType.OK,
                                "Response Contains No Query Result"
                                )
                            d.run()
                            d.destroy()
                        else:
                            q = wayround_org.xmpp.muc.Query.new_from_element(
                                muc_q
                                )
                            data = []
                            for i in q.get_item():
                                data.append(
                                    {
                                     'jid': i.get_jid(),
                                     'affiliation': i.get_affiliation(),
                                     'role': i.get_role(),
                                     'nick': i.get_nick()
                                     }
                                    )

                            b = self._g_text_view.get_buffer()
                            b.set_text(
                                json.dumps(data, sort_keys=True,
                                           indent=4, separators=(',', ': '))
                                )
                    else:
                        if res == False:
                            d = wayround_org.utils.gtk.MessageDialog(
                                self._window,
                                0,
                                Gtk.MessageType.ERROR,
                                Gtk.ButtonsType.OK,
                                "Timeout"
                                )
                            d.run()
                            d.destroy()

        return

    def _on_target_jid_edited(self, entry, event):
        self._target_jid = self._g_box_grid_jid_entry.get_text()
        self._window.set_title(
            "Editing privileges of `{}' as `{}'".format(
                self._target_jid,
                self._own_jid
                )
            )

        return

    def _on_query_fast_mod_clicked(self, button, mode):

        affiliation = None
        role = None

        if mode in ['owner', 'admin', 'member']:
            affiliation = mode
        elif mode == 'ban':
            affiliation = 'outcast'
        elif mode == 'moderator':
            role = 'moderator'
        elif mode == 'voice':
            role = 'participant'
        else:
            raise Exception("DNA Error")

        data = [{'affiliation': affiliation, 'role': role}]

        b = self._g_box_grid_query_edit.get_buffer()
        b.set_text(
            json.dumps(
                data,
                sort_keys=True,
                indent=4,
                separators=(',', ': ')
                )
            )

        return

    def _execute_set_query_button_clicked(self, button):

        b = self._set_text.get_buffer()
        text = b.get_text(b.get_start_iter(), b.get_end_iter(), False)
        try:
            data = json.loads(text)
        except:
            d = wayround_org.utils.gtk.MessageDialog(
                self._window,
                0,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Error Parsing JSON Text:\n\n{}".format(
                    wayround_org.utils.error.return_exception_info(
                        sys.exc_info()
                        )
                    )
                )
            d.run()
            d.destroy()
        else:
            b.set_text(
                json.dumps(data, sort_keys=True,
                           indent=4, separators=(',', ': '))
                )
            if not wayround_org.utils.types.struct_check(
                data,
                {'t': list, '.': {'t': dict}}
                ):
                d = wayround_org.utils.gtk.MessageDialog(
                    self._window,
                    0,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    "JSON data must be list of dicts"
                    )
                d.run()
                d.destroy()
            else:
                items = []
                error = False
                for i in data:
                    try:
                        actor = i.get('actor')
                        if actor != None:
                            actor = wayround_org.xmpp.muc.Actor(actor)
                        items.append(
                            wayround_org.xmpp.muc.Item(
                                affiliation=i.get('affiliation'),
                                jid=i.get('jid'),
                                nick=i.get('nick'),
                                role=i.get('role'),
                                reason=i.get('reason'),
                                actor=actor
                                )
                            )
                    except:
                        error = True
                        d = wayround_org.utils.gtk.MessageDialog(
                            self._window,
                            0,
                            Gtk.MessageType.ERROR,
                            Gtk.ButtonsType.OK,
                            "Error Parsing JSON Text:\n\n{}".format(
                                wayround_org.utils.error.return_exception_info(
                                    sys.exc_info()
                                    )
                                )
                            )
                        d.run()
                        d.destroy()

                if not error:

                    query = wayround_org.xmpp.muc.Query(
                        xmlns='#admin',
                        item=items
                        )

                    stanza = wayround_org.xmpp.core.Stanza('iq')

                    stanza.set_from_jid(str(self._own_jid))
                    stanza.set_to_jid(self._target_jid)
                    stanza.set_typ('set')

                    stanza.get_objects().append(query)

                    res = self._stanza_processor.send(stanza, wait=None)
                    if isinstance(res, wayround_org.xmpp.core.Stanza):
                        if res.is_error():
                            wayround_org.pyabber.misc.stanza_error_message(
                                self._window,
                                res,
                                "Server Returned Error"
                                )
                        else:
                            d = wayround_org.utils.gtk.MessageDialog(
                                self._window,
                                0,
                                Gtk.MessageType.INFO,
                                Gtk.ButtonsType.OK,
                                "Processed. No Error Returned From Server."
                                )
                            d.run()
                            d.destroy()

        return
