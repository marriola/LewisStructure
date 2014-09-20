import pygtk

pygtk.require("2.0")
import gtk
import gtk.glade
import cairo

from EditorBase import EditorBase


class PeriodicTableSelector(EditorBase):
	def __init__(self):
		super(PeriodicTableSelector, self).__init__()
		self.button_pressed = False

	def redraw_table(self):
		self.tableDialog.queue_draw_area(0, 0, table_pixbuf.get_width(), table_pixbuf.get_height())

	def on_dlgPeriodicTable_delete_event(self, widget, event):
		self.btnSelect.set_active(True)
		self.tableDialog.hide()

	def on_drawingarea2_configure_event(self, widget, event):
		global table_pixmap, table_pixbuf
		table_pixbuf = gtk.gdk.pixbuf_new_from_file("table.png")
		table_pixbuf = table_pixbuf.add_alpha(True, 255, 255, 255)
		table_pixmap = gtk.gdk.Pixmap(widget.window, table_pixbuf.get_width(), table_pixbuf.get_height())
		self.tableDialog.set_size_request(table_pixbuf.get_width() + 15,
											table_pixbuf.get_height() + 20 + self.buttonBox.allocation.height)

	def on_drawingarea2_expose_event(self, widget, event):
		cr = widget.window.cairo_create()
		cr.set_source_surface(self.table_image, 0)
		cr.paint()

		if self.table_hover is not None:
			position = self.table_hover.position
			cr.set_source_rgba(0, 0, 0, 0.75 if self.button_pressed else 0.5)
			cr.rectangle(position[0], position[1], 37, 44)
			cr.set_operator(cairo.OPERATOR_XOR)
			cr.fill()

	def on_dlgPeriodicTable_motion_notify_event(self, widget, event):
		global table_pixbuf
		ax = self.periodicTable.allocation.x
		ay = self.periodicTable.allocation.y
		x = int(event.x) - ax
		y = int(event.y) - ay

		if x > 0 and y > 0:
			self.table_hover = None

			self.periodicTable.set_tooltip_text(None)
			for key in self.elements.keys():
				e = self.elements[key]
				if (x >= e.position[0] and x <= e.position[0] + 37 and
							y >= e.position[1] and y <= e.position[1] + 44):
					self.tableDialog.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.HAND1))
					self.table_hover = e
					self.redraw_table()
					self.periodicTable.set_tooltip_text(e.name)
					break

			if not self.table_hover:
				self.tableDialog.window.set_cursor(None)
				self.redraw_table()

	def on_dlgPeriodicTable_button_press_event(self, widget, event):
		self.button_pressed = True
		self.redraw_table()

	def on_dlgPeriodicTable_button_release_event(self, widget, event):
		self.button_pressed = False
		if self.table_hover:
			self.tableDialog.hide()
			self.window1.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.PLUS))
			self.place_element = self.table_hover
			self.table_hover = None

	def on_btnPTCancel_clicked(self, widget):
		self.tableDialog.hide()
		self.btnSelect.set_active(True)