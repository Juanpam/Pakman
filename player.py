

class genericPlayer():

	def __init__(self):
		

		#Direction: Right=1, Left=2, Down=3, Up=4
		self.dir=1
		self.spdx=1
		self.spdy=1
		

		#State: noVulnerable=0, Vulnerable=1, dead=2, alive=3
		self.state=0

class ghost(genericPlayer):

	def __init__(self):

		#states ghost: searching=1 calculating=2 
		self.stateGhost=1


class pakman(genericPlayer):

	def __init__(self):
		self.lives=3
		self.points=0

