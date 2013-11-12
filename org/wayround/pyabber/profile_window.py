
import os
import sys

from gi.repository import Gtk, Gdk, GdkPixbuf

import org.wayround.utils.gtk

import org.wayround.pyabber.profile


class ProfileMgrWindow:

    def __init__(self, main):

        b = Gtk.Box()
        b.set_orientation(Gtk.Orientation.VERTICAL)
        b.set_margin_top(5)
        b.set_margin_bottom(5)
        b.set_margin_left(5)
        b.set_margin_right(5)

        b2 = Gtk.Box()
        b2.set_orientation(Gtk.Orientation.HORIZONTAL)

        b3 = Gtk.Box()
        b3.set_orientation(Gtk.Orientation.VERTICAL)
        b3.set_spacing(5)

        bb1 = Gtk.ButtonBox()
        bb1.set_orientation(Gtk.Orientation.VERTICAL)
        bb1.set_spacing(5)
        bb1.set_homogeneous(True)
        bb1.set_margin_left(5)
        bb1.set_margin_right(5)
        bb1.set_margin_top(5)
        bb1.set_margin_bottom(5)

        but1 = Gtk.Button("Open")
        but3 = Gtk.Button("New...")
        but4 = Gtk.Button("Change Password...")
        but6 = Gtk.Button("Delete")
        but7 = Gtk.Button("Refresh List")

        but1.connect('clicked', self._on_activate_clicked)
        but3.connect('clicked', self._on_new_clicked)
        but6.connect('clicked', self._on_delete_clicked)
        but7.connect('clicked', self._on_refresh_list_clicked)

        bb1.pack_start(but1, False, True, 0)
        bb1.pack_start(but3, False, True, 0)
        bb1.pack_start(but4, False, True, 0)
        bb1.pack_start(but6, False, True, 0)
        bb1.pack_start(but7, False, True, 0)

        ff1 = Gtk.Frame()
        ff1.add(bb1)
        ff1.set_label("Actions")

        icon_view = Gtk.IconView()

        ff = Gtk.Frame()
        ff.add(icon_view)
        ff.set_margin_right(5)
        ff.set_label("Available Profiles")
        b2.pack_start(ff, True, True, 0)
        b2.pack_start(b3, False, True, 0)

        b3.pack_start(ff1, False, True, 0)

        profile_info_label = Gtk.Label("(None)")

        ff2 = Gtk.Frame()
        ff2.add(profile_info_label)
        ff2.set_label("Current Profile")

        profile_info_label.set_margin_left(5)
        profile_info_label.set_margin_right(5)
        profile_info_label.set_margin_top(5)
        profile_info_label.set_margin_bottom(5)
        profile_info_label.set_line_wrap(True)
        profile_info_label.set_max_width_chars(10)

        b3.pack_start(ff2, True, True, 0)

        b.pack_start(b2, True, True, 0)

        window = Gtk.Window()

        window.add(b)

        window.connect('destroy', self._on_destroy)
        icon_view.connect(
            'item-activated', self._on_iconview_item_activated
            )

        self._iterated_loop = org.wayround.utils.gtk.GtkIteratedLoop()
        self._main = main
        self._profile_icon_view = icon_view
        self._profile_info_label = profile_info_label
        self._result = None
        self._window = window

        return

    def run(self):
        self.show()
        self._iterated_loop.wait()
        return self._result

    def show(self):
        self._window.show_all()

    def destroy(self):
        self._iterated_loop.stop()
        self._window.destroy()

    def refresh_list(self):

        selected = None

        items = self._profile_icon_view.get_selected_items()

        if len(items) != 0:

            selected = items[0]

        profiles = org.wayround.pyabber.profile.list_pfl(
            self._main.profiles_path
            )

        profiles.sort()

        tree = Gtk.ListStore(str, GdkPixbuf.Pixbuf)

        for i in profiles:

            tree.append([i, org.wayround.pyabber.icondb.get('profile')])

        self._profile_icon_view.set_model(tree)
        self._profile_icon_view.set_text_column(0)
        self._profile_icon_view.set_pixbuf_column(1)

        if selected:

            self._profile_icon_view.select_path(selected)

    def _on_destroy(self, window):
        self._window.hide()
        self._iterated_loop.stop()

    def _on_new_clicked(self, button):

        w = ProfileWindow(
            self._window, typ='new'
            )
        r = w.run()

        if r['button'] == 'ok':

            self._main.save(r['name'], {}, r['password'])

            self.refresh_list()

    def _on_save_clicked(self, button):
        if self._main.profile:
            self._main.profile.save()

    def _on_delete_clicked(self, button):

        items = self._profile_icon_view.get_selected_items()

        i_len = len(items)

        if i_len == 0:
            d = org.wayround.utils.gtk.MessageDialog(
                self._window,
                Gtk.DialogFlags.MODAL
                | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Profile not selected"
                )
            d.run()
            d.destroy()

        else:

            name = self._profile_icon_view.get_model()[items[0]][0][:-4]

            d = org.wayround.utils.gtk.MessageDialog(
                self._window,
                Gtk.DialogFlags.MODAL
                | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                Gtk.MessageType.QUESTION,
                Gtk.ButtonsType.YES_NO,
                "Do You really wish to delete profile `{}'?".format(name)
                )
            r = d.run()
            d.destroy()

            if r == Gtk.ResponseType.YES:

                profile = org.wayround.utils.path.join(
                    self._main.profiles_path, '{}.pfl'.format(name)
                    )

                try:
                    os.unlink(profile)
                except:
                    d = org.wayround.utils.gtk.MessageDialog(
                        self._window,
                        Gtk.DialogFlags.MODAL
                        | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                        Gtk.MessageType.ERROR,
                        Gtk.ButtonsType.OK,
                        "Error while removing profile_data:\n\n{}".format(
                            org.wayround.utils.error.return_exception_info(
                                sys.exc_info()
                                )
                            )
                        )
                    d.run()
                    d.destroy()

            self.refresh_list()

    def _on_deactivate_clicked(self, button):
        self._main.unset_profile()

    def _on_activate_clicked(self, button):

        items = self._profile_icon_view.get_selected_items()

        i_len = len(items)

        if i_len == 0:
            d = org.wayround.utils.gtk.MessageDialog(
                self._window,
                Gtk.DialogFlags.MODAL
                | Gtk.DialogFlags.DESTROY_WITH_PARENT,
                Gtk.MessageType.ERROR,
                Gtk.ButtonsType.OK,
                "Profile not selected"
                )
            d.run()
            d.destroy()

        else:

            name = self._profile_icon_view.get_model()[items[0]][0][:-4]

            self._main.open(name)

        return

    def _on_refresh_list_clicked(self, button):
        self.refresh_list()

    def _on_iconview_item_activated(self, icon_view, path):
        self._on_activate_clicked(None)


# TODO: remove this
class Dumb:
    pass


class ProfileWindow:

    def __init__(self, parent, profile=None, typ='new'):

        self.iteration_loop = org.wayround.utils.gtk.GtkIteratedLoop()

        if not typ in ['new', 'edit', 'open']:
            raise ValueError("`typ' must be in ['new', 'edit', 'open']")

        if typ in ['edit', 'open'] and not isinstance(profile, str):
            raise ValueError(
                "in ['edit', 'open'] mode `profile_data' must be str"
                )

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

        self.window_elements.win.hide()
        self.iteration_loop.stop()
