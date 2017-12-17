#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

import json


catlist = ["pc", "npc", "location", "situation", "object"]
categories = {"pc": {"color": Gdk.RGBA(0, 0.8, 0, 1),
                     "name": "PC",
                     "short": "P"},
              "npc": {"color": Gdk.RGBA(0, 0, 0.9, 1),
                      "name": "NPC",
                      "short": "N"},
              "situation": {"color": Gdk.RGBA(1, 0.2, 0.9, 1),
                            "name": "Situation",
                            "short": "S"},
              "object": {"color": Gdk.RGBA(0.7, 0.7, 0.5, 1),
                         "name": "Object",
                         "short": "O"},
              "location": {"color": Gdk.RGBA(0.6, 1, 0.4, 1),
                           "name": "Location",
                           "short": "L"}}


class Aspect():
    """A single aspect"""
    def __init__(self, desc):
        self.desc = desc

    def __str__(self):
        return self.desc


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
        self.fobj.up_aspect(self.aspect)
        self.btn.set_label(self.get_label_text())
        self.listbox.invalidate_sort()
        self.onUpdate()

    def get_value(self):
        """Get value for this list box entry"""

        return self.fobj.get_aspect_count(self.aspect)


class FobBoxWithData(Gtk.Box):
    def __init__(self, fob, flowbox):
        super(Gtk.Box, self).__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)

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
        self.entry.set_text(self.fob.name)
        self.box.pack_start(self.shortl, False, True, 0)
        self.box.pack_start(self.entry, False, True, 0)
        self.box.pack_start(self.label, False, True, 0)

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
        aspect = editbox.get_text()
        self.fob.add_aspect(aspect)
        self.listbox.add(ListBoxRowWithData(self.fob, aspect, self.listbox, self.onUpdate))
        editbox.set_text("")
        self.show_all()

    def setLabel(self):
        self.label.set_markup(str(self.fob.total()))

    def onUpdate(self):
        """Call this on update"""
        self.setLabel()
        self.flowbox.invalidate_sort()

    def get_value(self):
        return self.fob.total()

    def get_category(self):
        return self.fob.category


class FlowBoxWindow(Gtk.Window):

    def __init__(self, title, fobs):
        Gtk.Window.__init__(self, title=title)
        self.fobs = fobs
        self.set_border_width(10)
        self.set_default_size(600, 550)

        header = Gtk.HeaderBar(title="Fate Aspect Manager")
        header.set_subtitle("Manage aspect usage")
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
                return c1.get_category() < c2.get_category
            return c1.get_value() > c2.get_value()

        self.flowbox.set_sort_func(flow_sort_func)

        self.create_flowbox()

        scrolled.add(self.flowbox)

        self.add(scrolled)
        self.show_all()

    def add_fob(self, button, category):
        newfob = Fobject(category, "", [])
        self.fobs.append(newfob)
        self.flowbox.add(FobBoxWithData(newfob, self.flowbox))
        self.show_all()

    def create_flowbox(self):
        for fob in self.fobs:
            fobbox = FobBoxWithData(fob, self.flowbox)
            self.flowbox.add(fobbox)


if __name__ == "__main__":
    fobs = []

    # TODO Delete
    with open("data.json", "rt") as fh:
        data = json.load(fh)

        for item in data:
            alist = [a for a in item["aspects"]]
            fobs.append(Fobject(item["category"],
                            item["name"], alist))

    #fobs.append(Fobject("pc", "Moonchild Sundance", ["Kleinkrimineller", "Aufbrausend", "Gute Händchen für Geschäfte"]))
    #fobs.append(Fobject("pc", "Hope Glory Water", ["Zum Überleben geschaffener Monsterjäger", "Heimatlos/Wer bin ich", "Ich kann das allein"]))
    #fobs.append(Fobject("pc", "Catey Parsley", ["Auf Samtpfoten unterwegs", "Ich weiß (alles)", "Zur rechten Zeit am rechten Ort"]))
    #fobs.append(Fobject("pc", "Allan Pickerton", ["Großvater Hilly Billy Werwolf", "Landei", "Durch harte Arbeit zum Erfolg"]))
    #fobs.append(Fobject("pc", "Jay (Jean LaFayette Boogaville)", ["Gutmütiger Voodoo Priester", "Zu spät", "Lass dir helfen !"]))
    #fobs.append(Fobject("pc", "Buba Duncan", ["Der muskulöse Partylöwe", "Sprunghafter Nigger", "Ich hab da was für dich"]))
    #print(fobs)

    win = FlowBoxWindow("Fate aspect manager", fobs)
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()

    data = []
    for fob in fobs:
        data.append({"category": fob.category, "name": fob.name, "aspects": fob.get_aspects()})
    print(data)
    with open("data.json", "wt") as fh:
        json.dump(data, fh, indent=4)
