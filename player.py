"""
This module implements a generic player class used for the Pakman game
and some inherited classes for the pakman and the ghosts

"""

class genericPlayer():
	"""
	This class implements a generic player with attributes like position, speed and direction
	"""

	def __init__(self):
		#Direction: Right=1, Left=2, Down=3, Up=4
		self.dir=1
		self.spdx=20
		self.spdy=20
		
		self.posx = 0
		self.posy = 0

		#State: noVulnerable=0, Vulnerable=1, dead=2
		self.state=0

	def setPos(self, x, y):
		self.posx = x
		self.posy = y

	def changeDir(self, newDir):
		if(newDir>=1 and newDir <=4):
			self.dir = newDir

	def nextDir(self):
		newDir = self.dir+1
		if(not (newDir>=1 and newDir <=4)):
			return 1
		return newDir

	def updatePos(self):
		if(self.dir==1):
			self.posx += self.spdx
		if(self.dir==2):
			self.posx -= self.spdx
		if(self.dir==3):
			self.posy += self.spdy
		if(self.dir==4):
			self.posy -= self.spdy

	def getPos(self):
		return (self.posx,self.posy)

class ghost(genericPlayer):
	"""
	This class inherits from the genericPlayer class and adds some states for the AI
	"""

	def __init__(self):

		#states ghost: searching=1 calculating=2 
		super().__init__()
		self.stateGhost=1


class msPakman(genericPlayer):
	"""
	This class inherits from the genericPlayer class and adds some attributes like the number of lives
	and points
	"""

	def __init__(self):
		super().__init__()
		self.lives=3
		self.points=0

