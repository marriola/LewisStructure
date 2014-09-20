class EditorBase(object):
	SELECT = 0
	ADD_ATOM = 1
	DEL_ATOM = 2
	BOND = 3

	def __init__(self):
		self.num = 1
		self.mode = self.SELECT
		self.place_element = None
		self.grab = None
		self.grab_offset_x = self.grab_offset_y = -1
		self.hover = None
		self.table_hover = None
		self.selection = []
		self.selection_box = []
		self.snap_to_grid = True
		self.show_grid = False
		self.show_labels = True
		self.current_configuration = 0

		self.molecule = None
		self.elements = None
		self.table_image = None
		self.gladefile = None
		self.glade = None
		self.window1 = None
		self.winPreferences = None
		self.drawing = None
		self.buttonbox = None
		self.lblNumConfigurations = None
		self.tableDialog = None
		self.periodicTable = None
		self.btnSelect = None
		self.btnAdd = None
		self.btnRemove = None
		self.btnBond = None