"""A Lewis Structure editor."""

__author__ = "Matt Arriola"
__copyright__ = "Copyright 2014"

import pygtk

pygtk.require("2.0")
import gtk
import gtk.glade
import cairo

from Element import Element
from Molecule import Molecule
from MoleculeEditor import MoleculeEditor
from PeriodicTableSelector import PeriodicTableSelector
from PreferencesDialog import PreferencesDialog


class EditorWindow(MoleculeEditor, PeriodicTableSelector, PreferencesDialog):
	def __init__(self, elements):
		super(EditorWindow, self).__init__()

		self.molecule = Molecule()
		self.results = []
		self.elements = elements
		self.table_image = cairo.ImageSurface.create_from_png("table.png")

		self.gladefile = "LewisStructure.glade"
		self.glade = gtk.Builder()
		self.glade.add_from_file(self.gladefile)
		self.glade.connect_signals(self)

		self.window1 = self.glade.get_object("window1")
		self.winPreferences = self.glade.get_object("winPreferences")
		self.viewport = self.glade.get_object("viewport1")
		self.drawing = self.glade.get_object("drawingarea1")
		self.buttonbox = self.glade.get_object("hbuttonbox2")
		self.lblNumConfigurations = self.glade.get_object("lblNumConfigurations")
		self.tableDialog = self.glade.get_object("dlgPeriodicTable")
		self.periodicTable = self.glade.get_object("drawingarea2")
		self.buttonBox = self.glade.get_object("dialog-action_area2")
		self.btnSelect = self.glade.get_object("btnSelect")
		self.btnAdd = self.glade.get_object("btnAdd")
		self.btnRemove = self.glade.get_object("btnRemove")
		self.btnBond = self.glade.get_object("btnBond")
		self.menuSnap = self.glade.get_object("menuSnap")

		self.buttonbox.set_visible(False)
		self.lblNumConfigurations.set_visible(False)
		self.drawing.set_events(gtk.gdk.EXPOSURE_MASK)
		self.window1.show_all()

	def on_btnSelect_toggled(self, widget):
		widget.window.set_cursor(None)
		self.mode = self.SELECT

	def on_btnAdd_toggled(self, widget):
		if widget.get_active():
			widget.window.set_cursor(None)
			self.mode = self.ADD_ATOM
			self.tableDialog.run()
			self.tableHover = None

	def on_btnRemove_toggled(self, widget):
		widget.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.X_CURSOR))
		self.mode = self.DEL_ATOM

	def on_btnBond_toggled(self, widget):
		widget.window.set_cursor(None)
		self.mode = self.BOND


doubleBond = ["C", "N", "O", "P", "S"]

from ElementData import element_data

elements = {}
number = 1
for e in element_data:
	symbol, name, AVEE, group, valence, position = e
	elements[symbol] = Element(number, int(group), int(valence), symbol, name, AVEE, position)
	number += 1

if __name__ == "__main__":
	editor = EditorWindow(elements)
	gtk.main()