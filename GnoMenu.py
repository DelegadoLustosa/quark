#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# author: Delegado Lustosa

from gi.repository import Gtk, Gdk, GMenu
import subprocess
import os

class ListBoxRow(Gtk.ListBoxRow):
    def __init__(self, category, name, icon, executable):
        super(ListBoxRow, self).__init__()
        self.category = category
        self.name = name
        self.icon = icon
        self.executable = executable

        box = Gtk.Box()
        box.set_border_width(5)
        box.set_spacing(5)

        if self.icon:
            box.pack_start(Gtk.Image.new_from_gicon(self.icon, Gtk.IconSize.BUTTON), False, False, 0)
        box.pack_start(Gtk.Label.new(self.name), False, False, 0)

        self.add(box)
        self.show_all()

class DirectoriesListBox(Gtk.ListBox):
    def __init__(self):
        super(DirectoriesListBox, self).__init__()
        self.set_selection_mode(Gtk.SelectionMode.BROWSE)

class EntriesListBox(Gtk.ListBox):
    def __init__(self, search):
        super(EntriesListBox, self).__init__()
        self.category_filter = ""
        self.search = search
        self.set_filter_func(self.filter_list, None)
        self.connect("row-activated", self.row_activated)

    def filter_list(self, lists, data):
        text = self.search.get_text()
        if text:
            if text.lower() in lists.name.lower():
                return lists
        else:
            if self.category_filter.lower() == lists.category.lower():
                return lists

    def row_activated(self, listbox, row):
        subprocess.Popen(row.executable, shell = True)
        window = self.get_toplevel()
        window.close()

class Window(Gtk.Window):
    __gtype_name__ = "GnoMenu"

    def __init__(self):
        super(Window, self).__init__()
        self.set_size_request(550, 650)
        self.set_border_width(5)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(False)
        self.set_keep_above(True)
        self.connect("key-press-event", self.key_press_event)

        self.headerbar = Gtk.HeaderBar()
        self.headerbar.set_show_close_button(True)
        self.set_titlebar(self.headerbar)

        grid = Gtk.Grid()
        grid.set_row_spacing(5)
        grid.set_column_spacing(5)
        self.add(grid)

        self.search = Gtk.SearchEntry()
        self.search.connect("search-changed", self.search_changed)
        grid.attach(self.search, 0, 0, 1, 1)

        self.dlistbox = DirectoriesListBox()
        self.dlistbox.set_hexpand(False)
        self.dlistbox.set_vexpand(True)
        self.dlistbox.connect("row-selected", self.row_selected)
        grid.attach(self.dlistbox, 0, 1, 1, 1)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_hexpand(True)
        scrolled.set_vexpand(True)
        scrolled.set_shadow_type(Gtk.ShadowType.IN)
        self.elistbox = EntriesListBox(self.search)
        scrolled.add(self.elistbox)
        grid.attach(scrolled, 1, 0, 1, 2)

        self.tree = GMenu.Tree.new(os.environ.get("XDG_MENU_PREFIX", "") + "applications.menu", GMenu.TreeFlags.SORT_DISPLAY_NAME)
        self.tree.load_sync()
        self.create_list(self.tree.get_root_directory())

        index = self.dlistbox.get_row_at_index(0)
        self.dlistbox.select_row(index)

        self.show_all()
        self.present()

    def create_list(self, tree_directory):
        dir_iter = tree_directory.iter()
        current_type = dir_iter.next()
        while current_type is not GMenu.TreeItemType.INVALID:
            if current_type == GMenu.TreeItemType.DIRECTORY:
                directory = dir_iter.get_directory()
                self.dlistbox.add(ListBoxRow(None, directory.get_name(), directory.get_icon(), None))

                self.create_list(dir_iter.get_directory())

            elif current_type == GMenu.TreeItemType.ENTRY:
                entry = dir_iter.get_entry()
                info = entry.get_app_info()
                parent = entry.get_parent()
                self.elistbox.add(ListBoxRow(parent.get_name(), info.get_name(), info.get_icon(), info.get_executable()))
            current_type = dir_iter.next()

    def search_changed(self, entry):
        self.elistbox.invalidate_filter()

    def row_selected(self, listbox, row):
        if row:
            name = row.name
        else:
            name = ""
        self.elistbox.category_filter = name
        self.elistbox.invalidate_filter()
        self.headerbar.set_title(name)

    def key_press_event(self, window, event):
        if event.keyval == Gdk.KEY_Escape:
            self.close()

if __name__ == "__main__":
    Window()
    Gtk.main()
