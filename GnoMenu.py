#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from gi.repository import Gtk, Gdk, GMenu
import subprocess
import os

class Button(Gtk.Button):
    def __init__(self):
        super(Button, self).__init__()
        self.set_image(Gtk.Image.new_from_icon_name("view-list-symbolic", Gtk.IconSize.BUTTON))
        self.connect("clicked", self.clicked)

    def clicked(self, button):
        Window()

class ListBoxRow(Gtk.ListBoxRow):
    def __init__(self, data, text, gicon):
        super(ListBoxRow, self).__init__()
        self.data = data
        box = Gtk.Box()
        box.set_border_width(5)
        box.set_spacing(5)
        box.pack_start(Gtk.Image.new_from_gicon(gicon, Gtk.IconSize.BUTTON), False, False, 0)
        box.pack_start(Gtk.Label.new(text), False, False, 0)
        self.add(box)
        self.show_all()

class Window(Gtk.Window):
    def __init__(self):
        super(Window, self).__init__()
        self.set_size_request(500, 610)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(False)
        self.connect("focus-out-event", self.focus_out_event)
        self.connect("key-press-event", self.key_press_event)

        self.headerbar = Gtk.HeaderBar()
        self.headerbar.set_show_close_button(True)
        self.headerbar.set_decoration_layout(":close")
        self.set_titlebar(self.headerbar)

        self.button = Gtk.ToggleButton()
        self.button.set_image(Gtk.Image.new_from_icon_name("edit-find-symbolic", Gtk.IconSize.BUTTON))
        self.button.connect("toggled", self.toggled)
        self.headerbar.pack_start(self.button)

        grid = Gtk.Grid()
        self.add(grid)

        self.revealer = Gtk.Revealer()
        self.search = Gtk.SearchEntry()
        self.search.set_placeholder_text("Search")
        self.search.set_margin_left(5)
        self.search.set_margin_right(5)
        self.search.set_margin_top(5)
        self.search.set_margin_bottom(5)
        self.search.connect("search-changed", self.search_changed)
        self.revealer.add(self.search)
        grid.attach(self.revealer, 0, 0, 1, 1)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_hexpand(False)
        scrolled.set_vexpand(True)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.listbox1 = Gtk.ListBox()
        self.listbox1.connect("row-selected", self.row_selected)
        scrolled.add(self.listbox1)
        grid.attach(scrolled, 0, 1, 1, 1)

        separator = Gtk.Separator.new(Gtk.Orientation.VERTICAL)
        grid.attach(separator, 1, 0, 1, 2)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_hexpand(True)
        scrolled.set_vexpand(True)
        self.listbox2 = Gtk.ListBox()
        self.listbox2.set_filter_func(self.filter_list)
        self.listbox2.connect("row-activated", self.row_activated)
        scrolled.add(self.listbox2)
        grid.attach(scrolled, 2, 0, 1, 2)

        self.tree = GMenu.Tree.new(os.environ.get("XDG_MENU_PREFIX", "") + "applications.menu", GMenu.TreeFlags.SORT_DISPLAY_NAME)
        self.tree.load_sync()
        self.create_lists(self.tree.get_root_directory())

        widget = self.listbox1.get_row_at_index(0)
        self.listbox1.select_row(widget)

        self.show_all()
        self.present()

    def create_lists(self, tree_directory):
        dir_iter = tree_directory.iter()
        current_type = dir_iter.next()
        while current_type is not GMenu.TreeItemType.INVALID:
            if current_type == GMenu.TreeItemType.DIRECTORY:
                directory = dir_iter.get_directory()
                self.add_to_list(ListBoxRow(directory, directory.get_name(), directory.get_icon()), self.listbox1)

                self.create_lists(dir_iter.get_directory())

            elif current_type == GMenu.TreeItemType.ENTRY:
                entry = dir_iter.get_entry()
                info = entry.get_app_info()
                self.add_to_list(ListBoxRow(entry, info.get_name(), info.get_icon()), self.listbox2)
            current_type = dir_iter.next()

    def add_to_list(self, row, listbox):
        try:
            listbox.add(row)
        except:
            pass

    def toggled(self, button):
        if self.button.get_active():
            self.revealer.set_reveal_child(True)
            self.search.grab_focus()
        else:
            self.revealer.set_reveal_child(False)
            self.button.grab_focus()
        self.listbox2.invalidate_filter()

    def search_changed(self, entry):
        self.listbox2.invalidate_filter()

    def filter_list(self, lists):
        if self.button.get_active():
            if self.search.get_text().lower() in lists.data.get_app_info().get_name().lower():
                return lists
        else:
            selected_category = self.listbox1.get_selected_row()
            if selected_category:
                if selected_category.data.get_name() in lists.data.get_parent().get_name():
                    return lists

    def row_selected(self, listbox, row):
        self.listbox2.invalidate_filter()
        if row:
            self.headerbar.set_title(row.data.get_name())

    def row_activated(self, listbox, row):
        subprocess.Popen(row.data.get_app_info().get_executable(), shell = True)

    def focus_out_event(self, window, event):
        self.close()

    def key_press_event(self, window, event):
        if event.keyval == Gdk.KEY_Escape:
            self.close()

if __name__ == "__main__":
    window = Window()
    window.connect("delete-event", Gtk.main_quit)
    Gtk.main()
