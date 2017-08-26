"""
Artificial Intelligence for Videogames
Pontificia Universidad Javeriana Cali
Members:
	Paula Correa
	Juan Pablo Méndez


Main file for the Pakman project.	
Makes uses of the Pygame and Sys module.
"""


import sys, pygame, spritesheet
pygame.init()


class Game():
	"""
	Class created to store the most used game methods
	"""
	black = 0, 0, 0

	def __init__(self):


		#Configuration variables
		#Setting screen proportions
		self.wideScreen = True
		if(self.wideScreen):
			self.ratio = 9/16
		else:
			self.ratio = 1
		self.width = 1000
		self.height = int(self.width * self.ratio)
		size = self.width, self.height
		self.screen = pygame.display.set_mode(size)
		self.background = pygame.transform.scale(pygame.image.load("Mapa1.png"), size)
		


		self.loadSpriteSheet()
		self.infiniteLoop()

	def infiniteLoop(self):
		"""
		Infinite loop for the game
		"""
		while True:
		    for event in pygame.event.get():
		        if event.type == pygame.QUIT: sys.exit()

		    self.screen.fill(self.black)
		    self.screen.blit(self.background, (0,0))
		    for i in range(4):
		    	for j in range(8):
		    		self.screen.blit(self.ghostImages[i][j], (100*j,100*i))
		    pygame.display.flip()

	def loadSpriteSheet(self):
		self.sSheet = spritesheet.spritesheet("spriteSheet2.png")
		self.ghostImages=[]
		for x in range(4):
			self.ghostImages.append(self.sSheet.images_at([(7+(47*x),8+(47*y),33,32) for y in range(8)]))
game = Game()


