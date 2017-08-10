from Datas import Datas
from Cases import *

class Level(object):
	"""
	Objet "niveau" pour le jeu DAT.DOT
	"""

	##################### Lecture / écriture d'un fichier #####################
	
	@staticmethod
	def readLine(line, genre):
		"""
		On lit une line contenant des données
		"""

		if genre == 'info':
			return Info.fromLine(line)
		elif genre == 'switch':
			return Switch.fromLine(line)
		elif genre == 'tp':
			return Tp.fromLine(line)

	@classmethod
	def fromFile(cls, file):
		"""
		Ouvre un fichier de niveau et en extrait la grid,
		le nom du niveau et les données des cases
		"""
		if file == '':
			raise FileNotFoundError
		# Si le fichier existe, on l'ouvre et on met en mémoire
		# toutes les lignes
		with open(file) as file:
			lect = file.readlines()

		grid = []
		datas = Datas()
		# la première line correspond au nom du niveau
		name = lect[0].replace('\n', '')
		lect = lect[1:]

		for line in lect:
			if line[0] == '#':
				# Quand la line commence par le caractère '#', il s'agit de données
				# On sépare donc le type des informations
				genre, desc = line[1:].replace('\n', '').split(':')
				# On peut ensuite ajouter les information dans la superstructure datas
				datas[genre].append(Level.readLine(desc, genre))
			else:
				# Sinon, il s'agit de la description du niveau, que l'on stocke dans grid
				line = [x for x in line.replace('\n', '').upper()]
				grid.append(line)

		for i in range(len(grid)):
			for j in range(len(grid[0])):
				type_of_case = Cases.default_car[grid[i][j]]
				if type_of_case == "Wall" or type_of_case == "Path":
					grid[i][j] = eval(type_of_case + "()")
				elif type_of_case == "Info" or type_of_case == "Switch" or type_of_case == "Tp":
					grid[i][j] = datas[type_of_case.lower()][0]
					datas[type_of_case.lower()].remove(grid[i][j])
				elif type_of_case == "Exit":
					grid[i][j] = Exit()
				elif type_of_case == "Player":
					player = Player(None, j, i)
					grid[i][j] = player
					

		return Level(name, grid, player, file.name)

	def save(self):

		car = {}
		for key in Cases.default_car.keys():
			car[Cases.default_car[key]] = key

		with open(self.path, 'w') as file:
			file.write(self.name+'\n')

			datas = []
			for ligne in self.grid:
				for case in ligne:
					file.write(car[str(case)])
					if case in ('Tp', 'Info', 'Switch'):
						datas.append((str(case).lower(), case.toLine()))
				file.write('\n')

			for data in datas:
				file.write("#{type}:{content}\n".format(type=data[0], content=data[1]))

	##################### Général #####################

	def __init__(self, name, grid, player, path=None):
		self.name = name
		self.grid = grid
		self.player = player
		self.path = str(path)
		self.canvas = None

	def __repr__(self):
		strg = self.path + '\n' + self.name + '\n'
		for i in self.grid:
			for j in i:
				strg += str(j) + ' '
			strg += '\n'
		return strg

	def draw(self):
		"""
		Dessine le niveau et initialise les motif des cases
		"""

		for i in range(len(self.grid)):
			for j in range(len(self.grid[0])):
				# Voici les coordonnées de la case à afficher
				cords = self.coordonnees(j, i)
				self.canvas.create_rectangle(cords[0][0], cords[0][1],
						cords[1][0], cords[1][1], fill="white")
				if self.grid[i][j] == "Player":
					self.grid[i][j].img = self.canvas.create_oval(cords[0][0]+5, cords[0][1]+5,
						cords[1][0]-5, cords[1][1]-5, fill=self.grid[i][j].color, width=3)
				else:
					self.grid[i][j].img = self.canvas.create_rectangle(cords[0][0], cords[0][1],
						cords[1][0], cords[1][1], fill=self.grid[i][j].color,
						tag="{},{}".format(i, j))

	def movePlayer(self, cap):
		Up = 0, -1
		Down = 0, 1
		Left = -1, 0
		Right = 1, 0

		changes = eval(cap.keysym)
		x = self.player.x + changes[0]
		y = self.player.y + changes[1]

		if 0 <= y < len(self.grid) and 0 <= x < len(self.grid[0]):
			# Si le déplacement se fait à l'interieur self.grid
			cur_case = self.grid[y][x]
			if cur_case != 'Wall':
				# Si la case n'est pas un mur, on peut déplacer player
				self.player.x, self.player.y = x, y
				cords = self.coordonnees(self.player.x, self.player.y)
				self.canvas.coords(self.player.img, cords[0][0]+5, cords[0][1]+5, cords[1][0]-5, cords[1][1]-5)
				self.canvas.tag_raise(self.player.img)
				self.canvas.update()
				if cur_case == 'Exit':
					return "end"
				elif cur_case == 'Switch':
					# Case change_case, on effectue les changements de cases
					# self.grid = changeCases(self.grid, donnees.switch[cur_case][1])
					for i in cur_case.cases_to_change:
						self.grid[i[0]][i[1]] = self.grid[i[0]][i[1]].reverse()
						self.canvas.itemconfigure(self.grid[i[0]][i[1]].img, fill=self.grid[i[0]][i[1]].color)
					# Et on diminue le nombre d'utilisations
					self.grid[y][x].uses -= 1
					if self.grid[y][x].uses <= 0:
						# Si la case est au bout de ses utilisations, on l'efface
						self.grid[y][x] = Path(self.grid[y][x].img)
						self.canvas.itemconfigure(self.grid[y][x].img, fill=self.grid[y][x].color)
					return "switch"
				elif cur_case == 'Tp':
					# Case de téléportation, on déplace une 2e fois player
					self.player.x, self.player.y = cur_case.destination[0], cur_case.destination[1]
					cords = self.coordonnees(self.player.x, self.player.y)
					self.canvas.coords(self.player.img, cords[0][0]+5, cords[0][1]+5, cords[1][0]-5, cords[1][1]-5)
					self.canvas.tag_raise(self.player.img)
					self.canvas.update()
					# Puis on efface la case (elle ne sert qu'une fois)
					self.grid[y][x] = Path(self.grid[y][x].img)
					self.canvas.itemconfigure(self.grid[y][x].img, fill=self.grid[y][x].color)
					return "tp"
				elif cur_case == 'Info':
					# Case info
					self.grid[y][x].seeMe()
		return False

		##################### Echelle et placement #####################

	##################### Placement #####################

	def coordonnees(self, x, y):
		"""
		Cett fonction retourne les coordonnées de la case
		x, y en tenant compte de l'adaptation à l'écran
		"""
		echelle, delta_x, delta_y = self.find_scale_delta(self.canvas.winfo_height(), self.canvas.winfo_width())
		return (x*echelle+delta_x, y*echelle+delta_y), ((x+1)*echelle+delta_x, (y+1)*echelle+delta_y)

	def find_scale_delta(self, height, width):
		"""
		On choisit un echelle tel que toute la matrice rentre dans la fenêtre
		Si l'echelle est calculée en fonction de la hauteur car c'est la
		plus grande, il y aura un décalage pour la largueur que l'on caclule
		pour afficher le niveau au milieu de la fenêtre (et inversement dans le
		cas où la longueur est plus grande)
		"""
		verif = height / len(self.grid), width / len(self.grid[0])
		delta_x, delta_y, echelle = 0, 0, 0
		if verif[0] < verif[1]:
			echelle = verif[0]
			delta_x = (width - (len(self.grid[0])*echelle)) / 2
		else:
			echelle = verif[1]
			delta_y = (height - (len(self.grid)*echelle)) / 2

		return echelle, delta_x, delta_y
