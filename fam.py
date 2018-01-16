#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, Gio

import json
import sys
import gettext
import locale
from os.path import abspath, dirname, join

# Setup

APP = 'fateaspectmanager'
WHERE_AM_I = abspath(dirname(__file__))
LOCALE_DIR = join(WHERE_AM_I, 'mo')

gettext.bindtextdomain(APP, LOCALE_DIR)
gettext.textdomain(APP)
_ = gettext.gettext
locale.setlocale(locale.LC_ALL, '')
locale.bindtextdomain(APP, LOCALE_DIR)

print(gettext.find(APP, LOCALE_DIR))
print('Using locale directory: {}'.format(LOCALE_DIR))
print(_("PC"))

# Configs
catlist = ["pc", "npc", "location", "situation", "object"]
categories = {"pc": {"color": Gdk.RGBA(0, 0.8, 0, 1),
                     "name": _("PC"),
                     "short": "P"},
              "npc": {"color": Gdk.RGBA(0, 0, 0.9, 1),
                      "name": _("NPC"),
                      "short": "N"},
              "situation": {"color": Gdk.RGBA(1, 0.2, 0.9, 1),
                            "name": _("Situation"),
                            "short": "S"},
              "object": {"color": Gdk.RGBA(0.7, 0.7, 0.5, 1),
                         "name": _("Object"),
                         "short": "O"},
              "location": {"color": Gdk.RGBA(0.6, 1, 0.4, 1),
                           "name": _("Location"),
                           "short": "L"}}


class Fobject():
    """A fate object"""

    def __init__(self, category, name, aspects):
        """Init a Fate object

        category: category of the object
        name: name of the object
        aspects: list of strings
        """
        self.name = name
        self.category = category
        self.aspects = {}
        for a in aspects:
            self.add_aspect(a)

    def __str__(self):
        res = self.name + "\n\n"
        res += "\n".join([str(a) for a in self.aspects])
        return res

    def get_aspects(self):
        return self.aspects

    def add_aspect(self, aspect):
        """Add an aspect to the object"""
        self.aspects[aspect] = 0

    def get_aspect_count(self, aspect):
        return self.aspects[aspect]

    def up_aspect(self, aspect):
        """Add 1 to an aspect"""
        self.aspects[aspect] += 1

    def total(self):
        return sum(self.aspects.values())

    def set_name(self, name):
        print(name)
        self.name = name

class FCollection():
    """Manage a collection of Fate objects"""
    def __init__(self):
        self.collection = []

    def addfob(self, fob):
        """Add a fob object to the collection"""
        self.collection.append(fob)

    def addfobs(self, fobs):
        """Delete current collection and add all fobs"""
        self.collection = []
        for fob in fobs:
            self.addfob(fob)

    def remove_fob(self, fob):
        """Remove fob from data

        fob: fob to remove
        """
        self.collection.remove(fob)

    def clean(self):
        """remove all objects"""
        self.collection = []

    def load(self, filename):
        self.fobs = []
        if filename is None:
            filename = "default.fam"
        with open(filename, "rt") as fh:
            data = json.load(fh)

            for item in data:
                alist = [a for a in item["aspects"]]
                self.collection.append(Fobject(item["category"],
                                               item["name"], alist))

    def save(self, filename):
        """Store data into json format file"""
        data = []
        for fob in self.collection:
            data.append({"category": fob.category,
                         "name": fob.name,
                         "aspects": fob.get_aspects()})
        print(data)
        with open(filename, "wt") as fh:
            json.dump(data, fh, indent=4)

    def get_fobs(self):
        return self.collection

############ GUI stuff

class ListBoxRowWithData(Gtk.ListBoxRow):
    def __init__(self, fobj, aspect, listbox, onUpdate):
        super(Gtk.ListBoxRow, self).__init__()
        self.fobj = fobj
        self.aspect = aspect
        self.listbox = listbox
        self.onUpdate = onUpdate
        self.btn = Gtk.Button.new_with_label(self.get_label_text())
        self.btn.connect("clicked", self.on_click)
        self.add(self.btn)

    def get_label_text(self):
        return self.aspect + ": " + str(self.get_value())

    def on_click(self, button):
        """Increase the count of an aspect"""
        self.fobj.up_aspect(self.aspect)
        self.btn.set_label(self.get_label_text())
        self.listbox.invalidate_sort()
        self.onUpdate()

    def get_value(self):
        """Get value for this list box entry which is the count on the aspect"""

        return self.fobj.get_aspect_count(self.aspect)


