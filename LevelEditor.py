	
"""
Editeur de niveaux de DAT.DOT
"""

import os
from tkinter import *
import ctypes
from tkinter import messagebox
from tkinter.filedialog import askopenfilename
from math import sqrt
from Cases import *
from Levels import Level
from Pallet import Pallet
from Cases import *

SCREEN_INFO_X = ctypes.windll.user32.GetSystemMetrics(0)
SCREEN_INFO_Y = ctypes.windll.user32.GetSystemMetrics(1)

class CheckingError(Exception):
	pass

class Message(Message):
	def get(self):
		return self.cget('text')

def disabled(func):
	return lambda *var: print("Something awesome is coming soon, please wait :)")

class Interface_LevelEditor():

	def __init__(self):
		self.window = Tk()
		self.window.title("LevelEditor")
		self.window.resizable(False, False)

		phi = (1+sqrt(5)) / 2
		self.width_window, self.height_window = int(SCREEN_INFO_X / (phi*0.9)), int(SCREEN_INFO_Y / (phi*0.9))
		# Position de l'écran
		dx, dy = int((SCREEN_INFO_X-self.width_window)/2), int((SCREEN_INFO_Y-self.height_window)/2)
		self.window.geometry("{}x{}+{}+{}".format(self.width_window, self.height_window, dx, dy))

		self.window.protocol("WM_DELETE_WINDOW", lambda: self.escape())
		self.window.config(bg='#9af4fc')
		self.window.focus_force()

		self.width_grid = self.width_window * 0.75
		self.height_grid = int(self.height_window)
		# Taille de la palette
		self.width_pallet = self.width_window * 0.25
		self.height_pallet = self.height_window * 0.6
		# Case en mémoire en modification void
		self.current_case = None
		# Variable de contrôle
		self.in_work = False

		self.grid = Canvas(self.window, bg='#9af4fc')
		self.tools = Frame(self.window, bg='#9af4fc')

		self.type_of_cases, colors = [], []
		for i in Cases.default_color.keys():
			colors.append(Cases.default_color[i])
			self.type_of_cases.append(i)
			if i == "Player":
				colors[-1] = '&' + colors[-1]
		colors.append("#black")
		self.type_of_cases.append("void")
		self.pallet = Pallet(self.tools, buttons_color=colors, bg='#9af4fc', width=self.width_pallet, height=self.height_pallet)
		self.pallet.bind('<1>', lambda var: self.palletEvent())
		self.save = Button(self.tools, text='Save level', bg='lightgreen', command=self.saveLevel)
		self.carac = Frame(self.tools, bg='#9af4fc')
		self.F_entry = None

		self.grid.pack(side=LEFT)
		self.carac.pack(side=BOTTOM)
		
		# self.is_full_screen = False
		self.level = None
		self.menu()
		self.window.mainloop()

	def menu(self):
		"""
		Affiche le menu, les différents texte et efface
		toutes les frame inutiles
		"""

		self.in_work = False

		# On utilise plus toutes les fonctions liées à
		# la création de niveau
		keys = ['<1>', '<3>']
		for i in keys:
			self.grid.unbind(i)
		keys = ['<Control-m>']
		for i in keys:
			self.window.unbind(i)

		# On efface toutes les frames inutiles
		self.save.pack_forget()
		self.tools.pack_forget()
		self.clean(self.carac)
		self.grid.delete(ALL)
		self.grid.config(width=self.width_window, height=self.height_window)

		self.window.bind('<Escape>', lambda var : self.escape())
		self.window.bind('<c>', self.initialiseLevel)
		self.window.bind('<e>', self.initialiseLevel)

		msg = [("Press Escape anywhere to quit", "blue"),
					("Press Ctrl+M to return on here", "black"),
					("Press C to create a new level", "blue"),
					("Press E to edit an existant level", "black")]
		mid = self.width_window / 2, self.height_window / 2
		current_aff = len(msg) // 2

		for i in range(len(msg)):
			txt, color = msg[i]
			self.grid.create_text(mid[0], mid[1]-20*current_aff, text=txt, fill=color,
									state="disabled", font=('', 11))
			current_aff -= 1

	def initialiseLevel(self, var):

		if var.keysym == 'c': # create a level
			# Take the default one
			self.level = Level.fromFile("data/default_level.lvl")
		elif var.keysym == 'e': #edit a level
			# search the level
			d = '.lvl'
			f = [("LEVEL","*.lvl")]
			i = 'Level *.lvl'
			t = "Select witch level to edit"
			init_f = os.getcwd() + '\\levels\\user'
			file = askopenfilename(defaultextension=d, filetypes=f,
								initialfile=i, title=t, initialdir=init_f)

			if file == '':
				# Sécurité si aucun fichier sélectionné
				return FileNotFoundError

			self.level = Level.fromFile(file)

		self.current_case = self.level
		self.edit()

	def edit(self):
		"""
		Initialise l'écran d'édition
		"""

		self.window.unbind('<e>')
		self.window.unbind('<c>')

		self.save.pack(pady=10)
		self.grid.delete(ALL)
		self.grid.config(height=self.height_grid, width=self.width_grid)
		self.grid.update()
		self.tools.pack()
		self.pallet.pack(side=TOP)
		self.pallet.update()
		self.pallet.draw()
		self.level.canvas = self.grid
		self.level.draw()

		self.window.bind('<Control-m>', lambda var: self.menu())
		self.grid.bind('<1>', lambda var: self.gridClic1())
		self.grid.bind('<3>', lambda var: self.gridClic2())
		self.in_work = True

		self.showInfo(self.level)

	def escape(self):
		"""
		Quitter en vérifiant si l'utilisateur ne va pas perdre son travail
		"""
		if self.in_work:
			title = "Warning"
			txt = "Si vous quittez maintenant, tout vos changements seront perdus !"
			icone = 'warning'
			asw = messagebox.askokcancel(title, txt, icon=icone)
			if asw:
				self.window.destroy()
		else:
			self.window.destroy()

	##################### Event #####################

	def gridClic1(self):
		"""
		Quand on clic gauche sur grid
		"""

		case_x, case_y = map(int, self.findCaseClic())

		void = self.pallet.button_number == len(self.type_of_cases)-1
		same_color = self.level.grid[case_x][case_y] == self.type_of_cases[self.pallet.button_number]
		is_in_case = (case_x, case_y) != (-1, -1)
		is_selected = self.pallet.button_number != -1

		if void:
			# Si on clique en étant dans le mode 'void',
			# on affiche les données de la case (si elle
			# est spéciale) pour que l'utilisateur controle
			case = self.level.grid[case_x][case_y]
			if case in ['Tp', 'Info', 'Switch']:
				self.showInfo(case)
				self.current_case = case
				self.current_case_coords = case_x, case_y
				if case in ['Tp', 'Info']:
					drawDatas() #case, case_x, case_y, datas
					pass

		elif is_selected and is_in_case and not(same_color) and self.level.grid[case_x][case_y] != 'Player':
			# Sinon, on change la case par celle en selection dans palette
			case = self.type_of_cases[self.pallet.button_number]
			# On doit mettre chaque paramètre pour l'init des cases
			# On marque neanmoins qu'elles sont vides
			if case == 'Info' or case == 'Switch':
				self.level.grid[case_x][case_y] = eval(case + "(None, None)")
				self.level.grid[case_x][case_y].empty = True
			elif case == 'Tp':
				self.level.grid[case_x][case_y] = Tp(None)
				self.level.grid[case_x][case_y].empty = True
			elif case == 'Player':
				self.level.grid[self.level.player.x][self.level.player.y] = Path()
				player = Player(self.level.player.img, case_x, case_y)
				self.level.grid[case_x][case_y] = player
				self.level.player = player
			else:
				self.level.grid[case_x][case_y] = eval(case + "()")

			self.level.draw()

	def gridClic2(self):
		"""
		Quand on clic droit sur grid, on efface ce qui
		ce trouve sur la case visée (sauf si c'est le joueur)
		"""

		case_x, case_y = map(int, self.findCaseClic())
		if (case_x, case_y) == (-1, -1):
			return "Case no found"
		case = self.level.grid[case_x][case_y]
		if case != 'Player':
			self.level.grid[case_x][case_y] = Path()
			self.level.draw()

	def gridClic2Void(self):
		"""
		Quand on clic droit sur grid avec void sélectionnée
		on enregistre les cordonnées de la case
		"""

		case_x, case_y = map(int, self.findCaseClic())
		datas = [widget for widget in self.F_entry.winfo_children()]
		message = datas[-1]
		repr_case = "{},{}".format(case_x, case_y)
		deja_vue =  "({})".format(repr_case) in message.get()

		if deja_vue:
			self.level.canvas.itemconfig(repr_case, outline="black", width=1)
			message.config(text=message.get().replace("({})".format(repr_case)+'&', ''))

		if not deja_vue and self.current_case == "Switch":
			self.level.canvas.itemconfig(repr_case, outline="blue", width=5)
			self.level.canvas.tag_raise(repr_case)
			message.config(text=message.get() + "({})".format(repr_case) + '&')
		elif self.current_case == "Tp":
			if message.get() != '':
				old = eval(message.get())
				self.level.canvas.itemconfig("{},{}".format(old[0], old[1]), outline="black", width=1)
			self.level.canvas.itemconfig(repr_case, outline="blue", width=5)
			self.level.canvas.tag_raise(repr_case)
			message.config(text="({})".format(repr_case))

	def palletEvent(self):
		event = self.pallet.leftClic()

		if event == "leave void tool" or event == "void changed":
			self.grid.bind('<3>', lambda var: self.gridClic2())
			self.showInfo(self.level)
		elif event == "void selected":
			self.grid.bind('<3>', lambda var: self.gridClic2Void())
			pass


	def findCaseClic(self):
		"""
		On cherche quelle case est visée dans le canvas grid
		"""

		id_rect = self.grid.find_withtag(CURRENT)
		if len(id_rect) == 0:
			# No case found
			return (-1, -1)
		tags = self.grid.gettags(id_rect[0])
		if tags[0] == "current":
			return tags[1].split(',')
		else:
			return tags[0].split(',')

	def message(self, txt):
		"""
		Afficher un message pendant 8 secondes avec txt affiché
		"""
		m = Message(self.window, text=txt, width=200, bg="lightgreen", fg="black")
		m.place(x=self.width_window/2, y=20, anchor=CENTER)
		self.window.after(5000, m.destroy)

	def showInfo(self, case):
		"""
		Affiche une frame avec les caractéristiques du type demandé
		"""
		self.clean(self.carac)
		links = {'Level' : (("Level width :", "Level height :", "Name :"), ('width', 'height', 'name')),
				'Info' : (("Name :", "Message :"), ('name', 'message')),
				'Tp' : (("End case :",), ('destination',)),
				'Switch' : (("Number of uses :", "cases to change :"), ('uses', 'cases_to_change'))
				}

		txt_label, infos = links[case.__class__.__name__]

		# Tout est contenu dans une grande Frame, pour éviter
		# tout bug lié au placement
		big_frame = Frame(self.carac, bg='#9af4fc')
		big_frame.pack(side=TOP)
		F_txt = Frame(big_frame, bg='#9af4fc')
		F_txt.pack(side=LEFT)
		self.F_entry = Frame(big_frame, bg='#9af4fc')
		self.F_entry.pack(side=RIGHT)

		for txt in txt_label:
			Label(F_txt, text=txt, bg='#9af4fc', fg="blue").pack(pady=5)

		for i in infos[:-1]:
			Entry(self.F_entry).pack(pady=5)
		if case == 'Info' or case.__class__.__name__ == "Level":
			Entry(self.F_entry).pack(pady=5)
		else:
			Message(self.F_entry).pack(pady=5)

		b = Button(self.carac, text='Save changes', command=lambda: self.saveChanges())
		b.pack(side=BOTTOM, pady=10)

		if case.__class__.__name__ == "Level":
			level = case
			infos = [len(level.grid), len(level.grid[0]), level.name]
			i = 0
			for entry in self.F_entry.winfo_children():
				entry.insert(0, infos[i])
				i += 1
		else:
			i = 0
			for entry in self.F_entry.winfo_children():
				try:
					entry.insert(0, str(getattr(case, str(infos[i]))))
				except:
					entry.config(text=str(getattr(case, str(infos[i]))))
				i += 1

	def saveChanges(self):
		"""
		Sauvegarde des modifications du niveau ou des données d'une case
		"""
		# global L_var, matrice, name, donnees
		datas = [widget.get() for widget in self.F_entry.winfo_children()]

		if self.current_case.__class__.__name__ == "Level":
			try:
				# L'utilisateur a bien mis un entier > 3
				datas[0] = int(datas[0])
				if datas[0] < 3:
					raise ValueError
			except ValueError:
				self.message("Width must be an integer > 3")
			else:
				if datas[0] != len(self.level.grid[0]):
					# Si il y a eu un changement, on rajoute ou
					# enleve 'dif' lignes dans la grille du niveau
					dif = datas[0]-len(self.level.grid[0])
					if datas[0] > len(self.level.grid[0]):
						for ligne in self.level.grid:
							ligne += [Wall()] * dif
					else:
						for ligne in range(len(self.level.grid)):
							self.level.grid[ligne] = self.level.grid[ligne][:dif]
					for ligne in self.level.grid:
						ligne[-1] = Wall()
					self.level.grid[0] = [Wall()] * len(self.level.grid[0])
					self.level.grid[-1] = [Wall()] * len(self.level.grid[-1])
					self.message("Level updated successfully")

			try:
				# L'utilisateur a bien mis un entier > 3
				datas[1] = int(datas[1])
				if datas[1] < 3:
					raise ValueError
			except ValueError:
				self.message("Height must be an integer > 3")
			else:
				if datas[1] != len(self.level.grid):
					# Si il y a eu un changement, on rajoute ou
					# enleve 'dif' colonnes dans la grille du niveau
					dif = datas[1]-len(self.level.grid)
					if datas[1] > len(self.level.grid):
						for _ in range(dif):
							self.level.grid.append([Path() for _ in range(len(self.level.grid[0]))])
					else:
						self.level.grid = self.level.grid[:dif]
					for ligne in self.level.grid:
						ligne[0] = Wall()
						ligne[-1] = Wall()
					self.level.grid[0] = [Wall()] * len(self.level.grid[0])
					self.level.grid[-1] = [Wall()] * len(self.level.grid[-1])
					self.message("Level updated successfully")

			if datas[2] != '' and self.level.name != datas[2]:
				self.level.name = datas[2]
		else:
			attributes = {'Info' : ('name', 'message'),
								'Tp' : ('destination',),
								'Switch' : ('uses', 'cases_to_change')}
			i = 0
			for attr in attributes[self.current_case.__class__.__name__]:
				setattr(self.current_case, attr, datas[i])
				i += 1

			# Vérification
			if self.current_case == 'Tp':
				self.current_case.destination = eval(self.current_case.destination)
			elif self.current_case == 'Switch':
				self.current_case.cases_to_change = [eval(x) for x in self.current_case.cases_to_change.split('&') if x != '']
				self.current_case.uses = int(self.current_case.uses)
			empty = False
			for attr in attributes[self.current_case.__class__.__name__]:
				test = getattr(self.current_case, attr)
				if test == '':
					empty = True
					break
			self.current_case.empty = empty
			
			self.level.grid[self.current_case_coords[0]][self.current_case_coords[1]] = self.current_case
			self.message("Changes saved succesfully")

		self.level.draw()

	def saveLevel(self):
		"""
		Sauvegarde du niveau
		"""
		try:
			self.check()
		except CheckingError as error:
			messagebox.showerror('Error', error)
		else:
			if self.level.path == "data/default_level.lvl":
				# Dans le cas où on crée un niveau, on le met à la suite des autres
				nb = 1
				while os.path.exists(os.getcwd() + '\\levels\\user\\' + "Level {}.lvl".format(nb)):
					nb += 1
				self.level.path = os.getcwd() + '\\levels\\user\\' + "Level {}.lvl".format(nb)

			# try:
			self.level.save()
			# except:
			# 	messagebox.showerror('Error', "Can't save level")
			# else:
			titre, msg = 'Done', "Save succefull at {}".format(self.level.path)
			icone = "info"
			messagebox.showinfo(titre, msg, icon=icone)

			self.menu()

	def check(self):
		"""
		On vérifie si le niveau est conforme en tout point
		"""
		if self.level.name == '':
			# Le nom est vide
			raise CheckingError("Name of level is empty")

		for ligne in self.level.grid[0], self.level.grid[-1], [x[0] for x in self.level.grid], [x[-1] for x in self.level.grid]:
			for case in ligne:
				if case not in ('Wall', 'Exit'):
					# Le niveau n'est pas entouré de murs
					raise CheckingError("Edge must be Wall or Exit")

		exit = False
		start = False
		for ligne in self.level.grid:
			for case in ligne:
				if case.empty == True:
					raise CheckingError("There is an empty case")
				if case == 'Player':
					# On regarde s'il y a une sortie
					start = True
				if case == 'Exit':
					# et une case de départ
					exit = True

		if not exit:
			# Il n'y a pas de sortie
			raise CheckingError("Exit is missing")
		if not start:
			# Il n'y a pas de départ
			raise CheckingError("Dot-Start is missing")

	##################### Écran #####################

	"""
	Calcul de la taille de la fenêtre du jeu en fonction
	de la taille de l'écran
	"""

	screenAdaptator = lambda screen_x, screen_y: (int(screen_x / ((1+sqrt(5)) / 2)), int(screen_y / ((1+sqrt(5)) / 2)))
	screenAdaptator = staticmethod(screenAdaptator)

	@disabled
	def fullscreen(self):
		"""
		Cette fonction met ou enleve le plein écran
		"""
		if self.is_full_screen:
			self.window.attributes('-fullscreen', 0)
			self.width_window, self.height_window = self.screenAdaptator(SCREEN_INFO_X, SCREEN_INFO_Y)
			dx, dy = int((SCREEN_INFO_X-self.width_window)/2), int((SCREEN_INFO_Y-self.height_window)/2)
			self.window.geometry("{}x{}+{}+{}".format(self.width_window, self.height_window, dx, dy))
		else:
			self.window.attributes('-fullscreen', 1)
			self.height_window = ctypes.windll.user32.GetSystemMetrics(1)
			self.width_window = ctypes.windll.user32.GetSystemMetrics(0)
		self.is_full_screen = not(self.is_full_screen)
		self.canvas.config(width=self.width_window, height=self.height_window)
		self.canvas.update()

		# Chaque page s'adapte à l'écran, on relance donc
		# la page actuelle pour eviter les bugs graphiques
		if self.current_screen == 'menu':
			self.menu()
		elif self.current_screen == 'leveltype':
			self.levelType()
		elif self.current_screen == 'play':
			self.nextLevel(self.current_level)
		elif self.current_screen == 'passwordsMenu':
			height, width = self.height_window, self.width_window
			lab.place(y=height/2-75, x=width/2, anchor="center")
			E_password.place(y=height/2, x=width/2, anchor="center")
			B_valider.place(y=height/2+75, x=width/2, anchor="center")

	@staticmethod
	def clean(frame):
		"""
		Pour vider une frame sans la supprimer
		"""
		for w in frame.winfo_children():
			w.destroy()

##################### Events #####################

@disabled
def drawDatas(case, x, y, datas):
    """
    Permet de mettre en surbrillance les cases sélectionné
    pour une case spéciale comme change case
    """
    global Dic_selected
    if type(datas[-1]) is tuple:
        if not(type(datas[-1][-1]) is tuple):
            return "ERROR"
        data = [datas[-1]]
    elif type(datas[-1]) is list:
        data = datas[-1]
    for i in data:
        # Mise en surbrillance
        width, height = getGridInfos()
        echelle, delta_x, delta_y = find_scale_delta(height, width)
        x1, y1, x2, y2 = i[1]*echelle+delta_x, i[0]*echelle+delta_y, (i[1]+1)*echelle+delta_x, (i[0]+1)*echelle+delta_y
        Dic_selected[i] = grid.create_rectangle(x1, y1, x2, y2, fill=None, outline="blue", width=5)

Interface_LevelEditor()