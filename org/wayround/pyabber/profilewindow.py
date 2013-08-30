
import threading

from gi.repository import Gtk
from gi.repository import Gdk

import org.wayround.utils.gtk

class Dumb: pass

class ProfileWindow:

    def __init__(self, parent, profile=None, typ='new'):

        self.iteration_loop = org.wayround.utils.gtk.GtkIteratedLoop()

        if not typ in ['new', 'edit', 'open']:
            raise ValueError("`typ' must be in ['new', 'edit', 'open']")

        if typ in ['edit', 'open'] and not isinstance(profile, str):
            raise ValueError("in ['edit', 'open'] mode `profile' must be str")

        self.typ = typ

        self.window_elements = Dumb()

        win = Gtk.Window()

        title = "Creating New Profile"

        if typ == 'edit':
            title = "Changing Profile `{}' Password".format(profile)

        elif typ == 'open':
            title = "Opening Profile `{}'".format(profile)

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)

        b.set_margin_top(5)
        b.set_margin_bottom(5)
        b.set_margin_left(5)
        b.set_margin_right(5)

        b2 = Gtk.Grid()

        b2.set_orientation(Gtk.Orientation.VERTICAL)
        b2.set_row_homogeneous(True)
#        b2.set_column_homogeneous(True)
        b2.set_column_spacing(5)
        b2.set_margin_bottom(5)

        name_editor = Gtk.Entry()
        passwd_editor = Gtk.Entry()
        passwd2_editor = Gtk.Entry()

        if typ == 'new':
            profile = ''

        name_editor.set_text(profile)
        passwd_editor.set_visibility(False)
        passwd2_editor.set_visibility(False)

        l = Gtk.Label("Login")
        b2.attach(l, 0, 0, 1, 1)
        b2.attach(name_editor, 1, 0, 1, 1)
        l.set_alignment(0, 0.5)
        name_editor.set_halign(Gtk.Align.FILL)
        name_editor.set_hexpand(True)

        l = Gtk.Label("Password")
        b2.attach(l, 0, 1, 1, 1)
        b2.attach(passwd_editor, 1, 1, 1, 1)
        l.set_alignment(0, 0.5)
        passwd_editor.set_halign(Gtk.Align.FILL)
        passwd_editor.set_hexpand(True)

        l = Gtk.Label("Confirm Password")
        b2.attach(l, 0, 2, 1, 1)
        b2.attach(passwd2_editor, 1, 2, 1, 1)
        l.set_alignment(0, 0.5)
        passwd2_editor.set_halign(Gtk.Align.FILL)
        passwd2_editor.set_hexpand(True)

        b.pack_start(b2, True, True, 0)

        if typ == 'edit':
            name_editor.set_sensitive(False)

        if typ == 'open':
            name_editor.set_sensitive(False)
            passwd2_editor.set_sensitive(False)

        bb = Gtk.ButtonBox()

        ok_button = Gtk.Button("Ok")
        cancel_button = Gtk.Button("Cancel")

        bb.pack_start(cancel_button, False, True, 0)
        bb.pack_start(ok_button, False, True, 0)


        b.pack_start(bb, False, True, 0)

        win.add(b)

        win.set_title(title)
        win.set_modal(True)
        win.set_transient_for(parent)
        win.set_destroy_with_parent(True)
        win.set_type_hint(Gdk.WindowTypeHint.DIALOG)

        ok_button.set_can_default(True)

        win.set_default(ok_button)

        name_editor.set_activates_default(True)
        passwd_editor.set_activates_default(True)
        passwd2_editor.set_activates_default(True)

        self.window_elements.win = win
        self.window_elements.ok_button = ok_button
        self.window_elements.cancel_button = cancel_button
        self.window_elements.name_editor = name_editor
        self.window_elements.passwd_editor = passwd_editor
        self.window_elements.passwd2_editor = passwd2_editor

        ok_button.connect('clicked', self._ok)
        cancel_button.connect('clicked', self._cancel)

        win.connect('destroy', self._window_destroy)


        self.result = {
            'button': 'cancel',
            'name': 'name',
            'password': '123',
            'password2': '1234'
            }

    def run(self):

        self.window_elements.win.show_all()

        self.iteration_loop.wait()

        return self.result

    def _ok(self, button):

        name = self.window_elements.name_editor.get_text()
        pwd1 = self.window_elements.passwd_editor.get_text()
        pwd2 = self.window_elements.passwd2_editor.get_text()

        if name == '':
            d = org.wayround.utils.gtk.MessageDialog(
                self.window_elements.win,
                Gtk.DialogFlags.MODAL
                | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Name must be not empty"
                )
            d.run()
            d.destroy()
        else:

            if self.typ in ['new', 'edit'] and pwd1 != pwd2:
                d = org.wayround.utils.gtk.MessageDialog(
                    self.window_elements.win,
                    Gtk.DialogFlags.MODAL
                    | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    "Password confirmation mismatch"
                    )
                d.run()
                d.destroy()
            else:

                if pwd1 == '':
                    d = org.wayround.utils.gtk.MessageDialog(
                        self.window_elements.win,
                        Gtk.DialogFlags.MODAL
                        | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                        Gtk.MessageType.ERROR,
                        Gtk.ButtonsType.OK,
                        "Password must be not empty"
                        )
                    d.run()
                    d.destroy()
                else:

                    self.result = {
                        'button': 'ok',
                        'name': name,
                        'password': pwd1,
                        'password2': pwd2
                        }

                    self.window_elements.win.destroy()

    def _cancel(self, button):

        self.result = {
            'button': 'cancel',
            'name': self.window_elements.name_editor.get_text(),
            'password': self.window_elements.passwd_editor.get_text(),
            'password2': self.window_elements.passwd2_editor.get_text()
            }

        self.window_elements.win.destroy()

    def _window_destroy(self, window):

        self.iteration_loop.stop()
