#!/usr/bin/gjs
imports.gi.versions['GLib'] = '2.0';
imports.gi.versions['GObject'] = '2.0';
imports.gi.versions['Gio'] = '2.0';
imports.gi.versions['Gdk'] = '3.0';
imports.gi.versions['Gtk'] = '3.0';
imports.gi.versions['WebKit'] = '3.0';

const System = imports.system;
const GLib = imports.gi.GLib;
const GIRepository = imports.gi.GIRepository;
const Gio = imports.gi.Gio;
const Gdk = imports.gi.Gdk;
const display = Gdk.Display.open(':0');
const screen = display.get_default_screen();
const Gtk = imports.gi.Gtk;
const WebKit = imports.gi.WebKit;

var params = {
	application_id: 'mete0r.MYAPP',
	flags: 0
};

GLib.set_prgname(params.application_id);
GLib.set_application_name('MYAPP');

const App = new Gtk.Application(params);
App.connect('activate', function() {
	const MainWindow = new Gtk.ApplicationWindow({
		application: App
	});
	const grid = new Gtk.Box({
		orientation: Gtk.Orientation.VERTICAL,
		visible: true,
	});
	const wv = new WebKit.WebView();
	wv.load_string('hello', 'text/plain', '', '');
	grid.pack_start(wv, true, true, 0);
	MainWindow.add(grid);
	grid.show_all();
	MainWindow.show();
	print('OK');
	log('OK');
});
App.run(ARGV);
