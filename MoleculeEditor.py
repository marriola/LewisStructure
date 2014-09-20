from __future__ import print_function
import pygtk

pygtk.require("2.0")
import gtk
import gtk.glade
import pango
import cairo
import math
import copy
from collections import defaultdict

from EditorBase import EditorBase
from Atom import Atom
from Bond import Bond
from Molecule import Molecule


class MoleculeEditor(EditorBase):
	GAP_SIZE = 2
	SINGLE_BOND_THICKNESS = 2

	def __init__(self):
		super(MoleculeEditor, self).__init__()

		self.starting_slots = []
		angle = 0
		angle_step = math.pi / 2
		electron_step = 15
		distance = 0

		for i in range(8):
			self.starting_slots.append([angle, distance, 0, electron_step])
			angle += angle_step
			# if angle > math.pi * 2:
			# angle -= math.pi * 2
			if i == 3:
				angle += math.pi / 4
				electron_step = 20
				distance += 5


	# ########################################
	# ##           Graphics methods
	# ########################################

	def snap_atoms(self, atoms):
		for a in atoms:
			# atom = self.molecule.atoms[a]
			a.x = a.x // 20 * 20
			a.y = a.y // 20 * 20

	def redraw(self):
		self.window1.queue_draw_area(0, 0, 640, 480)

	def overlaps_bond(self, atom, region, gc):
		"""Checks if any bonds associated with an atom pass through a region"""
		redGC = pixmap.new_gc()
		redGC.set_rgb_fg_color(gtk.gdk.Color("red"))

		blueGC = pixmap.new_gc()
		blueGC.set_rgb_fg_color(gtk.gdk.Color("blue"))

		for bond in self.molecule.bonds:
			if atom.label in (bond.atom1, bond.atom2):
				atom1 = self.molecule.atoms[bond.atom1]
				atom2 = self.molecule.atoms[bond.atom2]

				x1 = atom1.x + atom1.layout_width / 2
				y1 = atom1.y + atom1.layout_height / 2
				x2 = atom2.x + atom2.layout_width / 2
				y2 = atom2.y + atom2.layout_height / 2
				diff_x = float(x2 - x1)
				diff_y = float(y2 - y1)
				if diff_x == 0:
					diff_x = 0.001

				slope = (diff_y / diff_x)

				# does the line cross the region at any of its edges?

				# check left edge
				pos_x = region.x
				pos_y = int(y1 + slope * (region.x - x1))
				# if region.x > x2 and region.y < pos_y < region.y + region.height:
				between = (x2 < region.x < x1) if x1 > x2 else (x1 < region.x < x2)
				if between and region.y < pos_y < region.y + region.height:
					return True

				# print(atom1.label, atom2.label, slope, y1, region.y, y2)
				if slope:
					pos_x = int(x1 + 1 / slope * (region.y - y1))
					pos_y = region.y
					# if region.y > y2 and region.x < pos_x < region.x + region.width:
					# between = (y2 < region.y < y1) if y1 > y2 else (y1 < region.y < y2)
					if between and region.x < pos_x < region.x + region.width:
						return True
				"""elif y1 < region.y < y2 or y2 < region.y < y1:
					return True"""

		return False

	def point_from_origin(self, origin_x, origin_y, r, theta):
		x = int(r * math.cos(theta))
		y = int(r * math.sin(theta))
		return [origin_x + x, origin_y + y]

	def draw_point(self, size, x, y, dot_color="black"):
		"""Draws a point at the end of a line segment from polar coordinates (0, 0) to (r, theta)"""

		gc = pixmap.new_gc()
		gc.set_rgb_fg_color(gtk.gdk.Color(dot_color))
		pixmap.draw_rectangle(gc, True, x, y, size, size)

	# pixmap.draw_line(gc, origin_x, origin_y, origin_x + x, origin_y + y)

	def draw_nonbonding_electrons(self, widget, gc, atom):
		origin_x = atom.x + atom.layout_width / 2
		origin_y = atom.y + atom.layout_height / 2
		num_electrons = atom.nonbonding_electrons
		dot_color = False
		blocked = defaultdict(lambda: False, {})

		# assign electrons to slots around the atom
		slots = copy.deepcopy(self.starting_slots)
		current_slot = 0

		while num_electrons:
			point = self.point_from_origin(origin_x, origin_y, atom.layout_width + 5, slots[current_slot][0])
			region = gtk.gdk.Rectangle(point[0] - 5, point[1] - 5, 10, 10)
			# does a bond overlap this region?
			if self.overlaps_bond(atom, region, gc):
				blocked[current_slot] = True
				# do we already have an electron in this slot? if so, stick it in the next one instead
				if slots[current_slot][2] == 1:
					slots[current_slot][2] -= 1
					num_electrons += 1

				# go to first empty slot
				for i in range(8):
					# print("trying slot %d at angle %f" % (i, slots[i][0]))
					if slots[i][2] == 0 and not blocked[i]:
						current_slot = i
						break
					if i == 7:
						print("fuck all slots blocked!!!")
						return

			else:
				# advance to the next empty slot if full
				if slots[current_slot][2] == 2:
					for i in range(8):
						if slots[i][2] == 0 and not blocked[i]:
							current_slot = i
							break

				slots[current_slot][2] += 1
				num_electrons -= 1

		# separate adjacent slots if possible
		"""last = 0
		for i in range(8):
			if last > 0 and slots[i][2] > 0 and slots[i + 1][2] == 0 and not blocked[i + 2]:
				slots[i + 1][2] = slots[i][2]
				slots[i][2] = 0
			last = slots[i][2]"""

		# draw the slots
		for slot in slots:
			angle, distance, num_electrons, electron_step = slot
			# print(slot, angle * 180 / math.pi)
			if num_electrons == 2:
				angle1 = angle - math.pi / electron_step
				angle2 = angle + math.pi / electron_step
				p1 = self.point_from_origin(origin_x, origin_y, atom.layout_width + distance, angle1)
				p2 = self.point_from_origin(origin_x, origin_y, atom.layout_width + distance, angle2)
				self.draw_point(2, p1[0], p1[1])
				self.draw_point(2, p2[0], p2[1])

			elif num_electrons == 1:
				p = self.point_from_origin(origin_x, origin_y, atom.layout_width + distance, angle)
				self.draw_point(2, p[0], p[1])

	def draw_atom(self, widget, gc, atom):
		"""Draws an atom to the editor window

		widget		Widget to draw to
		gc			Graphics context to draw with
		atom		Atom object to display
		"""
		# specify symbol
		layout = widget.create_pango_layout(atom.element.symbol)
		layout.set_font_description(pango.FontDescription('Sans 15'))
		layout_size = layout.get_pixel_size()
		atom.layout_width, atom.layout_height = layout_size

		# clear a space around the atom
		gc.set_rgb_fg_color(gtk.gdk.Color("white"))
		pixmap.draw_rectangle(gc, True, atom.x - 2, atom.y - 2, layout_size[0] + 4, layout_size[1] + 4)

		# draw symbol
		symbol_color = "black" if atom.status == Atom.OK else "red"
		gc.set_rgb_fg_color(gtk.gdk.Color(symbol_color))
		pixmap.draw_layout(gc, atom.x, atom.y, layout)

		self.draw_nonbonding_electrons(widget, gc, atom)

		if self.show_labels:
			# specify atom label
			label_layout = widget.create_pango_layout(atom.label)
			label_layout.set_font_description(pango.FontDescription('Sans 6'))
			label_layout_size = label_layout.get_pixel_size()
			"""label_left = atom.x + (layout_size[0] / 2) - (label_layout_size[0] / 2) + 2
			label_top = atom.y + layout_size[1] + 5"""
			label_left = atom.x + layout_size[0] + 5
			label_top = atom.y - 10
			# atom.label_height = layout_size[1] - 5

			cr = pixmap.cairo_create()
			# draw box around atom label
			cr.set_source_rgba(1.0, 1.0, 0.5, 0.5)
			cr.rectangle(label_left - 3, label_top - 1, label_layout_size[0] + 2, label_layout_size[1] + 2)
			cr.fill()
			cr.set_source_rgba(0.0, 0.0, 0.0, 0.5)
			cr.rectangle(label_left - 3, label_top - 1, label_layout_size[0] + 2, label_layout_size[1] + 2)
			cr.stroke()

			cr.set_font_size(8)
			cr.move_to(label_left - 2, label_top + 8)
			cr.show_text(atom.label)

			"""gc.set_rgb_fg_color(gtk.gdk.Color("#ff8"))
			pixmap.draw_rectangle(gc, True, label_left - 3, label_top - 1, label_layout_size[0] + 2, label_layout_size[1] + 2)
			gc.set_rgb_fg_color(gtk.gdk.Color("black"))
			pixmap.draw_rectangle(gc, False, label_left - 3, label_top - 1, label_layout_size[0] + 2, label_layout_size[1] + 2)

			# draw label text
			pixmap.draw_layout(gc, label_left - 2, label_top, label_layout)"""
		else:
			label_layout_size = [0, 0]

		# indicate if this atom is currently selected
		if atom in self.selection:
			cr = pixmap.cairo_create()
			cr.set_source_rgba(64, 96, 255, 0.33)
			cr.rectangle(atom.x - 2, atom.y, layout_size[0] + 7, layout_size[1])
			cr.set_operator(cairo.OPERATOR_XOR)
			cr.fill()

	def draw_bond(self, pixmap, type, atom1, atom2, openEnd=None):
		"""Draws a bond between two atoms. If the bond is open (the first atom
		has been selected, but not the first), then atom2 will be None and
		openEnd will contain the coordinates of the open end.

		pixmap		Pixmap to draw to
		type		Type of bond (Bond.SINGLE, Bond.DOUBLE, or Bond.TRIPLE)
		atom1		First atom in the bond
		atom2		Second atom in the bond (None if bond is open)
		openEnd		Coordinates of the open end of an open bond"""

		start_x, start_y = atom1.x + atom1.layout_width / 2, atom1.y + atom1.layout_height / 2
		if openEnd:
			end_x, end_y = openEnd
		else:
			end_x, end_y = atom2.x + atom2.layout_width / 2, atom2.y + atom2.layout_height / 2

		# determine gap between multiple bond lines based on relative position of its atoms
		gap_x = -self.GAP_SIZE if start_x > end_x else self.GAP_SIZE
		gap_y = self.GAP_SIZE if start_y > end_y else -self.GAP_SIZE

		lineGC = pixmap.new_gc()
		if type == Bond.SINGLE:
			lineGC.set_line_attributes(self.SINGLE_BOND_THICKNESS, gtk.gdk.LINE_SOLID, gtk.gdk.CAP_BUTT,
										gtk.gdk.JOIN_MITER)
			pixmap.draw_line(lineGC, start_x, start_y, end_x, end_y)
		elif type == Bond.DOUBLE:
			pixmap.draw_line(lineGC, start_x - gap_x, start_y - gap_y, end_x - gap_x, end_y - gap_y)
			pixmap.draw_line(lineGC, start_x + gap_x, start_y + gap_y, end_x + gap_x, end_y + gap_y)
		elif type == Bond.TRIPLE:
			pixmap.draw_line(lineGC, start_x - gap_x, start_y - gap_y, end_x - gap_x, end_y - gap_y)
			pixmap.draw_line(lineGC, start_x, start_y, end_x, end_y)
			pixmap.draw_line(lineGC, start_x + gap_x, start_y + gap_y, end_x + gap_x, end_y + gap_y)

	def on_drawingarea1_configure_event(self, widget, event):
		global pixmap
		x, y, width, height = widget.get_allocation()
		pixmap = gtk.gdk.Pixmap(widget.window, width, height)
		return True

	def copy_pixmap_to_window(self, widget, x, y, width, height):
		drawable_gc = widget.get_style().fg_gc[gtk.STATE_NORMAL]
		widget.window.draw_drawable(drawable_gc, pixmap, x, y, x, y, width, height)


	# ########################################
	# ##         GUI callback methods
	# ########################################

	def on_drawingarea1_expose_event(self, widget, event):
		global pixmap
		x, y, width, height = event.area

		gc = pixmap.new_gc()
		gc.set_rgb_fg_color(gtk.gdk.Color("white"))
		pixmap.draw_rectangle(gc, gtk.TRUE, 0, 0, width, height)

		# draw open bond if we have to
		gc.set_rgb_fg_color(gtk.gdk.Color("black"))
		if self.mode == self.BOND and self.grab is not None:
			self.draw_bond(pixmap, Bond.SINGLE, self.molecule.atoms[self.grab], None, openEnd=self.line_to)

		# draw bonds
		for bond in self.molecule.bonds:
			atom1 = self.molecule.atoms[bond.atom1]
			atom2 = self.molecule.atoms[bond.atom2]
			self.draw_bond(pixmap, bond.type, atom1, atom2)

		for key in self.molecule.atoms.keys():
			atom = self.molecule.atoms[key]
			self.draw_atom(widget, gc, atom)

		if self.show_grid:
			gc.set_rgb_fg_color(gtk.gdk.Color("black"))
			for gx in range(0, 640, 20):
				for gy in range(0, 480, 20):
					pixmap.draw_point(gc, gx, gy)

		self.copy_pixmap_to_window(widget, x, y, width, height)

		if len(self.selection_box) == 4:
			cr = widget.window.cairo_create()
			cr.set_source_rgba(64, 96, 255, 0.33)
			cr.rectangle(self.selection_box[0], self.selection_box[1], self.selection_box[2], self.selection_box[3])
			cr.set_operator(cairo.OPERATOR_XOR)
			cr.fill()

	def on_window1_delete_event(self, widget, event):
		gtk.main_quit()

	def on_window1_button_press_event(self, widget, event):
		dx = self.drawing.allocation.x
		dy = self.drawing.allocation.y
		x, y, mask = widget.window.get_pointer()
		x -= dx
		y -= dy

		# if we're in select or bond mode, check if we clicked on an atom
		if x >= 0 and y >= 0 and self.mode in (self.SELECT, self.BOND):
			for key in self.molecule.atoms.keys():
				atom = self.molecule.atoms[key]
				if (x >= atom.x and x <= atom.x + atom.layout_width and
							y >= atom.y and y <= atom.y + atom.layout_height):  # + atom.label_height):
					self.grab_offset_x = x - atom.x
					self.grab_offset_y = y - atom.y
					self.grab = key
					break

			# nothing selected, enable selection square
			if self.grab is None:
				self.selection_box = [x, y]

	def on_window1_motion_notify_event(self, widget, event):
		base_x = self.drawing.allocation.x
		base_y = self.drawing.allocation.y
		x = int(event.x) - base_x
		y = int(event.y) - base_y

		if not self.grab:
			if len(self.selection_box) > 0 and self.mode == self.SELECT:
				origin_x = self.selection_box[0]
				origin_y = self.selection_box[1]

				if x < origin_x:
					x, origin_x = origin_x, x
				if y < origin_y:
					y, origin_y = origin_y, y

				self.selection_box = [origin_x, origin_y, x - origin_x, y - origin_y]
				self.redraw()

			elif self.mode in (self.SELECT, self.BOND):
				new_hover = None
				for key in self.molecule.atoms.keys():
					atom = self.molecule.atoms[key]
					if (x >= atom.x and x <= atom.x + atom.layout_width and
								y >= atom.y and y <= atom.y + atom.layout_height):  # + atom.label_height):
						self.window1.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.HAND1))
						new_hover = key
						break

				if self.hover is not None and new_hover is None:
					self.window1.window.set_cursor(None)
				self.hover = new_hover

		elif self.grab:
			if self.mode == self.SELECT:
				# the atom we picked is selected already
				atom = self.molecule.atoms[self.grab]
				if self.molecule.atoms[self.grab] in self.selection:
					atoms = self.selection[:]
					atoms.remove(atom)
				else:
					atoms = []

				old_x, old_y = atom.x, atom.y
				atom.x = x - self.grab_offset_x
				atom.y = y - self.grab_offset_y
				diffX = old_x - atom.x
				diffY = old_y - atom.y
				if atoms and len(atoms) > 0:
					for a in atoms:
						a.x -= diffX
						a.y -= diffY

				self.redraw()
			elif self.mode == self.BOND:
				atom = self.molecule.atoms[self.grab]
				self.line_from = [atom.x + atom.layout_width, atom.y + atom.layout_height]
				self.line_to = [x, y]
				self.redraw()

	def on_window1_button_release_event(self, widget, event):
		dx = self.drawing.allocation.x
		dy = self.drawing.allocation.y
		x, y, mask = widget.window.get_pointer()
		x -= dx
		y -= dy

		if len(self.selection_box) == 2:
			self.selection = []
		elif len(self.selection_box) == 4:
			x1 = self.selection_box[0]
			y1 = self.selection_box[1]
			x2 = self.selection_box[2] + x1
			y2 = self.selection_box[2] + y1
			self.selection = []

			for key in self.molecule.atoms.keys():
				atom = self.molecule.atoms[key]
				if (atom.x >= x1 and atom.x <= x2 and
							atom.y >= y1 and atom.y <= y2):
					self.selection.append(atom)

		self.selection_box = []

		if x >= 0 and y >= 0:
			if self.mode == self.SELECT:
				if self.snap_to_grid:
					if self.selection:
						self.snap_atoms(self.selection)
					elif self.grab:
						self.snap_atoms([self.molecule.atoms[self.grab]])
				self.grab = None

			elif self.mode == self.ADD_ATOM:
				e = self.place_element
				if self.snap_to_grid:
					x = x // 20 * 20
					y = y // 20 * 20
				else:
					x -= 10
					y -= 10
				self.molecule.add_atom(e, e.symbol + str(self.num), x, y)
				self.num += 1

			elif self.mode == self.DEL_ATOM:
				for key in self.molecule.atoms.keys():
					atom = self.molecule.atoms[key]
					if (x >= atom.x and x <= atom.x + atom.layout_width and
								y >= atom.y and y <= atom.y + atom.layout_height):
						self.molecule.remove_atom(key)

			elif self.mode == self.BOND:
				for key in self.molecule.atoms.keys():
					atom = self.molecule.atoms[key]
					if (x >= atom.x and x <= atom.x + 20 and
								y >= atom.y and y <= atom.y + 20):
						self.molecule.add_bond(self.molecule.atoms[self.grab].label, atom.label, Bond.SINGLE)
						break

				self.grab = None

			self.redraw()

	def on_menuSnap_toggled(self, widget):
		self.snap_to_grid = not self.snap_to_grid

	def on_menuShowGrid_toggled(self, widget):
		self.show_grid = not self.show_grid
		self.redraw()

	def on_menuShowLabels_toggled(self, widget):
		self.show_labels = not self.show_labels
		self.redraw()

	def on_menuPreferences_activate(self, widget):
		self.winPreferences.show()

	def on_menuAssignElectrons_activate(self, widget):
		results = self.molecule.assign_electrons()
		if results:
			self.buttonbox.set_visible(True)
			self.lblNumConfigurations.set_visible(True)

			self.results = results
			self.lblNumConfigurations.set_text("%d / %d" % (1, len(self.results)))
			self.current_configuration = 1
			self.molecule = self.results[0]
			self.results = self.results[1:]
			self.redraw()
		else:
			self.buttonbox.set_visible(False)
			self.lblNumConfigurations.set_visible(False)

			md = gtk.MessageDialog(parent=self.window1, type=gtk.MESSAGE_WARNING, buttons=gtk.BUTTONS_CLOSE,
									message_format="Not enough electrons to fill all valence shells")
			md.run()
			md.destroy()

	def on_btnAssignElectrons_clicked(self, widget):
		self.on_menuAssignElectrons_activate(widget)

	def on_btnNew_clicked(self, widget):
		self.molecule = Molecule()
		self.results = []
		self.redraw()

	def on_btnNext_clicked(self, widget):
		if self.results:
			self.current_configuration += 1
			if self.current_configuration > len(self.results) + 1:
				self.current_configuration = 1
			self.lblNumConfigurations.set_text("%d / %d" % (self.current_configuration, len(self.results) + 1))

			self.results.append(self.molecule)
			self.molecule = self.results[0]
			self.results = self.results[1:]
			self.redraw()

	def on_btnPrev_clicked(self, widget):
		if self.results:
			self.current_configuration -= 1
			if self.current_configuration == 0:
				self.current_configuration = len(self.results) + 1
			self.lblNumConfigurations.set_text("%d / %d" % (self.current_configuration, len(self.results) + 1))

			self.results.insert(0, self.molecule)
			self.molecule = self.results[-1]
			self.results = self.results[:-1]
			self.redraw()