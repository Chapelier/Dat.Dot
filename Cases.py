

class Cases(object):

	default_car = {'X' : "Wall",
			' ' : "Path",
			'I' : "Info",
			'E' : "Exit",
			'C' : "Switch",
			'T' : "Tp",
			'B' : "Player"}
	default_color = {"Wall": "black",
					"Path": "white",
					"Info": "blue",
					"Exit": "green",
					"Switch": "orange",
					"Tp": "violet",
					"Player": "blue"}

	def __init__(self, tk_case=None):
		self.img = tk_case
		self.color = ""
		self.car = ''

	def __repr__(self):
		return self.__class__.__name__

	def __eq__(self, obj):
		return obj == self.__class__.__name__

	def reverse(self):
		if self == "Wall":
			return Path(self.img)
		else:
			return Wall(self.img)

class Wall(Cases):

	def __init__(self, tk_case=None):
		Cases.__init__(self, tk_case)
		self.color = Cases.default_color["Wall"]

class Path(Cases):

	def __init__(self, tk_case=None):
		Cases.__init__(self, tk_case)
		self.color = Cases.default_color["Path"]

class Info(Cases):

	def __init__(self, name, message, tk_case=None):
		Cases.__init__(self, tk_case)
		self.name = name
		self.message = message
		self.color = Cases.default_color["Info"]

	def seeMe(self):
		try:
			from tkinter.filedialog import messagebox, colorchooser
		except ImportError:
			from tkinter import messagebox, colorchooser

		title = self.name
		msg = self.message
		icone = "info"
		messagebox.showinfo(title, msg, icon=icone)

	@classmethod
	def fromLine(cls, line):
		line = line.replace('&', '\n')
		end = line.index(')')
		name, message = line[1:end], line[end+1:]
		return cls(name, message)

class Exit(Cases):

	def __init__(self, tk_case=None):
		Cases.__init__(self, tk_case)
		self.color = Cases.default_color["Exit"]

class Switch(Cases):

	def __init__(self, uses, L_cases, tk_case=None):
		Cases.__init__(self, tk_case)
		self.uses = uses
		self.cases_to_change = L_cases
		self.color = Cases.default_color["Switch"]

	@classmethod
	def fromLine(cls, line):
		end = line.index(']')
		uses, case_to_change = int(line[1:end]), line[end+1:].split(' ')
		return cls(uses, [eval(x) for x in case_to_change])

class Tp(Cases):

	def __init__(self, destination, tk_case=None):
		Cases.__init__(self, tk_case)
		self.destination = destination
		self.color = Cases.default_color["Tp"]

	@classmethod
	def fromLine(cls, line):
		return cls(eval(line))

class Player(Cases):

	def __init__(self, tk_case, x, y):
		Cases.__init__(self, tk_case)
		self.color = Cases.default_color["Player"]
		self.x = x
		self.y = y

	def __repr__(self):
		return "Player " + self.color + " at ({}, {})".format(self.x, self.y)