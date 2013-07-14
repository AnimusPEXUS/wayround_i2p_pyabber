
from gi.repository import Gtk
from gi.repository import Gdk

class ProfileWindow:

    def __init__(self, parent, profile=None, typ='new'):

        if not typ in ['new', 'edit', 'open']:
            raise ValueError("`typ' must be in ['new', 'edit', 'open']")

        if typ in ['edit', 'open'] and not isinstance(profile, str):
            raise ValueError("in ['edit', 'open'] mode `profile' must be str")

        win = Gtk.Window()

        title = "Creating New Profile"

        if typ == 'edit':
            title = "Changing Profile `{}' Password".format(profile)

        elif typ == 'open':
            title = "Opening Profile `{}'".format(profile)

        win.set_title(title)

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)

        b.set_margin_top(5)
        b.set_margin_bottom(5)
        b.set_margin_left(5)
        b.set_margin_right(5)

        b2 = Gtk.Grid()

        b2.set_orientation(Gtk.Orientation.VERTICAL)
        b2.set_row_homogeneous(True)
        b2.set_column_homogeneous(True)
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

        b2.attach(Gtk.Label("Login"), 0, 0, 1, 1)
        b2.attach(name_editor, 1, 0, 1, 1)

        b2.attach(Gtk.Label("Password"), 0, 1, 1, 1)
        b2.attach(passwd_editor, 1, 1, 1, 1)

        b2.attach(Gtk.Label("Confirm Password"), 0, 2, 1, 1)
        b2.attach(passwd2_editor, 1, 2, 1, 1)

        b.pack_start(b2, True, True, 0)

        if typ == 'edit':
            name_editor.set_active(False)

        if typ == 'open':
            passwd2_editor.set_active(False)

        bb = Gtk.ButtonBox()

        ok_button = Gtk.Button("Ok")
        cancel_button = Gtk.Button("Cancel")

        bb.pack_start(cancel_button, False, True, 0)
        bb.pack_start(ok_button, False, True, 0)


        b.pack_start(bb, False, True, 0)

        win.add(b)

        win.set_modal(True)
        win.set_transient_for(parent)
        win.set_destroy_with_parent(True)
        win.set_type_hint(Gdk.WindowTypeHint.DIALOG)
#        win.set_attached_to(parent)

        ok_button.connect('clicked', self._ok)
        cancel_button.connect('clicked', self._cancel)

        self.win = win
        self.name_ed = name_editor
        self.passwd_ed = passwd_editor
        self.passwd2_ed = passwd2_editor

        self.result = {
            'button': 'cancel',
            'name': 'name',
            'password': '123',
            'password2': '1234'
            }

    def run(self):

        self.win.show_all()
        Gtk.main()

        return self.result

    def _ok(self, user_data):

        name = self.name_ed.get_text()
        pwd1 = self.passwd_ed.get_text()
        pwd2 = self.passwd2_ed.get_text()

        if name == '':
            d = Gtk.MessageDialog(
                self.win,
                Gtk.DialogFlags.MODAL
                | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Name must be not empty"
                )
            d.run()
            d.destroy()
        else:

            if pwd1 != pwd2:
                d = Gtk.MessageDialog(
                    self.win,
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
                    d = Gtk.MessageDialog(
                        self.win,
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

                    Gtk.main_quit()
                    self.win.destroy()

    def _cancel(self, user_data):

        self.result = {
            'button': 'cancel',
            'name': self.name_ed.get_text(),
            'password': self.passwd_ed.get_text(),
            'password2': self.passwd2_ed.get_text()
            }

        Gtk.main_quit()
        self.win.destroy()
