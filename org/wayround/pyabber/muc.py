
from gi.repository import Gtk

import lxml.etree

import org.wayround.xmpp.muc
import org.wayround.xmpp.xdata
import org.wayround.pyabber.xdata


class MUCConfigWindow:

    def __init__(self, controller, stanza):
        """
        :param org.wayround.xmpp.core.Stanza stanza:
        """

        if not isinstance(stanza, org.wayround.xmpp.core.Stanza):
            raise ValueError(
                "`xdata' must be org.wayround.xmpp.core.Stanza inst"
                )

        self._controller = controller
        self._stanza = stanza

        xdata = None

        error_result = False

        q = stanza.body.find('{http://jabber.org/protocol/muc#owner}query')

        if q == None:
            error_result = "Returned stanza has not query result"

            if stanza.is_error():
                error_result += "\n\nBut instead it is an ERROR stanza:\n\n"
                error_result += org.wayround.xmpp.core.stanza_error_to_text(
                    stanza.get_error()
                    )

        else:
            x = q.find('{jabber:x:data}x')

            if x == None:
                error_result = "Returned stanza has not room configuration form"

                if stanza.is_error():
                    error_result += "\n\nBut instead it is an ERROR stanza:\n\n"
                    error_result += org.wayround.xmpp.core.stanza_error_to_text(
                        stanza.get_error()
                        )

            else:

                xdata = org.wayround.xmpp.xdata.XData.new_from_element(x)

        self._window = Gtk.Window()
        w = self._window

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)
        b.set_margin_left(5)
        b.set_margin_right(5)
        b.set_margin_top(5)
        b.set_margin_bottom(5)
        b.set_spacing(5)

        w.add(b)

        if error_result:
            lab = Gtk.Label(error_result)
            b.pack_start(lab, True, True, 0)
        else:
            xdata_widget_ctl = org.wayround.pyabber.xdata.XDataFormWidgetController(
                xdata
                )

            self._form_controller = xdata_widget_ctl

            f = Gtk.Frame()
            f.set_label("Suggested form")
            s = Gtk.ScrolledWindow()
            f.add(s)
            xdata_widget_ctl_widget = xdata_widget_ctl.get_widget()
            s.add(xdata_widget_ctl_widget)
            xdata_widget_ctl_widget.set_margin_left(5)
            xdata_widget_ctl_widget.set_margin_right(5)
            xdata_widget_ctl_widget.set_margin_top(5)
            xdata_widget_ctl_widget.set_margin_bottom(5)

            b.pack_start(f, True, True, 0)

            bb = Gtk.ButtonBox()
            bb.set_orientation(Gtk.Orientation.HORIZONTAL)

            submit_button = Gtk.Button("Submit")
            submit_button.connect('clicked', self._on_submit_pressed)

            bb.pack_start(submit_button, False, False, 0)

            b.pack_start(bb, False, False, 0)


        w.set_title(
            "Configuring room `{room}' as `{who}'".format(
                room=stanza.jid_from,
                who=stanza.jid_to
                )
            )

        return


    def show(self):

        self._window.show_all()

    def _on_submit_pressed(self, button):

        if not self._form_controller:
            d = org.wayround.utils.gtk.MessageDialog(
                None,
                0,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Form controller not found"
                )
            d.run()
            d.destroy()
        else:

            x_data = self._form_controller.gen_x_data()
            if x_data == None:
                d = org.wayround.utils.gtk.MessageDialog(
                    None,
                    0,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    "Some error while getting x_data"
                    )
                d.run()
                d.destroy()
            else:
                x_data.set_form_type('submit')
                xform_element = x_data.gen_element()

                org.wayround.xmpp.muc.submit_room_configuration(
                    room_bare_jid=self._stanza.jid_from,
                    from_full_jid=self._controller.jid.full(),
                    stanza_processor=self._controller.client.stanza_processor,
                    form_element=xform_element
                    )

                self._window.destroy()

        return

class MUCDestructionDialog:

    def __init__(self, own_jid, room_jid, stanza_processor):

        self._own_jid = own_jid
        self._room_jid = room_jid
        self._stanza_processor = stanza_processor

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)
        b.set_margin_top(5)
        b.set_margin_left(5)
        b.set_margin_right(5)
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
        reason_textarea_frame2.set_margin_left(5)
        reason_textarea_frame2.set_margin_right(5)
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
        alter_jid_entry.set_margin_left(5)
        alter_jid_entry.set_margin_right(5)
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
        window.set_title(
            "Destroying room `{}' being `{}'".format(
                room_jid,
                own_jid
                )
            )

        window.add(b)

        return

    def show(self):
        self._window.show_all()

    def _on_submit_button_clicked(self, button):

        reason = None
        if self._reason_textarea_frame_cb.get_active():
            b = self._reason_textarea.get_buffer()
            reason = b.get_text(b.get_start_iter(), b.get_end_iter(), False)

        alternate_venue_jid = None
        if self._alter_jid_entry_frame_cb.get_active():
            alternate_venue_jid = self._alter_jid_entry.get_text()


        res = org.wayround.xmpp.muc.destroy_room(
            room_bare_jid=self._room_jid,
            from_full_jid=self._own_jid,
            stanza_processor=self._stanza_processor,
            reason=reason,
            alternate_venue_jid=alternate_venue_jid
            )

        if res.is_error():
            org.wayround.pyabber.controller.stanza_error_message(
                self._window, res, message=None
                )
        else:
            d = org.wayround.utils.gtk.MessageDialog(
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

class MUCPopupMenu:

    def __init__(self, controller, muc_jid):

        self._controller = controller
        self._muc_jid = muc_jid

        jid = org.wayround.xmpp.core.JID.new_from_string(muc_jid)

        jid_service = False
        if jid:
            jid_service = jid.user == None

        self._menu = Gtk.Menu()
        menu = self._menu

        new_muc_mi = Gtk.MenuItem("New..")
        configure_muc_mi = Gtk.MenuItem("Configure..")
        delete_muc_mi = Gtk.MenuItem("Delete..")

        new_muc_mi.set_sensitive(jid_service)

        configure_muc_mi.set_sensitive(not jid_service)
        delete_muc_mi.set_sensitive(not jid_service)

        new_muc_mi.connect('activate', self._on_new_muc_mi_activated)
        configure_muc_mi.connect('activate', self._on_configure_muc_mi_activated)
        delete_muc_mi.connect('activate', self._on_delete_muc_mi_activated)

        menu.append(new_muc_mi)
        menu.append(Gtk.SeparatorMenuItem())
        menu.append(configure_muc_mi)
        menu.append(delete_muc_mi)

        self._menu.show_all()
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

    def get_widget(self):
        return self._menu

    def _on_new_muc_mi_activated(self):
        pass

    def _on_configure_muc_mi_activated(self, menuitem):

        res = org.wayround.xmpp.muc.request_room_configuration(
            room_bare_jid=self._muc_jid,
            from_full_jid=self._controller.jid.full(),
            stanza_processor=self._controller.client.stanza_processor
            )

        w = org.wayround.pyabber.muc.MUCConfigWindow(
            self._controller,
            res
            )
        w.show()

    def _on_delete_muc_mi_activated(self, menuitem):

        w = MUCDestructionDialog(
            own_jid=self._controller.jid.full(),
            room_jid=self._muc_jid,
            stanza_processor=self._controller.client.stanza_processor
            )

        w.show()