class FobBoxWithData(Gtk.Box):
    """Draw a Fobbox"""
    def __init__(self, window, fob, flowbox):
        super(Gtk.Box, self).__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)

        self.window = window
        self.flowbox = flowbox
        self.fob = fob
        self.label = Gtk.Label()
        self.setLabel()

        # Horizontal box for header
        self.box = Gtk.Box(spacing=6)
        self.box.override_background_color(Gtk.StateType.NORMAL, categories[fob.category]["color"])
        self.add(self.box)
        self.shortl = Gtk.Label(categories[fob.category]["short"])
        self.entry = Gtk.Entry()
        self.entry.connect("activate", self.name_changed)
        self.entry.connect("key-release-event", self.name_changed)
        self.remove_button = Gtk.Button("-")
        self.remove_button.connect("clicked", self.remove_clicked)
        self.entry.set_text(self.fob.name)
        self.box.pack_start(self.shortl, False, True, 0)
        self.box.pack_start(self.entry, False, True, 0)
        self.box.pack_start(self.label, False, True, 0)
        self.box.pack_start(self.remove_button, False, True, 0)

        self.listbox = Gtk.ListBox()
        for aspect in self.fob.get_aspects():
            self.listbox.add(ListBoxRowWithData(self.fob, aspect, self.listbox, self.onUpdate))

        def sort_func(row_1, row_2, data, notify_destroy):
            return row_1.get_value() > row_2.get_value()

        self.listbox.set_sort_func(sort_func, None, False)

        self.pack_start(self.listbox, True, True, 0)

        self.box_end = Gtk.Box(spacing=6)
        self.add(self.box_end)
        self.entry = Gtk.Entry()
        self.entry.connect("activate", self.aspect_added)
        self.box_end.pack_start(Gtk.Label("+"), False, True, 0)
        self.box_end.pack_start(self.entry, False, True, 0)

    def name_changed(self, editbox, event=None):
        self.fob.set_name(editbox.get_text())

    def aspect_added(self, editbox):
        """Event called when an aspect was added"""
        aspect = editbox.get_text()
        self.fob.add_aspect(aspect)
        self.listbox.add(ListBoxRowWithData(self.fob, aspect, self.listbox, self.onUpdate))
        editbox.set_text("")
        self.show_all()

    def remove_clicked(self, thebutton):
        """User clicked remove button"""
        dialog = Gtk.MessageDialog(self.window, 0, Gtk.MessageType.QUESTION,
            Gtk.ButtonsType.YES_NO, _("Delete this Object from your world ?"))
        dialog.format_secondary_text(
            _("Do you want to delete this object ?"))
        response = dialog.run()
        if response == Gtk.ResponseType.YES:
            dialog.destroy()
            self.window.remove_fob(self)
        elif response == Gtk.ResponseType.NO:
            #print("QUESTION dialog closed by clicking NO button")
            dialog.destroy()
            pass



    def setLabel(self):
        """Set the count label"""
        self.label.set_markup(str(self.fob.total()))

    def onUpdate(self):
        """Call this on update"""
        self.setLabel()
        self.flowbox.invalidate_sort()

    def get_value(self):
        return self.fob.total()

    def get_category(self):
        return self.fob.category


