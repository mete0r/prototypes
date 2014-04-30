# -*- coding: utf-8 -*-
#
#   MYAPP : SOME_DESCRIPTION
#   Copyright (C) 2014 mete0r <mete0r@sarangbang.or.kr>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from gi.repository import Gtk
from gi.repository import WebKit


def main(uri):
    webview = WebKit.WebView()
    webview.connect('load-finished', webview_load_finished)
    webview.load_uri(uri)

    scrolled_window = Gtk.ScrolledWindow()
    scrolled_window.add(webview)

    vbox = Gtk.VBox()
    vbox.pack_start(scrolled_window, expand=True, fill=True, padding=0)

    window = Gtk.Window()
    window.add(vbox)
    window.connect('delete-event', Gtk.main_quit)
    window.set_default_size(600, 400)
    window.show_all()
    Gtk.main()


def webview_load_finished(webview, webframe):
    print(webframe.get_uri())
