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
import gtk
import webkit


def main():
    content = '''
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
    '''
    view = webkit.WebView()
    view.load_string(content, 'text/plain', '', '')

    scrolled_window = gtk.ScrolledWindow()
    scrolled_window.props.hscrollbar_policy = gtk.POLICY_AUTOMATIC
    scrolled_window.props.vscrollbar_policy = gtk.POLICY_AUTOMATIC
    scrolled_window.add(view)

    box = gtk.VBox()
    box.pack_start(scrolled_window)

    window = gtk.Window()
    window.add(box)
    window.connect('delete-event', gtk.main_quit)
    window.set_default_size(600, 400)
    window.show_all()

    gtk.main()


if __name__ == '__main__':
    main()
