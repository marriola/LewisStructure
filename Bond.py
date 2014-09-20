class Bond:
	SINGLE = 1
	DOUBLE = 2
	TRIPLE = 3

	def __init__(self, atom1, atom2, type):
		self.atom1 = atom1
		self.atom2 = atom2
		self.type = type

	def equals(self, bond):
		return (self.atom1 == bond.atom1 and self.atom2 == bond.atom2 and self.type == bond.type)