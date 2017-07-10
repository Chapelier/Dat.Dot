
from threading import Thread

class Processbar():

	def __init__(self, label, canvas):
		self.infos = ["Chargement des images du bouton mute",
					"Création de l'échelle de volume",
					"Création du chronomètre",
					"Initialise Interface attribute",
					"Stockage des mots de passe",
					"Initialise pygame",
					"Chargement de la cinématique d'introduction",]
		self.step = 0
		self.canvas = canvas
		self.msg = label
		self.msg.pack()
		self.msg.config(text=self.infos[0])
		self.canvas.create_rectangle(50, 100, 450, 105)

	def next(self):
		self.canvas.create_rectangle(50, 100, self.step/(len(self.infos)-1)*400+50, 105, fill='green')
		self.msg.config(text=self.infos[self.step])
		self.canvas.update()
		self.step += 1