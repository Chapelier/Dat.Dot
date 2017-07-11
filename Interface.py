
from tkinter import *
try:
    from tkinter.filedialog import messagebox, colorchooser
except ImportError:
    from tkinter import messagebox, colorchooser
import ctypes
import glob
from os.path import exists
import os
from time import sleep
from math import sqrt
from Levels import Level
from Processbar import Processbar

successfull_import = True
try:
    import pygame
except ImportError:
    successfull_import = False

SCREEN_INFO_X = ctypes.windll.user32.GetSystemMetrics(0)
SCREEN_INFO_Y = ctypes.windll.user32.GetSystemMetrics(1)

class Interface():

	def __init__(self):
		self.window = Tk()
		self.window.title("Dat.Dot")
		self.window.resizable(False, False)
		self.window.geometry("500x500")
		self.window.config(bg='#9af4fc')
		self.window.focus_set()
		# Canvas de fond
		self.canvas = Canvas(self.window, width=500, height=250, highlightthickness=0, bg='#9af4fc')
		self.canvas.pack()
		# Barre de chargement
		self.processbar = Processbar(Message(self.window, width=250, font=('', 16), bg='#9af4fc'), self.canvas)
		# Bouton de volume
		self.img_volume_on = PhotoImage(file="images/volon.gif")
		self.img_volume_off = PhotoImage(file="images/voloff.gif")
		self.volume_button = Button(self.window, image=self.img_volume_off, command=self.volumeoff)
		# Potentiomètre du volume
		self.processbar.next()
		self.scale_volume = Scale(self.window, orient='horizontal', from_=0, to=1, bg='#9af4fc', bd=0, showvalue=0,
								resolution=0.01, tickinterval=0, length=100, command=self.changeVolume, border=0)
		self.scale_volume.set(1)
		# Chronomètre
		self.processbar.next()
		self.countdown = Label(self.window, bg='black', fg='#00FF44', font=('Source Code Pro Light', 12))

		self.processbar.next()
		self.current_session = ""
		self.current_level = 0
		self.current_screen = ""
		self.is_full_screen = False
		self.clock = 0
		self.level = None
		self.skip_intro = False

		# self.height_window, self.width_window = self.screenAdaptator(SCREEN_INFO_Y, SCREEN_INFO_X)
		# dx, dy = int((SCREEN_INFO_X-self.width_window)/2), int((SCREEN_INFO_Y-self.height_window)/2)
		# self.window.geometry("{}x{}+{}+{}".format(self.width_window, self.height_window, dx, dy))
		# self.canvas.config(bg='#9af4fc', width=self.width_window, height=self.height_window)

		self.processbar.next()
		self.passwords = []
		# On lit le fichier des mots de passe
		with open ('data/password.txt') as file:
			for i in file.readlines():
				self.passwords.append(i.replace('\n',''))

		self.processbar.next()
		self.mixer = None
		if successfull_import:
			pygame.init()
			self.mixer = pygame.mixer

		self.processbar.next()
		self.intro()
		self.window.mainloop()

	##################### Écran #####################

	"""
	Calcul de la taille de la fenêtre du jeu en fonction
	de la taille de l'écran
	"""

	screenAdaptator = lambda screen_x, screen_y: (int(screen_x / ((1+sqrt(5)) / 2)), int(screen_y / ((1+sqrt(5)) / 2)))
	screenAdaptator = staticmethod(screenAdaptator)

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

	##################### Musique & Bruitages #####################

	def music(self, title):
		"""
		Joue le morceau 'title' en arrêtant la précédente
		"""
		# Si une musique est en cours de lecture, on l'arrête
		try:
			self.mixer.music.stop()
		except pygame.error:
			pass

		# On lance la musique du menu si on est dans le menu
		if title=='menu':
			self.mixer.music.load('music/menu.mp3')
			self.mixer.music.play(-1)

		# On lance les musiques du jeu si on est dans le jeu
		if title=='game':
			self.mixer.music.load('music/welcome.ogg')
			self.mixer.music.play()
			sleep(2)
			self.mixer.music.stop()
			self.mixer.music.load('music/firstsong.ogg')

			songs = glob.glob("music/song*.ogg")        
			for k in range(len(songs)):
				self.mixer.music.queue('music/song{}.ogg'.format(k))
			self.mixer.music.play()

	def volumeon(self):
		# On remet le volume à la valeur du potentiomètre
		self.mixer.music.set_volume(self.scale_volume.get())
		# On modifie le bouton et son image
		self.volume_button.configure(image=self.img_volume_off, command=self.volumeoff)
	        
	def volumeoff(self):
		# On remet le volume à 0
		self.mixer.music.set_volume(0)
		# On modifie le bouton et son image
		self.volume_button.configure(image=self.img_volume_on, command=self.volumeon)

	def changeVolume(self, var):
		# On change le volume à la valeur du potentiomètre
		self.mixer.music.set_volume(self.scale_volume.get())

	def bruit(self, title):
		"""
		Joue le bruitage 'title' en arrêtant le précédent
		"""
		try:
			self.bruitage.stop()
		except:
			pass
		self.bruitage = self.mixer.Sound(title)
		self.bruitage.play()

	##################### Général #####################

	def skip(self):
		# Press Return to skip Intro
		self.skip_intro = True
		self.canvas.delete(ALL)

	def intro(self):
		"""
		Lance la cinématique d'intro en plein écran
		"""
		# On prend toutes les images dans le dossier intro et
		# on les met dans l'ordre
		images=[]
		img = glob.glob("intro/*.gif")
		img = sorted(img)
		for k in img:
			# On les transforme toutes en objets image
			images.append(PhotoImage(file=k))

		self.canvas.config(bg='black')
		self.window.bind("<Return>", lambda var : self.skip())
		self.fullscreen()
		for k in images:
			if self.skip_intro == False:
				# Puis on les affiche une à une avec une vitesse de 30 images/s
				self.canvas.create_image(0, 0, image=k, anchor="nw")
				self.canvas.update()
				sleep(1/30)

		# On quitte le pein écran
		self.fullscreen()
		#  On adapte la fenêtre à l'écran
		self.width_window, self.height_window = self.screenAdaptator(SCREEN_INFO_X, SCREEN_INFO_Y)
		dx, dy = int((SCREEN_INFO_X-self.width_window)/2), int((SCREEN_INFO_Y-self.height_window)/2)
		self.canvas.config(bg='#9af4fc', width=self.width_window, height=self.height_window)
		self.window.geometry("{}x{}+{}+{}".format(self.width_window, self.height_window, dx, dy))

		self.window.bind("<Escape>", lambda var : self.window.destroy())
		# On lance le menu
		self.menu()

	def menu(self):
		"""
		Affiche le menu principal
		"""
		self.window.title("Menu")
		self.current_screen = 'menu'
		self.stopClock()

		# On assigne les touches du clavier aux évènements du menu
		self.event("unbind", ['<Up>', '<Down>', '<Left>', '<Right>', '<m>', '<i>', '<&>'])
		self.event("unbind", [str(x) for x in range(10)])
		event_functions = {'<c>': self.chooseColor,
						'<p>': lambda var: self.levelType(),
						'<F12>': lambda var: self.fullscreen(),
						'<x>': lambda var: self.passwordsMenu()}
		self.event("bind", event_functions)

		# On détruit les boutons de l'écran password si ils sont présents
		try:
			self.E_password.destroy()
			self.B_valider.destroy()
		except AttributeError:
			pass

		# On lance la musique du menu
		if successfull_import:
			self.music('menu')

		self.canvas.delete(ALL)
		self.countdown.place_forget()
		self.volume_button.place(x=60,y=40)
		self.scale_volume.place(x=25,y=80)

		# On crée les messages du menu et on leur assigne une couleur
		messages = [("Press Escape anywhere to quit", "blue"),
					("Press M to return on here", "black"),
					("Press R to restart", "green"),
					("Press C to select your color", "white"),
					("Press P to play !", "red"),
					("Press L to open LevelEditor [Coming soon]", "blue"),
					("Press X to enter a password", "purple"),
					("Press F12 to switch normal screen <-> full screen", "black")]

		# On affiche les messages de manière à ce qu'ils soient centrés sur l'écran
		height, width = self.height_window, self.width_window
		mid = width / 2, height / 2
		current_aff = len(messages)//2
		for i in range(len(messages)):
			txt, color = messages[i]
			self.canvas.create_text(mid[0], mid[1]-20*current_aff, text=txt, fill=color, state="disabled", font=("Modern", 18))
			current_aff -= 1.5

	def levelType(self):
		# Ici l'utilisateur choisira entre les trois types de niveaux
		self.window.title("Choose the levels")
		self.current_screen = 'leveltype'
		self.event("unbind", ['<c>', '<p>'])

		# On bind les touches pour accéder aux différents types de niveaux
		event_functions = {'<m>': lambda var: self.menu(),
						'<p>': lambda var: self.play("public"),
						'<s>': lambda var: self.play("story"),
						'<u>': lambda var: self.play("user")}
		self.event("bind", event_functions)

		# On crée les messages qui seront affichés à l'écran
		levelmessages = [("Press P to play public levels", "white", "#87CEFA"),
						("Press S to play the original storyline", "white", "#DDA0DD"),
						("Press U to play your own levels", "white", "#7FFFD4")]

		# On affiche les messages précédents
		height, width = self.height_window, self.width_window
		for i in range(len(levelmessages)):
			txt, txt_color, bg = levelmessages[i]
			coords = int(i*width/3), 0,  int(width/3 + i*width/3), height
			self.canvas.create_rectangle(coords[0], coords[1], coords[2], coords[3], fill=bg)
			self.canvas.create_text((coords[0]+coords[2])/2, height/2, text=txt, fill=txt_color, font=("Modern", 14))

	def play(self, session):
		"""
		On lance le premier niveau, l'utilisateur
		commence à jouer
		"""
		self.current_screen = 'play'
		self.current_session = session

		if successfull_import:
			self.music('game')

		self.event("unbind", ['<p>', '<s>', '<u>'])
		self.countdown.place(x=10,y=10)
		self.nextLevel(1)

	def nextLevel(self, level):
		"""
		Cherche s'il existe un fichier de niveau suivant
		Si oui, on l'exploite et on retourne le niveau actuel
		Sinon, l'utilisateur a finit tout les niveaux et
		on lui propose de quitter ou de recommencer
		"""

		path = "levels/{}".format(self.current_session)
		if os.listdir(path) == []:
			title = "No such file"
			msg = "There is no level in this place, sorry"
			icone = "info"
			messagebox.showinfo(title, msg, icon=icone)
			self.menu()
		else:
			file = path + "/level {}.lvl".format(level)
			if exists(file):
				# Il reste un niveaux, que l'on charge
				self.current_level = level
				self.level = Level.fromFile(file)
				self.level.canvas = self.canvas
				self.window.title(file.replace('.lvl', '').replace('levels/', '') + ' : ' + self.level.name)
				self.canvas.delete(ALL)
				self.level.draw()
				# On relance le chronomètre
				self.stopClock()
				self.update_clock(0)
				# On bind les touches de déplacement et
				# celle pour recommencer
				event_functions = {'<Up>': self.move,
								'<Down>': self.move,
								'<Left>': self.move,
								'<Right>': self.move,
								'<r>': lambda var : self.nextLevel(self.current_level)}
				self.event("bind", event_functions)
				# On bind les codes de triche
				for key in range(10):
					self.event("bind", {str(key): self.getAcces})
			else:
				# Tout les niveaux sont réussit, on demande
				# à l'utilisateur s'il veux quitter ou recommencer
				titre = "Game over !"
				msg = "Congratulations :)"
				icone = "info"
				messagebox.showinfo(titre, msg, icon=icone)

				titre = "Now what ?"
				msg = "Leave ?"
				leave = messagebox.askquestion(titre, msg)
				if leave == 'yes':
					self.window.destroy()
				else:
					self.menu()

	def passwordsMenu(self):
		self.window.title("Enter a password")
		self.canvas.delete(ALL)
		self.current_screen = 'passwordsMenu'
		self.event("unbind", ['<c>', '<p>', '<l>', '<x>', '<p>', '<s>', '<u>'])
		event_functions = {'<Return>' : lambda var: getpass()}
		self.event("bind", event_functions)

		def getpass():
			entry = E_password.get()
			# Si le mot de passe entré est dans la liste des mots de passe...
			# ...on lance le niveau associé au mot de passe
			if entry == 'quit':
				quitPasswordsMenu()
			elif entry in self.passwords:
				self.current_session = 'story'
				self.canvas.delete(ALL)
				E_password.destroy()
				B_valider.destroy()
				lab.destroy()
				self.play(self.current_session)
				self.level = self.passwords.index(entry)+1
				self.nextLevel(self.level)
				self.window.focus_force()

		def quitPasswordsMenu():
			self.canvas.delete(ALL)
			E_password.destroy()
			B_valider.destroy()
			lab.destroy()
			self.menu()

		height, width = self.height_window, self.width_window
		# On affiche un simple label 
		lab = Label(self.window, fg='black', bg='#9af4fc', text="Type quit to return on menu\nPress enter to validate", font=("Modern", 14))
		lab.place(y=height/2-75, x=width/2, anchor="center")
		# On crée un entry pour entrer les mots de passe
		E_password = Entry(self.window, font=("Juice ITC", 24), justify="center")
		E_password.place(y=height/2, x=width/2, anchor="center")
		E_password.focus_force()
		# On crée un bouton valider qui lance la def "getpass"
		B_valider = Button(self.window, text="Valider", width=10, command=getpass)
		B_valider.place(y=height/2+75, x=width/2, anchor="center")


	def chooseColor(self, var):
		"""
		On lance une boite de dialogue pour
		choisir la couleur du personnage
		"""
		rgb, self.color_player = colorchooser.askcolor("blue", title="Choose your color !")

	def event(self, action, commands):
		"""
		Cette fonction n'a été ajouté que pour
		rendre le code plus lisible, elle est
		utilisée pour bind ou unbind des évènements
		en masse.
		"""
		if action == "bind":
			for key, funct in commands.items():
				self.window.bind(key, funct)
		elif action == "unbind":
			for i in commands:
				self.window.unbind(i)

	def update_clock(self, time):
		"""
		Chronomètre actualisé toutes les secondes
		"""

		hours = time // 3600
		minutes = (time - hours*3600) // 60
		seconds = time - hours*3600 - minutes*60
		self.countdown.configure(text="%02d:%02d:%02d" % (hours, minutes, seconds))
		self.clock = self.window.after(1000, lambda : self.update_clock(time+1))

	def stopClock(self):
		"""
		Fonction pour arrêter le chronomètre
		"""
		self.window.after_cancel(self.clock)

	def getAcces(self, var):
		"""
		Cheatcode pour les niveaux (developpers only ;))
		"""
		acces = int(var.keysym)
		if acces == 0:
			acces = 10
		self.nextLevel((self.current_level//10)*10 + acces)

	def move(self, cap):
		msg = self.level.movePlayer(cap)
		if msg == "end":
			self.nextLevel(self.current_level+1)
			if successfull_import:
				self.bruit('sounds/exit.ogg')
		elif msg == "tp" and successfull_import:
			self.bruit('sounds/tp.ogg')
		elif msg == "switch" and successfull_import:
			self.bruit('sounds/change.ogg')

i = Interface()