class FlowBoxWindow(Gtk.ApplicationWindow):

    def __init__(self, fcol, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fcol = fcol
        self.set_border_width(10)
        self.set_default_size(600, 550)

        header = Gtk.HeaderBar()
        header.set_title(_("Fate Aspect Manager"))
        header.set_subtitle(_("Manage aspect usage"))
        header.props.show_close_button = True

        for key in catlist:
            b = Gtk.Button(categories[key]["name"])
            b.override_color(Gtk.StateType.NORMAL, categories[key]["color"])
            b.connect("clicked", self.add_fob, key)
            header.pack_start(b)

        self.set_titlebar(header)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_valign(Gtk.Align.START)
        self.flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.flowbox.set_max_children_per_line(30)

        def flow_sort_func(child_1, child_2):
            c1 = child_1.get_children()[0]
            c2 = child_2.get_children()[0]
            if c1.get_category() != c2.get_category():
                return catlist.index(c1.get_category()) > catlist.index(c2.get_category())
            return c1.get_value() > c2.get_value()

        self.flowbox.set_sort_func(flow_sort_func)

        self.fill_flowbox()

        scrolled.add(self.flowbox)

        self.add(scrolled)
        self.show_all()

    def add_fob(self, button, category):
        """Adds a new and empty fob"""
        newfob = Fobject(category, "", [])
        self.fcol.addfob(newfob)
        self.flowbox.add(FobBoxWithData(self, newfob, self.flowbox))
        self.show_all()

    def fob_already_displayed(self, fob):
        for flowbox in self.flowbox.get_children():
            if flowbox.get_children()[0].fob == fob:
                return True
        return False

    def fill_flowbox(self, fcol=None):
        """Add all the Fobs in the collection to the flowbox"""
        if fcol:
            self.fcol = fcol
        for fob in self.fcol.get_fobs():
            print(fob)
            if not self.fob_already_displayed(fob):
                fobbox = FobBoxWithData(self, fob, self.flowbox)
                self.flowbox.add(fobbox)
        self.show_all()

    def empty_flowbox(self):
        """Remove all children from the flowbox"""
        for child in self.flowbox.get_children():
            self.flowbox.remove(child)

    def remove_fob(self, child, remove_data=True):
        """Remove child from flowbox

        child: child to remove
        remove_data: Also remove data representation
        """
        if remove_data:
            self.fcol.remove_fob(child.fob)
        for boxes in self.flowbox.get_children():
            if boxes.get_children()[0] == child:
                self.flowbox.remove(boxes)


class Application(Gtk.Application):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="org.sickstuff.FateAspectManager",
                         flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
                         **kwargs)
        self.window = None

        self.add_main_option("test", ord("t"), GLib.OptionFlags.NONE,
                             GLib.OptionArg.NONE, "Command line test", None)

        self.fcol = FCollection()
        #self.fobs = []
        self.path = None

    def do_startup(self):
        Gtk.Application.do_startup(self)

        action = Gio.SimpleAction.new("open", None)
        action.connect("activate", self.on_open_file)
        self.add_action(action)

        action = Gio.SimpleAction.new("openandadd", None)
        action.connect("activate", self.on_open_and_add_file)
        self.add_action(action)

        action = Gio.SimpleAction.new("save", None)
        action.connect("activate", self.on_save_file)
        self.add_action(action)

        action = Gio.SimpleAction.new("saveas", None)
        action.connect("activate", self.on_save_as_file)
        self.add_action(action)

        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.on_about)
        self.add_action(action)

        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self.on_quit)
        self.add_action(action)

        self.builder = Gtk.Builder()
        self.glade_file = join(WHERE_AM_I, "ui", "fam.glade")
        self.builder.set_translation_domain(APP)
        self.builder.add_from_file(self.glade_file)
        self.set_app_menu(self.builder.get_object("app-menu"))

    def do_activate(self):
        # We only allow a single window and raise any existing ones
        if not self.window:
            # Windows are associated with the application
            # when the last one is closed the application shuts down
            self.window = FlowBoxWindow(fcol=self.fcol, application=self, title=_("Fate Aspect Manager"))

        self.window.present()

    def do_command_line(self, command_line):
        options = command_line.get_options_dict()

        if options.contains("test"):
            # This is printed on the main instance
            print("Test argument recieved")

        self.activate()
        return 0

    def load(self, filename=None):
        if filename is None:
            filename = "default.fam"
        self.fcol.load(filename)

    def save(self, filename=None):
        if filename is None:
            filename = "default.fam"
        self.fcol.save(filename)

    @classmethod
    def add_filters(cls, dialog):
        filter_fam = Gtk.FileFilter()
        filter_fam.set_name('FAM data')
        filter_fam.add_pattern("*.fam")
        dialog.add_filter(filter_fam)

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)

    def on_open_file(self, action, param):
        dialog = Gtk.FileChooserDialog(_("Open File"),
                                       self.window,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL,
                                        Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN,
                                        Gtk.ResponseType.OK))
        self.add_filters(dialog)
        dialog.set_select_multiple(True)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.window.empty_flowbox()
            paths = dialog.get_filenames()
            for path in paths:
                self.path = path
                self.load(self.path)
                self.window.fill_flowbox(fcol=self.fcol)
            if len(paths) > 0:
                self.path = None
            dialog.destroy()
        elif response == Gtk.ResponseType.CANCEL:
            dialog.destroy()

    def on_open_and_add_file(self, action, param):
        dialog = Gtk.FileChooserDialog(_("Open File"),
                                       self.window,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL,
                                        Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN,
                                        Gtk.ResponseType.OK))
        self.add_filters(dialog)
        dialog.set_select_multiple(True)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            paths = dialog.get_filenames()
            for path in paths:
                self.path = None
                self.load(path)
                self.window.fill_flowbox(fcol=self.fcol)
            dialog.destroy()
        elif response == Gtk.ResponseType.CANCEL:
            dialog.destroy()

    def on_save_file(self, action, param):
        self.save(self.path)

    def on_save_as_file(self, action, param):
        dialog = Gtk.FileChooserDialog(_("Save File"),
                                       self.window,
                                       Gtk.FileChooserAction.SAVE,
                                       (Gtk.STOCK_CANCEL,
                                        Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN,
                                        Gtk.ResponseType.OK))
        self.add_filters(dialog)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.path = dialog.get_filename()
            self.save(self.path)
            dialog.destroy()
        elif response == Gtk.ResponseType.CANCEL:
            dialog.destroy()

    def on_about(self, action, param):
        about_dialog = Gtk.AboutDialog(transient_for=self.window, modal=True)
        about_dialog.set_copyright(_("By Thorsten Sick"))
        about_dialog.set_website("https://github.com/Thorsten-Sick/FateAspectManager")
        about_dialog.set_license_type(Gtk.License.GPL_3_0)
        about_dialog.present()

    def on_quit(self, action, param):
        # TODO: Cleanup. lots of it....code is ugly thanks to experiments
        # TODO: Extra large name tag for cards (currently: does not scale)
        # TODO: Remember working dir to open from
        self.quit()


if __name__ == "__main__":

    app = Application()
    app.run(sys.argv)
