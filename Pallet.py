
from tkinter import Canvas, CURRENT

class Pallet(Canvas):
	
	def __init__(self, master=None, buttons_color=[], nb_columns=2, width_brush=5, cnf={}, **kw):
		Canvas.__init__(self, master, cnf={}, **kw)
		self.buttons_color = buttons_color
		self.width_brush = width_brush
		self.brush = self.create_rectangle(-1, -1, -1, -1, fill='red', width=3, outline='red')
		self.button_number = -1
		self.columns = nb_columns
		self.len = len(self.buttons_color)//nb_columns + len(self.buttons_color) % self.columns
		self.bind('<1>', lambda var: self.leftClic())

	def get_coords_of_button(self, x, y, long):
		width, height = self.winfo_width(), self.winfo_height()
		cord_x = (width / self.columns) *(0.25+x), (width / self.columns) * (0.75+x)
		cord_y = (height / long) * (0.25+y), (height / long) * (0.75+y)
		delta_x, delta_y = cord_x[1]-cord_x[0], cord_y[1]-cord_y[0]
		if delta_x < delta_y:
			cord_y = cord_y[0], cord_y[0] + delta_x
		else:
			cord_x = cord_x[0], cord_x[0] + delta_y
		return cord_x, cord_y

	def draw(self):
		current_button = 0
		for i in range(len(self.buttons_color)//self.columns):
			for j in range(self.columns):
				cords = self.get_coords_of_button(j, i, self.len)
				if '&' in self.buttons_color[current_button]:
					# By adding a '&' in color name, make a circle button without borderline
					self.create_oval(cords[0][0], cords[1][0], cords[0][1], cords[1][1],
						fill=self.buttons_color[current_button][1:],
						tag=current_button)
				else:
					if '#' in self.buttons_color[current_button]:
						self.create_rectangle(cords[0][0], cords[1][0], cords[0][1], cords[1][1],
							fill=self.cget('bg'),
							tag=current_button)
						# By adding a '#' in color name, make a cross
						self.create_line(cords[0][0], cords[1][0], cords[0][1], cords[1][1],
							fill=self.buttons_color[current_button][1:], width=3,
							tag=current_button)
						self.create_line(cords[0][0], cords[1][1], cords[0][1], cords[1][0],
							fill=self.buttons_color[current_button][1:], width=3,
							tag=current_button)

					else:
						self.create_rectangle(cords[0][0], cords[1][0], cords[0][1], cords[1][1],
							fill=self.buttons_color[current_button],
							tag=current_button)

				current_button += 1
			mem = i+1

		j = 0
		for i in range(len(self.buttons_color) % self.columns):
			# Adding a button if len(buttons_color) is an odd number
			cords = self.get_coords_of_button(j, mem, self.len)
			self.create_rectangle(cords[0][0], cords[1][0], cords[0][1], cords[1][1],
				fill=self.buttons_color[current_button])
			j += 1

	def leftClic(self):
		"""
		Quand on choisit une case dans la palette
		"""

		id_rect = self.find_withtag(CURRENT)

		msg = ""
		# Si une case est visée, on la (dé)sélectionne
		if len(id_rect) != 0:
			tags = self.gettags(id_rect[0])
			if tags[0] == "current":
				button_number = int(tags[1])
			else:
				button_number = int(tags[0])
			if self.button_number == button_number:
				# Désélection (c'est la même case)
				self.itemconfig(self.brush, outline=self.cget('bg'), fill=self.cget('bg'))
				# Si on déséléctionne void, on reconfigure le clic et le reste
				if self.button_number == len(self.buttons_color)-1:
					msg = "leave void tool"
					# grid.bind('<3>', lambda var: gridClic2(var, self.buttons_color, matrice, donnees, echange))
					# # On efface dic
					# for val in Dic_selected.values():
					# 	grid.delete(val)
					# Dic_selected = {}
					# setCurCase("#")
				self.button_number = -1
			else:
				# Si void était séléctionnée et qu'on change
				if self.button_number == len(self.buttons_color)-1:
					msg = "void changed"
					# grid.bind('<3>', lambda var: gridClic2(var, self.buttons_color, matrice, donnees, echange))
					# # On efface dic
					# for val in Dic_selected.values():
					# 	grid.delete(val)
					# Dic_selected = {}
					# setCurCase("#")
				# Sélection
				self.button_number = button_number
				self.itemconfig(self.brush, outline='red', fill='red')
				# On affiche le rectangle de sélection
				cords = self.get_coords_of_button(button_number%self.columns, button_number//self.columns, self.len)
				self.coords(self.brush, cords[0][0]-self.width_brush, cords[1][0]-self.width_brush,
					cords[0][1]+self.width_brush, cords[1][1]+self.width_brush)
				self.update()

			# Si la case sélectionnée est void, on change le mode de clic
			if self.button_number == len(self.buttons_color)-1:
				msg = "void selected"
				# grid.bind('<3>', lambda var: gridClic2Void(var, self.buttons_color, matrice, donnees, echange))
		
		return msg
		# On affiche les infos du niveau
		# L_var = makeAFrameIn('carac', carac, True, [len(matrice[0]), len(matrice), name])

# p = Pallet(t, ['red', 'green', 'yellow', 'black', 'white'], bg='blue', height=500, width=500)