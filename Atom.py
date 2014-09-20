__author__ = 'Matt Arriola'


class Atom:
	OK = 0
	ERROR = 1

	def __init__(self, label, element, x, y):
		self.label = label
		self.element = element
		self.x = x
		self.y = y
		self.layout_width = 0
		self.layout_height = 0
		self.nonbonding_electrons = 0
		self.status = self.OK

	def equals(self, atom):
		cond = (atom.label == self.label and
				atom.element.symbol == self.element.symbol and
				atom.nonbonding_electrons == self.nonbonding_electrons)
		return cond