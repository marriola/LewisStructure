import pygtk
pygtk.require("2.0")
import gtk
import gtk.glade
import cairo

from EditorBase import EditorBase


class PreferencesDialog(EditorBase):
	def on_btnPrefCancel_clicked(self, widget):
		self.winPreferences.hide()

	def on_btnPrefApply_clicked(self, widget):
		pass

	def on_btnPrefOK_clicked(self, widget):
		self.winPreferences.hide()