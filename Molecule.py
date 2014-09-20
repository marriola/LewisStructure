from __future__ import print_function
import copy
from Atom import Atom
from Bond import Bond


class Molecule:
	def __init__(self):
		self.atoms = {}
		self.bonds = []
		self.total_bonding = 0
		self.total_valence = 0

	# self.lastNumber = 1

	def __hash__(self):
		return hash(tuple(self.atoms)) | hash(tuple(self.bonds)) | hash(self.total_valence) | hash(self.total_bonding)

	def __eq__(self, other):
		if (len(other.atoms) != len(self.atoms) or
					len(other.bonds) != len(self.bonds) or
					other.total_bonding != self.total_bonding or
					other.total_valence != self.total_valence):
			return False

		for key in self.atoms.keys():
			if key not in other.atoms.keys() or not self.atoms[key].equals(other.atoms[key]):
				return False

		self_bonds_set = set(["%s%s%d" % (bond.atom1, bond.atom2, bond.type) for bond in self.bonds])
		other_bonds_set = set(["%s%s%d" % (bond.atom1, bond.atom2, bond.type) for bond in other.bonds])
		# print("COMPARE", self_bonds_set, other_bonds_set)
		if self_bonds_set != other_bonds_set:
			return False
		"""for bond in self.bonds:
			found = False
			for x in other.bonds:
				if x.equals(bond):
					found = True
					break
			if not found:
				return False"""

		#print("GREAT SUCCESS")

		return True

	def __ne__(self, other):
		return not self.__eq__(other)

	def __lt__(self, other):
		return False

	def __le__(self, other):
		return False

	def __gt__(self, other):
		return False

	def __ge__(self, other):
		return False

	def add_atom(self, element, label, x, y):
		"""Adds an atom to the molecule"""

		self.atoms[label] = Atom(label, element, x, y)
		self.total_valence += element.valence

	def remove_bond(self, atom1, atom2):
		"""Removes a bond between two atoms, if it exists"""

		remove = []
		for bond in self.bonds:
			if ((bond.atom1 == atom1 and bond.atom2 == atom2) or
					(bond.atom1 == atom2 and bond.atom2 == atom1)):
				remove.append(bond)

		for x in remove:
			self.bonds.remove(x)

	def remove_atom(self, label):
		"""Removes an atom from the molecule as well as its associated bonds"""

		# delete all bonds involving this atom
		remove_list = []
		for bond in self.bonds:
			if label in (self.atoms[bond.atom1].label, self.atoms[bond.atom2].label):
				remove_list.append(bond)
		for bond in remove_list:
			self.bonds.remove(bond)

		# decrement total valence electron count
		self.total_valence -= self.atoms[label].element.valence

		# delete the atom
		del self.atoms[label]

	def remove_nonbonding_electrons(self, label, n):
		"""Strips the molecule of its nonbonding electrons"""

		for key in self.atoms.keys():
			atom = self.atoms[key]
			if atom.label == label and atom.nonbonding_electrons >= n:
				atom.nonbonding_electrons -= n
				return True
		return False

	def add_bond(self, atom1, atom2, type):
		"""Adds a bond to the molecule

		atom1	Label of the first atom to bond
		atom2	Label of the second atom to bond
		:type	Type of bond (Bond.SINGLE, Bond.DOUBLE, Bond.TRIPLE)
		"""
		self.bonds.append(Bond(atom1, atom2, type))
		self.total_bonding += 2 * type

	def promote_bond(self, atom1, atom2):
		"""Increments the bond type between two atoms. Returns false if the specified atoms do not exist or are not bonded."""

		for bond in self.bonds:
			if ((atom1 == bond.atom1 and atom2 == bond.atom2) or
					(atom1 == bond.atom2 and atom2 == bond.atom1)):
				bond.type += 1
				return True
		return False

	def num_bonding_electrons(self, label):
		"""Counts the number of bonding electrons on an atom"""
		total = 0

		for bond in self.bonds:
			if label in (bond.atom1, bond.atom2):
				total += 2 * bond.type

		return total

	def formal_charge(self, label):
		"""Calculates the formal charge on an atom"""

		atom = self.atoms[label]
		bonding_pairs = (self.num_bonding_electrons(label) // 2)
		return atom.element.valence - atom.nonbonding_electrons - bonding_pairs

	def total_absolute_formal_charge(self):
		"""Sums the formal charges of each atom in the molecule. This function is used to sort generated molecule
		configurations by stability. That is, configurations with the most neutral electronic configuration will
		appear first."""

		total_charge = 0
		for atom in self.atoms:
			charge = abs(self.formal_charge(atom))
			total_charge += charge
		# print("total charge", total_charge)
		return total_charge

	def partial_charge(self, bond, reverse=False):
		"""Calculates the partial charge on an atom"""

		atom1 = bond.atom1
		atom2 = bond.atom2
		if reverse:
			atom1, atom2 = atom2, atom1
		unpaired_valence = atom1.element.valence - atom1.nonbonding_electrons - self.num_bonding_electrons(atom1)
		return unpaired_valence * atom1.element.AVEE / (atom1.element.AVEE + atom2.element.AVEE)

	def neighbors(self, label):
		"""Returns a list of atoms bonded to an atom.

		label	The label of the atom to examine"""

		results = []

		for bond in self.bonds:
			if label == bond.atom1:
				results.append(bond.atom2)
			elif label == bond.atom2:
				results.append(bond.atom1)

		return results

	def generate_bond_configurations(self, molecule, visited=None):
		"""Moves nonbonding electrons into double or triple bonds with atoms
		that have unfilled valence shells, generating all possible combinations
		recursively."""
		results = []
		if not visited:
			visited = set()

		for label in molecule.atoms:
			atom = molecule.atoms[label]
			full_shell = 2 if atom.element.symbol == "H" else 8
			total_electrons = atom.nonbonding_electrons + molecule.num_bonding_electrons(label)

			if total_electrons < full_shell:
				# this atom's valence shell is unfilled
				# iterate through neighboring atoms
				for neighbor in molecule.neighbors(atom.label):
					next_state = copy.deepcopy(molecule)
					# if we can take 2 non-bonding electrons from this atom,
					# transfer them to the bond
					if next_state.remove_nonbonding_electrons(neighbor, 2):
						print("share 2 electrons between %s and %s" % (label, neighbor))
						next_state.promote_bond(atom.label, neighbor)
						results.append(next_state)
						if next_state not in visited:
							visited.add(next_state)
							for r in self.generate_bond_configurations(next_state, visited):
								results.append(r)

		return results

	def has_unfilled_valence_shells(self, molecules):
		for m in molecules:
			for key in m.atoms.keys():
				atom = m.atoms[key]
				full_shell = 2 if atom.element.symbol == "H" else 8
				total_electrons = atom.nonbonding_electrons + m.num_bonding_electrons(key)

				if total_electrons < full_shell:
					return True

		return False

	def does_not_contain(self, list, item):
		for x in list:
			if x == item:
				return False
		return True

	def generate_nonbonding_electron_configurations(self, molecule, remaining_electrons, added="", spaces=0):
		"""Generates all possible configurations of nonbonding electrons for a molecule.

		molecule				A Molecule object to be completed
		remaining_electrons		The number of electrons available to be placed in the molecule"""

		results = set()
		keys = molecule.atoms.keys()
		key_index = 0
		num_keys = len(keys)

		while remaining_electrons > 0:
			last = remaining_electrons
			for label in keys:
				atom = molecule.atoms[label]
				full_shell = 2 if atom.element.group == 1 else 8
				num_bonding = molecule.num_bonding_electrons(label)
				needs = full_shell - num_bonding - atom.nonbonding_electrons

				if needs - 2 >= 0:
					for i in range(spaces):
						print(end=" ")
					print("assign 2 to %s (needs %d, %d remain) [%s]" %
							(label, needs - 2, remaining_electrons - 2, added))

					atom_copy = copy.deepcopy(atom)
					atom_copy.nonbonding_electrons += 2
					molecule_copy = copy.deepcopy(molecule)
					molecule_copy.atoms[label] = atom_copy
					if remaining_electrons:
						children = self.generate_nonbonding_electron_configurations(molecule_copy,
																					remaining_electrons - 2,
																					added + " %s" % label, spaces + 2)
						print(len(results))
						results = results.union(children)
						print(len(results))
						"""for configuration in children:
							#if self.does_not_contain(results, configuration):
							#if configuration not in results:
							results.add(configuration)
							#else:
							#	print("rejected")"""

			if remaining_electrons == last:
				return list(results) if spaces == 0 else results

		results.add(molecule)
		return list(results) if spaces == 0 else results

	def remove_incomplete_configurations(self, configurations, remaining_electrons):
		"""Remove all molecular configurations that haven't had all available electrons assigned.

		configurations			A list of Molecule objects to filter
		remaining_electrons		The number of electrons available to be placed"""

		remove = set()
		for molecule in configurations:
			total_nonbonding = 0
			for label in molecule.atoms.keys():
				atom = molecule.atoms[label]
				total_nonbonding += atom.nonbonding_electrons
			if total_nonbonding < remaining_electrons:
				remove.add(molecule)

		for x in remove:
			configurations.remove(x)
		# results -= remove
		return configurations

	def assign_electrons(self):
		total_valence = self.total_valence
		total_bonding = self.total_bonding
		remaining_electrons = total_valence - total_bonding

		"""print("%d total valence electrons\n" \
				"%d total bonding electrons\n" \
				"%d available electrons" % (total_valence, total_bonding, remaining_electrons))"""

		for bond in self.bonds:
			bond.type = Bond.SINGLE
		for label in self.atoms.keys():
			self.atoms[label].nonbonding_electrons = 0

		# generate all ways to place available nonbonding electrons on the molecule
		molecules = self.generate_nonbonding_electron_configurations(self, remaining_electrons)
		molecules = self.remove_incomplete_configurations(molecules, remaining_electrons)

		# identify atoms with unfilled outer shells
		# share electrons with nearby atoms and move electrons from atom to atom
		results = []

		for m in molecules:
			out = [m]
			while self.has_unfilled_valence_shells(out):
				# print(results)
				molecule = out[0]
				#print("while", molecule)
				out.remove(molecule)
				add = self.generate_bond_configurations(molecule)
				for r in add:
					out.append(r)

			for x in out:
				if len(results):
					for y in results:
						if x != y:
							results.append(x)
							break
				else:
					results.append(x)

		# sort configurations by stability (in increasing order of summed absolute formal charges)
		return sorted(results, key=lambda x: x.total_absolute_formal_charge())