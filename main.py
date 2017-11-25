"""
Artificial Intelligence for Videogames
Pontificia Universidad Javeriana Cali
Members:
    Paula Correa
    Juan Pablo Méndez


Main file for the Pakman project.   
Makes use of the Pygame and Sys module.
"""


import sys, pygame, spritesheet, map, player, astar, pygame.freetype, os, flock, random
from dforest import dforest
from btree import BTree




class Game():
    """
    Class created to store the most used game methods
    """
    black = 0, 0, 0
    white = 255, 255, 255
    #playersCount = 2
    def __init__(self, level = None):

        #Level configuration
        if level == None:
            level = 1
        self.level = level

        #Configuration variables
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()
        pygame.display.set_caption("Pakman - 2017")
        pygame.display.set_icon(pygame.image.load("icon.png"))

        #Setting screen proportions
        self.wideScreen = False
        if(self.wideScreen):
            self.ratio = 9/16
        else:
            self.ratio = 1

        #Default width
        self.width = 700
        self.height = int(self.width * self.ratio)
        size = self.width, self.height
        self.screen = pygame.display.set_mode(size)

        #Cell size in pixels
        self.cellSize = 50

        #Map set-up
        self.mapToLoad = "map8.txt"
        self.gameMap = map.Map(self.mapToLoad)
        self.originalGameMap = map.Map(self.mapToLoad)
        self.noObstaclesMap = self.gameMap.getNoObstaclesMap()
        self.AStarMap = self.gameMap.getAStarMap()
        self.playersCount = self.gameMap.playersCount
        #print("Players count", self.playersCount)
        #Uncomment to print map
        #for row in self.gameMap.matrix:
            #print(row)

        #Load sprites
        self.loadSpriteSheet()
        self.originalGhostImages = self.ghostImages[:]
        self.charsPos = self.getCharsPos() #Characters top-left edge position
        #print(self.charsPos) 
        self.charsPosCenter = self.getCharPosCenter() #Characters center position

        
        #There are at least 2 players always
        self.players = [player.msPakman(), player.ghost()]

        #Add additional players/ghosts
        for i in range(2,self.playersCount):
            self.players.append(player.ghost())

        #Decrease speed
        for i in range(1,self.playersCount):
            self.players[i].spdx -= 1
            self.players[i].spdy -= 1

        #Draw map based on the gameMap
        self.color = self.black
        self.background = self.drawMap()


        #Find path to follow Ms. Pakman
        self.paths = []
        for i in range(1 ,self.playersCount):
            self.paths.append(self.calcPath(None, i))
        if(7 in self.gameMap.playersInMap):
            self.noObstaclesPath = self.calcPath(self.noObstaclesMap, 3)
        self.visibleDistance = 10

        #Create forest object
        self.forest = dforest(self.gameMap.dimensions[0]*self.gameMap.dimensions[1])
        self.pacDotPos = self.findPacDotesZones()
        self.indexPacDot = 0

        #Uncomment to print calculated path
        #print(self.path)
        
        #Update players logical position based on the position in the drawn map
        for p in range(len(self.players)):
            self.players[p].setPos(*self.charsPos[p])

        #Initial ghost position in cells 
        #Actual position is stored on the first position of each tuple on this array and old position on the second one
        self.ghostPos = [[( self.charsPosCenter[p][0]//self.cellSize,self.charsPosCenter[p][1]//self.cellSize ),
                            ( self.charsPosCenter[p][0]//self.cellSize,self.charsPosCenter[p][1]//self.cellSize )] for p in range(1,len(self.players))]

        self.playerPos = [( self.charsPosCenter[0][0]//self.cellSize,self.charsPosCenter[0][1]//self.cellSize ),
                            ( self.charsPosCenter[0][0]//self.cellSize,self.charsPosCenter[0][1]//self.cellSize )]

        
        #If there is a path between Ms. Pakman and the ghost the direction is updated and the path is consumed
        if(self.paths[0]):
            self.players[1].changeDir(int(self.paths[0][0]))
            self.paths[0]=self.paths[0][1:]

        


        
        #Initialize text module
        pygame.freetype.init()
        self.refreshImagesTime = 100
        
        self.gameClock = pygame.time.Clock()

        #Turns on or off the sound
        self.fchannel = pygame.mixer.find_channel()
        self.sound = True
        
        
        #Turn to true for some fun
        self.metal = False

        if(self.metal):
            self.sound = True
            for i in range(self.playersCount):
                self.players[i].spdx += 3
                self.players[i].spdy += 3
            self.refreshImagesTime = 70
            pygame.time.set_timer(pygame.USEREVENT+2, 5500)

        #Powerup related variables
        self.powerUp = False
        self.powerUpTime = 10000
        
        
        self.createEvents()
        self.infiniteLoop()


    def updatePacDoteZone(self):
        self.forest = dforest(self.gameMap.dimensions[0]*self.gameMap.dimensions[1])
        new = self.findPacDotesZones()
        if(new != self.pacDotPos):
            self.pacDotPos = new
            self.indexPacDot = 0
            #print("CAMBIEEEE", self.pacDotPos)

    def findPacDotesZones(self):
        #Arrays used to check cells adjacency
        dx = [0, 1, 0, -1]
        dy = [-1, 0, 1, 0]
        rows = self.gameMap.dimensions[1]
        cols = self.gameMap.dimensions[0]
        # for r in self.gameMap.matrix:
        #     print(r)
        for i in range(rows):
            for j in range(cols):
                if(self.gameMap.getCell(j,i) == 2):
                    for k in range(len(dx)):
                        u,v = j+dx[k], i+dy[k]
                        if(0 <= u < cols and 
                            0 <= v < rows and 
                            self.gameMap.getCell(u,v) == 2):
                            self.forest.union(cols*i+j,cols*v+u)
                else:
                    self.forest.setCount(cols*i+j, 0)

        m = self.forest.toMatrix(self.gameMap.dimensions[1])
        pacDotPositions = []
        maxCountParent = self.forest.maxCountParent()
        #print("maxCountParent", maxCountParent)
        for r in range(rows):
            for c in range(cols):
                if(m[r][c] == maxCountParent):
                    pacDotPositions.append((c,r))

        return pacDotPositions



    def calcPath(self, gameMap=None, playerId=None, destination = None):
        """
        Calculates path and translates it to being compatible with the actual map
        """
        if(not gameMap):
            gameMap = self.AStarMap
        if(not playerId):
            playerId = 1
        if(not destination):
            destination = (self.charsPosCenter[0][0]//self.cellSize,self.charsPosCenter[0][1]//self.cellSize)
        path = astar.pathFind(gameMap,astar.directions,astar.dx,astar.dy,self.charsPosCenter[playerId][0]//self.cellSize,self.charsPosCenter[playerId][1]//self.cellSize,*destination)
        path = astar.translatePath(path)
        #print(path)
        return path

    def infiniteLoop(self):
        """
        Infinite loop for the game
        """
        firstTime = True
        beginSoundFinished = False
        death = win = False
        
        while self.level == 1:
            if(firstTime or beginSoundFinished and not (death or win)):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: sys.exit()
                    if event.type == pygame.USEREVENT+1:
                        self.updateImages()
                    if event.type == pygame.USEREVENT+2:
                        self.color = self.white if self.color == self.black else self.black
                    if event.type == pygame.USEREVENT+3:
                        self.deactivatePowerUp()
                    if event.type == pygame.KEYDOWN and event.key==pygame.K_UP:
                        self.players[0].changeDir(4)
                    if event.type == pygame.KEYDOWN and event.key==pygame.K_DOWN:
                        self.players[0].changeDir(3)
                    if event.type == pygame.KEYDOWN and event.key==pygame.K_LEFT:
                        self.players[0].changeDir(2)
                    if event.type == pygame.KEYDOWN and event.key==pygame.K_RIGHT:
                        self.players[0].changeDir(1)


                
                
                if(not death or win):
                    for i,p in enumerate(self.players):
                        if(p.alive):
                            self.updateGhostDir(i)
                            self.movePlayer(i)
                            self.updatePlayerPos(i)
                    
                    self.checkGhostsCatched()
                    # self.movePlayer(1)
                    # self.movePlayer(0)
                    death = self.checkIfDeath()
                    #death = False
                    #win = self.checkIfWin()
                    #win = True
                    self.background=self.drawMap(False)
                    self.screen.fill(self.color)
                    self.screen.blit(self.background, (0,0))

                


                # self.screen.blit(self.msPakmanImages[self.imageId],(50*4,50*4))
                # for j in range(len(self.ghostImages)):
                #     for i in range(len(self.ghostImages[j])):
                #         self.screen.blit(self.ghostImages[j][self.imageId],(50*i,50*j))
                #print(pygame.mouse.get_pos(), self.charsPos)
                # print(self.charsPos)
                #print("Farthest point",self.gameMap.getFarthestEmptyPoint(*self.playerPos[0]))
                #print(self.forest.maxCount())
            else:

                if(death):
                    pygame.mixer.stop()
                    pygame.mixer.music.load("pacman_death.wav")
                    pygame.mixer.music.play()
                    while(pygame.mixer.music.get_busy()):
                        pass#print("Sigo ocupadisimo")
                    pygame.event.clear()
                    for i in range(1,3):
                        pygame.time.set_timer(pygame.USEREVENT+i, 0)
                    break
                if(win):
                    self.level = 2
                    self.color = self.black
                    pygame.mixer.stop()
                    pygame.mixer.music.load("pacman_win.wav")
                    pygame.mixer.music.play()
                    while(pygame.mixer.music.get_busy()):
                        pass#print("Sigo ocupadisimo")
                    pygame.event.clear()
                    for i in range(1,3):
                        pygame.time.set_timer(pygame.USEREVENT+i, 0)
                    

                for event in pygame.event.get():
                    if event.type == pygame.QUIT: sys.exit()
                    if event.type == pygame.USEREVENT+2:
                        pygame.time.set_timer(pygame.USEREVENT+2, 100)
                        chomp = pygame.mixer.Sound("pacman_chomp.wav")
                        chomp.set_volume(0.4)
                        pygame.mixer.find_channel().play(chomp, -1)
                        beginSoundFinished = True
                        self.fchannel = pygame.mixer.find_channel()
            
            pygame.display.flip()

            if(firstTime or not beginSoundFinished):
                if(self.sound):
                    if(not self.metal):
                        if(firstTime):
                            pygame.mixer.music.load("pacman_beginning.wav")
                            pygame.mixer.music.play()
                        if(not pygame.mixer.music.get_busy()):
                            pygame.mixer.music.load("pacman_chomp.wav")
                            pygame.mixer.music.play(-1)
                            beginSoundFinished = True
                    else:
                        if(firstTime):
                            pygame.mixer.find_channel().play(pygame.mixer.Sound("pakman_metal.wav"), -1)
                            
                else:
                    beginSoundFinished = True    
                        

                firstTime = False
            #Uncomment to print map
            # print("Here is the map")
            # for row in self.gameMap.matrix:
            #     print(row)
            # #Uncomment for a slow game play useful for debuggin
            if(self.powerUp):
                pass#print("Powerup activo")
            else:
                pass#print("Powerup inactivo")
            self.gameClock.tick(120)

        
        if(death):
            print("Acabo el juego")
            self.__init__()

        print("Acabo el nivel 1")
        print("Comienza nivel 2")
        firstTime = True
        beginSoundFinished = death = win = False

        self.prepareLevel2()


        ########## LEVEL 2 ############
        while(self.level == 2):
            if(firstTime or beginSoundFinished and not (death or win)):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: sys.exit()
                    if event.type == pygame.USEREVENT+1:
                            self.updateImages()
                    if event.type == pygame.USEREVENT+2:
                        self.color = self.white if self.color == self.black else self.black
                    if event.type == pygame.USEREVENT+3:
                        self.deactivatePowerUp()
                    if event.type == pygame.KEYDOWN and event.key==pygame.K_UP:
                        self.players[0].changeDir(4)
                    if event.type == pygame.KEYDOWN and event.key==pygame.K_DOWN:
                        self.players[0].changeDir(3)
                    if event.type == pygame.KEYDOWN and event.key==pygame.K_LEFT:
                        self.players[0].changeDir(2)
                    if event.type == pygame.KEYDOWN and event.key==pygame.K_RIGHT:
                        self.players[0].changeDir(1)
                    if event.type == pygame.KEYDOWN and event.key==pygame.K_m:
                        print("follow power up")
                        self.flockCount = 2
                    if event.type == pygame.KEYDOWN and event.key==pygame.K_n:
                        print("follow pakman")
                        self.distancePowerUp = self.visibleDistance + 1
                        self.flockCount = 7

                
                #print("Main Loop")

                # self.background = self.genRandomPowerUpPos(self.background)


                if(not death or win):
                    #print(self.charsPos)
                    self.runTree()
                    for i,p in enumerate(self.players):
                        if(p.alive):
                            self.updateGhostDir(i)
                            self.movePlayer(i)
                            self.updatePlayerPos(i)
                    
                    # self.checkGhostsCatched()
                    # self.movePlayer(1)
                    # self.movePlayer(0)
                    
                    death = self.checkIfDeath()
                    #death = False
                    win = self.checkIfWin()
                    self.updateTree()

                self.background = self.drawMap(True)


                self.screen.fill(self.color)
                self.screen.blit(self.background, (0,0))
                pygame.display.flip()
            
            else:
                if(death):
                    pygame.mixer.stop()
                    pygame.mixer.music.load("pacman_death.wav")
                    pygame.mixer.music.play()
                    while(pygame.mixer.music.get_busy()):
                        pass#print("Sigo ocupadisimo")
                    pygame.event.clear()
                    for i in range(1,3):
                        pygame.time.set_timer(pygame.USEREVENT+i, 0)
                    break
                if(win):
                    self.level = 2
                    self.color = self.black
                    pygame.mixer.stop()
                    pygame.mixer.music.load("pacman_win.wav")
                    pygame.mixer.music.play()
                    while(pygame.mixer.music.get_busy()):
                        pass#print("Sigo ocupadisimo")
                    # pygame.event.clear()
                    for i in range(1,3):
                        pygame.time.set_timer(pygame.USEREVENT+i, 0)
                #print("This is not a main loop")
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: sys.exit()
                    if event.type == pygame.USEREVENT+2:
                        pygame.time.set_timer(pygame.USEREVENT+2, 100)
                        chomp = pygame.mixer.Sound("pacman_chomp.wav")
                        chomp.set_volume(0.4)
                        pygame.mixer.find_channel().play(chomp, -1)
                        beginSoundFinished = True
                        self.fchannel = pygame.mixer.find_channel()
            
            if(firstTime or not beginSoundFinished):
                if(self.sound):
                    if(not self.metal):
                        if(firstTime):
                            pygame.mixer.music.load("pacman_beginning.wav")
                            pygame.mixer.music.play()
                        if(not pygame.mixer.music.get_busy()):
                            pygame.mixer.music.load("pacman_chomp.wav")
                            pygame.mixer.music.play(-1)
                            beginSoundFinished = True
                    else:
                        if(firstTime):
                            pygame.mixer.find_channel().play(pygame.mixer.Sound("pakman_metal.wav"), -1)
                            
                else:
                    beginSoundFinished = True    
                        

                firstTime = False

            self.gameClock.tick(120)

        if(death):
                print("Acabo el juego")
                self.__init__(2)

    def updateTree(self):
        # print("----------updating tree-------------")
        self.bTree.restartTree()
        #print(self.bTree.treeToString())
        self.bTreeData["flock"] = self.flockCount
        self.distancePakman =  self.gameMap.getDistanceInCells(*self.ghostPos[0][0],*self.playerPos[0])
        self.distancePowerUp = self.gameMap.getDistanceInCells(*self.ghostPos[0][0],*self.powerUpPos)
        self.bTreeData["distancePakman"] = self.distancePakman
        self.bTreeData["distancePowerUp"] = self.distancePowerUp

        
    def runTree(self):
        count = 0
        while(count < 2 and (not self.bTree.getActiveNode().isLeaf() or not self.bTree.getActiveNode().isAction())):
            self.bTree.updateState()
            #print("dando vuelticas", self.bTree.getActiveNode())
            #print("running tree count", count)
            #print(self.bTree.treeToString())
            # count += 1
        print("RUN TREE")
        # print(self.bTree.treeToString())
        print(self.bTree.getActiveNode())
        print(self.bTree.getAllData())
    
    def prepareLevel2(self):
        """
        Prepares environment for the level 2
        """

        if(self.metal):
            self.sound = True
            for i in range(self.playersCount):
                self.players[i].spdx += 3
                self.players[i].spdy += 3
            self.refreshImagesTime = 70
            pygame.time.set_timer(pygame.USEREVENT+2, 5500)

        #Big pink ghost 
        self.ghostImages[0], self.ghostImages[5] = self.ghostImages[5], self.ghostImages[0]
        self.ghostImages[0] = [pygame.transform.scale2x(i) for i in self.ghostImages[0]]
        self.images[4] = self.ghostImages[0][0]

        #Update map, charsPos and playersCount
        self.mapToLoad = "map.txt"
        self.gameMap = map.Map(self.mapToLoad)
        self.gameMap.matrix = self.gameMap.getLevel2Map()
        self.originalGameMap = map.Map(self.mapToLoad)
        self.originalGameMap.matrix = self.originalGameMap.getLevel2Map()
        self.AStarMap = self.gameMap.getAStarMap()        
        self.playersCount = self.gameMap.playersCount

        self.charsPos = self.getCharsPos() #Characters top-left edge position
        #print(self.charsPos) 
        self.charsPosCenter = self.getCharPosCenter() #Characters center position

        #There are at least 2 players always
        self.players = [player.msPakman(), player.ghost()]

        #Add additional players/ghosts
        for i in range(2,self.playersCount):
            self.players.append(player.ghost())

        #Update players logical position based on the position in the drawn map
        for p in range(len(self.players)):
            self.players[p].setPos(*self.charsPos[p])

        #Decrease speed
        for i in range(1,self.playersCount):
            self.players[i].spdx -= 2
            self.players[i].spdy -= 2

        #Find path to follow Ms. Pakman
        self.paths = []
        for i in range(1 ,self.playersCount):
            self.paths.append(self.calcPath(None, i))
        if(7 in self.gameMap.playersInMap):
            self.noObstaclesPath = self.calcPath(self.noObstaclesMap, 3)
        self.visibleDistance = 10

        self.ghostPos = [[( self.charsPosCenter[p][0]//self.cellSize,self.charsPosCenter[p][1]//self.cellSize ),
                            ( self.charsPosCenter[p][0]//self.cellSize,self.charsPosCenter[p][1]//self.cellSize )] for p in range(1,len(self.players))]

        self.playerPos = [( self.charsPosCenter[0][0]//self.cellSize,self.charsPosCenter[0][1]//self.cellSize ),
                            ( self.charsPosCenter[0][0]//self.cellSize,self.charsPosCenter[0][1]//self.cellSize )]


        #Power up setup
        self.powerUpTime = 100
        self.updatePowerUpPos()

        self.flock = flock.Flock()

        self.flockCount = 1
        self.capacity = 10
        self.umbral = 5
        self.visibleDistance = 5

        #BTree setup
        self.bTree = self.createBTree()
        self.distancePakman =  self.gameMap.getDistanceInCells(*self.ghostPos[0][0],*self.playerPos[0])
        self.distancePowerUp = self.gameMap.getDistanceInCells(*self.ghostPos[0][0],*self.powerUpPos)
        self.bTreeData = {"flock": self.flockCount, "capacity": self.capacity, "umbral": self.umbral, "closeDistance" : self.visibleDistance,
                            "distancePakman" : self.gameMap.getDistanceInCells(*self.ghostPos[0][0],*self.playerPos[0]),
                            "distancePowerUp" : self.gameMap.getDistanceInCells(*self.ghostPos[0][0],*self.powerUpPos)}
        # self.bTreeData["distancePakman"] = 3
        # self.bTreeData["distancePowerUp"] = 5
        self.bTree.setData(self.bTreeData)



        
        print("---before state update---")
        print(self.bTree.treeToString())
        # self.bTree.updateState()
        # print("---between state update---")
        # self.bTree.updateState()
        print("---after state update---")
        # print(self.bTree.treeToString())
        # print(self.bTree.getActiveNode())
        # print(self.bTreeData)
        # print("position ghost and tomato",self.ghostPos[0][0], self.powerUpPos)
        # print(self.bTree.findNode("seq3"))

        self.createEvents()

    def updatePowerUpPos(self):
        xmax, ymax = self.gameMap.dimensions[0], self.gameMap.dimensions[1] 
        x, y = random.randrange(xmax), random.randrange(ymax)
        while(self.gameMap.getCell(x,y) != 0):
            x, y = random.randrange(xmax), random.randrange(ymax)
        self.powerUpPos = (x, y)
        self.gameMap.updateMap(x, y, 3)

    def genRandomPowerUpPos(self, background):

        xmax, ymax = self.width - self.images[2].get_width(), self.height - self.images[2].get_height()
        x, y = random.randrange(xmax), random.randrange(ymax)
        background.blit(self.images[2], (x, y))
        return background

    def createBTree(self):
        """
        Creates the behaviour tree for the big ghost on level 2
        """
        
        selectors = [BTree("selector", "sel"+str(i)) for i in range(2)]
        sequences = [BTree("sequence", "seq"+str(i)) for i in range(6)]

        mainTree = selectors[0]
        selectors[0].addChild(sequences[0])
        selectors[0].addChild(sequences[1])
        selectors[0].addChild(sequences[2])
        selectors[0].addChild(sequences[3])
        selectors[1].addChild(sequences[4])
        selectors[1].addChild(sequences[5])

        checks = [BTree() for i in range(6)]

        checks[0].setName("isGhostDead")
        checks[0].addCondition("flock == 0")

        checks[1].setName("isFlockFull")
        checks[1].addCondition("flock == capacity")

        checks[2].setName("flockGTUmbral")
        checks[2].addCondition("flock > umbral")

        checks[3].setName("flockLTUmbral")
        checks[3].addCondition("flock <= umbral")
        checks[3].addCondition("0 < flock")

        checks[4].setName("powerUpClose")
        checks[4].addCondition("distancePowerUp <= closeDistance")
        
        checks[5].setName("pakmanClose")
        checks[5].addCondition("distancePakman <= closeDistance")

        fPUPNodes = [BTree(name = "followPowerUp"+str(i)) for i in range(2)]
        fPakNodes = [BTree(name = "followPakman"+str(i)) for i in range(2)]
        endNode = BTree(name = "endNode")

        for node in fPUPNodes:
            node.setAction(True)

        for node in fPakNodes:
            node.setAction(True)

        endNode.setAction(True)

        
        
        for i in range(5):
            sequences[i].addChild(checks[i])

        sequences[2].addChild(selectors[1])
        
        #Setting up follow pakman nodes        
        sequences[1].addChild(fPakNodes[0])
        sequences[5].addChild(fPakNodes[1])

        #Setting up follow power-up nodes
        sequences[3].addChild(fPUPNodes[0])
        sequences[4].addChild(fPUPNodes[1])

        #Setting up endNode
        sequences[0].addChild(endNode)

        
        

        
        return mainTree 


    def checkIfDeath(self):
        if(not self.powerUp):
            r = self.radiusPakman+self.radiusGhost
            for i,p in enumerate(self.charsPosCenter[1:]):
                #print(p[0])
                if(self.players[i+1].alive and 
                    abs(p[0] - self.charsPosCenter[0][0]) < r and
                    abs(p[1] - self.charsPosCenter[0][1]) < r):
                    return True
        return False

    def checkGhostsCatched(self):
        if(self.powerUp):
            r = self.radiusPakman+self.radiusGhost
            for i,p in enumerate(self.charsPosCenter[1:]):
                #print(p[0])
                if(abs(p[0] - self.charsPosCenter[0][0]) < r and
                    abs(p[1] - self.charsPosCenter[0][1]) < r):
                    #print("Ghost",i,"died.")
                    self.players[i+1].alive = False

    def checkIfWin(self):
        if(self.level == 1):
            maxCountPacDots = self.forest.maxCount()
            if(maxCountPacDots == 0):
                return True
            else:
                return False
        elif(self.level == 2):
            if(self.bTree.getActiveNode().getName() == "endNode"):
                return True
            else:
                return False

    def createEvents(self):

        #User event for the sprites
        pygame.time.set_timer(pygame.USEREVENT+1,self.refreshImagesTime)

    def updateImages(self):
        """
        Updates the images to be blit for each player
        """

        #spriteGroup is a direction convention fix

        for i,p in enumerate(self.players):
            if(p.dir == 2):
                spriteGroup = 3
            elif(p.dir == 3):
                spriteGroup = 2
            else:
                spriteGroup = p.dir 
            p.lastSprite = ((p.lastSprite + 1) % p.totalSprites) + (p.totalSprites * (spriteGroup-1))

            if(i==0):
                self.images[3] = self.msPakmanImages[p.lastSprite]
            else:
                #print("lala",p.lastSprite,i)
                self.images[3+i] = self.ghostImages[i-1][p.lastSprite]



    def loadSpriteSheet(self):
        #Ghosts variables
        ghostHeight, ghostWidth = 32, 32
        initialXGhost = 7
        initialYGhost = 8
        spaceBetweenGhosts = 15
        intervalSizeG = spaceBetweenGhosts + ghostHeight
        gSpriteCount = 8
        ghostsCount = 7

        #Ms. Pakman variables
        msPakHeight, msPakWidth = 43, 43
        initialXMSPak = 800
        initialYMSPak = 5
        spaceBetweenMSPak = 4
        intervalSizeMSPak = spaceBetweenMSPak + msPakHeight
        msPakCount = 12

        self.sSheet = spritesheet.spritesheet("spriteSheet2.png")
        self.ghostImages=[]
        for x in range(ghostsCount):
            self.ghostImages.append(self.sSheet.images_at([(initialXGhost+(intervalSizeG*x),initialYGhost+(intervalSizeG*y),ghostWidth ,ghostHeight) for y in range(gSpriteCount)],self.black))
        self.msPakmanImages=self.sSheet.images_at([(initialXMSPak,initialYMSPak+(intervalSizeMSPak*y),msPakWidth,msPakHeight) for y in range(msPakCount)],self.black)


        self.scaredGhostImages = self.sSheet.images_at([(initialXGhost,initialYGhost+(intervalSizeG*(y+11)),ghostWidth ,ghostHeight) for y in range(gSpriteCount)],self.black)
        #print("len de scared",len(self.scaredGhostImages))
        #Tomato and pill load
        self.pillImage=pygame.image.load("pill.png")
        self.tomatoImage=pygame.image.load("tomatoso.png")
        self.wallImage=pygame.image.load("cubito.png")

        # for i in range(len(self.msPakmanImages)):
        #     image = pygame.Surface((self.cellSize,self.cellSize))
        #     print("msPakman sizes",self.msPakmanImages[i].get_width(),self.msPakmanImages[i].get_height())
        #     image.blit(self.msPakmanImages[i],((self.cellSize-self.msPakmanImages[i].get_width())//2,(self.cellSize-self.msPakmanImages[i].get_height())//2))
        #     image.set_colorkey(self.black)
        #     self.msPakmanImages[i] = image

        # for i in range(len(self.ghostImages)):
        #     for j in range(len(self.ghostImages[i])):
        #         image = pygame.Surface((self.cellSize,self.cellSize))
        #         image.blit(self.ghostImages[i][j],((self.cellSize-self.ghostImages[i][j].get_width())//2,(self.cellSize-self.ghostImages[i][j].get_height())//2))
        #         image.set_colorkey(self.black)
        #         self.ghostImages[i][j] = image

        self.images=[self.wallImage,self.pillImage,self.tomatoImage,self.msPakmanImages[0],self.ghostImages[0][0]]

        self.radiusPakman = self.images[3].get_width() // 2
        self.radiusGhost = self.images[4].get_width() // 2
        ## Re arranging image order
        #Makes second player purple
        self.ghostImages[1], self.ghostImages[5] = self.ghostImages[5], self.ghostImages[1]  
        self.ghostImages[2], self.ghostImages[3] = self.ghostImages[3], self.ghostImages[2]  
        
        for i in range(self.playersCount-2):
            if(i == 0):
                self.images.append(self.ghostImages[1][0])
            elif(i == 1):
                self.images.append(self.ghostImages[2][0])
            elif(i == 2):
                self.images.append(self.ghostImages[3][0])

    def drawMap(self, debug=False):

        background = pygame.Surface((self.cellSize*self.gameMap.dimensions[0],self.cellSize*self.gameMap.dimensions[1]))
            
        background.fill(self.color)

        for i in range(self.gameMap.dimensions[0]):
            for j in range(self.gameMap.dimensions[1]):
                if(self.gameMap.getCell(i,j)>0 and self.gameMap.getCell(i,j)<4):
                    background.blit(self.images[self.gameMap.getCell(i,j)-1], (self.cellSize*i, self.cellSize*j))


        background = self.drawCharacters(background)
        

        if debug:
            background = self.drawCenterPlayers(background)
            background = self.drawCornersPlayers(background)
            

        background = pygame.transform.smoothscale(background,(self.width,self.height))
        return background

    def drawCenterPlayers(self,background):
        """
        Draws a rectangle at the center of the players for debugging purposes
        """
        color = (0,255,0)
        h,w = 10, 10
        for c in self.charsPosCenter: 
            sRectangle = pygame.Surface((h,w))
            sRectangle.fill(color)
            background.blit(sRectangle,(c[0]-(w//2),c[1]-(h//2)))

        return background

    def drawCornersPlayers(self, background):
        """
        Draws rectangles at players corners
        """
        color = (0,255,0)
        h,w = 10, 10


        for i, c in enumerate(self.charsPos): 
            width, height = self.images[i+3].get_width(), self.images[i+3].get_width()
            sRectangle = pygame.Surface((h,w))
            sRectangle.fill(color)
            background.blit(sRectangle,(c[0],c[1]))
            background.blit(sRectangle,(c[0]+width-w,c[1]))
            background.blit(sRectangle,(c[0],c[1]+height-h))
            background.blit(sRectangle,(c[0]+width-w,c[1]+height-h))
            # background.blit(sRectangle,(c[0]+-(w//2),c[1]-(h//2)))
            
        return background


    def getCellFromPos(self,x,y):
        scaledCellSize = (self.cellSize * self.width)/(self.cellSize * self.gameMap.dimensions[0])
        return (int(x//scaledCellSize),int(y//scaledCellSize))

    def getPosFromCell(self, x, y):
        scaledCellSize = (self.cellSize * self.width)/(self.cellSize * self.gameMap.dimensions[0])
        return (int(x*scaledCellSize),int(y*scaledCellSize))


    def drawCharacters(self,background):
        
        # for i in range(self.gameMap.dimensions[0]):
        #     for j in range(self.gameMap.dimensions[1]):
        #         if(self.gameMap.getCell(i,j)>=4 and self.gameMap.getCell(i,j)<9):
        #             charId = self.gameMap.getCell(i,j) #Which character are we painting
        #             #print(charId,self.charsPos,self.cellSize*i, self.cellSize*j,pygame.mouse.get_pos())
        for charId in self.gameMap.playersInMap:
            if(self.players[charId-4].alive):
                background.blit(self.images[charId-1], (self.charsPos[charId-4][0], self.charsPos[charId-4][1]))
        return background

    def getCharsPos(self):

        charPos = [0 for i in range(self.playersCount)]
        for i in range(self.gameMap.dimensions[0]):
            for j in range(self.gameMap.dimensions[1]):
                if(self.gameMap.getCell(i,j) in range(4,9)):
                    charPos[self.gameMap.getCell(i,j)-4]=(self.cellSize*i,self.cellSize*j)
            if(self.level == 2):
                pass#print(charPos)
        return charPos

    def getCharPosCenter(self):
        charPosCenter = []
        for i in range(len(self.charsPos)):
            #print("charposcenter",i)
            charPosCenter.append((self.charsPos[i][0]+(self.images[3+i].get_width()//2),self.charsPos[i][1]+(self.images[3+i].get_height()//2)))
        return charPosCenter

    def updateMapPlayer(self,playerId):
        #Updates the player position on the logical map using the default cellsize


        if(playerId == 0):
            pos = self.playerPos[0]
            oldPos = self.playerPos[1]
            #print("pos, oldPos",pos,oldPos)
        # pos = ((self.charsPos[playerId][0]+(self.images[3+playerId].get_width()//2))//self.cellSize,
        #     (self.charsPos[playerId][1]+(self.images[3+playerId].get_height()//2))//self.cellSize)
        else:
            pos = self.ghostPos[playerId-1][0]
            oldPos = self.ghostPos[playerId-1][1]

        #print(pos)
        
        if(playerId == 0):
            cell = self.gameMap.getCell(*pos) 
            if(self.gameMap.getCell(*pos) < 4):
                self.originalGameMap.updateMap(*pos, 0)
                self.gameMap.updateMap(*pos, 4+playerId)
            if(pos != oldPos):
                #print("entre aquiii")
                self.gameMap.updateMap(*oldPos, self.originalGameMap.getCell(*oldPos))
            if(cell == 2 and pos in self.pacDotPos):
                    #print("ACTUALICEEE")
                    self.updatePacDoteZone()
            if(cell == 3):
                self.activatePowerUp()
        else:
            if(self.gameMap.getCell(*oldPos) < 4):
                cell = self.gameMap.getCell(*pos)
                if(cell == 3):
                    self.activatePowerUp(playerId)
                self.gameMap.updateMap(*pos, 4+playerId)
                self.gameMap.updateMap(*oldPos, self.originalGameMap.getCell(*oldPos))
            
    def activatePowerUp(self, playerId = None):
        """
        Makes the changes necessary to activate the power up effects
        """
        if(self.level == 1):
            self.powerUp = True
            pygame.time.set_timer(pygame.USEREVENT+3, self.powerUpTime)
            if(not self.fchannel.get_busy()):
                self.fchannel = pygame.mixer.find_channel()
                self.fchannel.play(pygame.mixer.Sound("frightened.wav"), -1)
            else:
                pass#print("YA ESTABA SONANDO")
            for i in range(len(self.ghostImages)):
                self.ghostImages[i] = self.scaredGhostImages
        elif(self.level == 2):
            if(not playerId):
                playerId = 0
            if(playerId == 0):
                self.flockCount -= 1
            elif(playerId == 1 and self.flockCount ):
                self.flockCount += 1
            print("Player", playerId, "picked up a powerUp")
            pygame.time.set_timer(pygame.USEREVENT+3, self.powerUpTime)

    def deactivatePowerUp(self):
        """
        Makes the changes necessary to deactivate the power up effects
        """
        if(self.level == 1):
            self.powerUp = False
            pygame.time.set_timer(pygame.USEREVENT+3, 0)
            self.fchannel.stop()
            self.ghostImages = self.originalGhostImages[:]
        elif(self.level == 2):
            self.updatePowerUpPos()
            pygame.time.set_timer(pygame.USEREVENT+3, 0)
            pass

    def checkMovementPlayer(self,playerId):
        #Checks if the player can move in the desired direction using the borders and the center
        #Also, it on some cases adds the image width and heigth through the conditions
        
        width, height = self.images[playerId+3].get_width(), self.images[playerId+3].get_width()

        dx = dy = 1
        if(playerId == 0):
            dx = self.players[playerId].spdx 
            dy = self.players[playerId].spdy
        
        #print("Direccion: ",self.players[playerId].dir, "playerId", 2)
        return (((self.players[playerId].dir==1 and self.gameMap.getCell(((self.charsPos[playerId][0]+width+dx)//self.cellSize),self.charsPos[playerId][1]//self.cellSize)!=1) and
            (self.players[playerId].dir==1 and self.gameMap.getCell(((self.charsPos[playerId][0]+width+dx)//self.cellSize),(self.charsPos[playerId][1]+height)//self.cellSize)!=1)) or
            
            ((self.players[playerId].dir==2 and self.gameMap.getCell(((self.charsPos[playerId][0]-dx)//self.cellSize),self.charsPos[playerId][1]//self.cellSize)!=1) and
            (self.players[playerId].dir==2 and self.gameMap.getCell(((self.charsPos[playerId][0]-dx)//self.cellSize),(self.charsPos[playerId][1]+height)//self.cellSize)!=1)) or

            ((self.players[playerId].dir==3 and self.gameMap.getCell((self.charsPos[playerId][0]//self.cellSize),((self.charsPos[playerId][1]+height+dy)//self.cellSize))!=1) and
            (self.players[playerId].dir==3 and self.gameMap.getCell(((self.charsPos[playerId][0] + width)//self.cellSize),((self.charsPos[playerId][1]+height+dy)//self.cellSize))!=1)) or
            
            ((self.players[playerId].dir==4 and self.gameMap.getCell((self.charsPos[playerId][0]//self.cellSize),((self.charsPos[playerId][1]-dy)//self.cellSize))!=1)) and
            (self.players[playerId].dir==4 and self.gameMap.getCell(((self.charsPos[playerId][0] + width)//self.cellSize),((self.charsPos[playerId][1]-dy)//self.cellSize))!=1))
       

    def movePlayer(self,playerId):
        #print(self.charsPosCenter)
        
        if(self.checkMovementPlayer(playerId)):
            self.players[playerId].updatePos()
            if(playerId == 0):
                #print("Cambiando posicion personaje")
                self.playerPos[0] = (self.charsPosCenter[playerId][0]//self.cellSize,self.charsPosCenter[playerId][1]//self.cellSize )
        
            
        self.charsPos[playerId] = self.players[playerId].getPos()
        self.charsPosCenter=self.getCharPosCenter()
        self.updateMapPlayer(playerId)

    def correctDir(self, playerId):
        """
        Corrects ghost direction when he can't move 
        """
        width, height = self.images[playerId+3].get_width(), self.images[playerId+3].get_width()

        ans = None
    
        if (self.players[playerId].dir==1 and self.gameMap.getCell(((self.charsPos[playerId][0]+width+1)//self.cellSize),self.charsPos[playerId][1]//self.cellSize)==1):
            ans = 3           
        elif (self.players[playerId].dir==1 and self.gameMap.getCell(((self.charsPos[playerId][0]+width+1)//self.cellSize),(self.charsPos[playerId][1]+height)//self.cellSize)==1):
            ans = 4
        elif (self.players[playerId].dir==2 and self.gameMap.getCell(((self.charsPos[playerId][0]-1)//self.cellSize),self.charsPos[playerId][1]//self.cellSize)==1):
            ans = 3
        elif (self.players[playerId].dir==2 and self.gameMap.getCell(((self.charsPos[playerId][0]-1)//self.cellSize),(self.charsPos[playerId][1]+height)//self.cellSize)==1):
            ans = 4
        elif (self.players[playerId].dir==3 and self.gameMap.getCell((self.charsPos[playerId][0]//self.cellSize),((self.charsPos[playerId][1]+height+1)//self.cellSize))==1):
            ans = 1
        elif (self.players[playerId].dir==3 and self.gameMap.getCell(((self.charsPos[playerId][0] + width)//self.cellSize),((self.charsPos[playerId][1]+height+1)//self.cellSize))==1):
            ans = 2
        elif (self.players[playerId].dir==4 and self.gameMap.getCell((self.charsPos[playerId][0]//self.cellSize),((self.charsPos[playerId][1]-1)//self.cellSize))==1):
            ans = 1
        elif (self.players[playerId].dir==4 and self.gameMap.getCell(((self.charsPos[playerId][0] + width)//self.cellSize),((self.charsPos[playerId][1]-1)//self.cellSize))==1):
            ans = 2

        #print("Corrigiendo direccion a ", ans, "playerId", playerId)
        
        return ans
       


    def updateGhostDir(self, playerId):
        """
        Updates the ghost direction
        """
        if(self.level == 1):
            if(self.powerUp and playerId>0):
                #print(self.charsPos)
                self.ghostPos[playerId - 1][0] = ( self.charsPosCenter[playerId][0]//self.cellSize,self.charsPosCenter[playerId][1]//self.cellSize )
                if(not self.checkMovementPlayer(playerId) and self.ghostPos[playerId - 1][0]==self.ghostPos[playerId - 1][1]):
                    self.players[playerId].changeDir(self.correctDir(playerId))
                else:
                    self.paths[playerId - 1] = self.calcPath(self.gameMap.getRunawayMap(), playerId, self.gameMap.getFarthestEmptyPoint(*self.playerPos[0]))
                    #print(self.paths[playerId - 1], "id", playerId - 1)
                    if(self.paths[playerId - 1]):
                        self.players[playerId].changeDir(int(self.paths[playerId - 1][0]))
            
            #For the red and the purple ghost
            elif(playerId <= 2 and playerId>0):
                #If pakman has not been catched
                if( (self.charsPos[playerId][0] // self.cellSize != self.charsPos[0][0] // self.cellSize) or
                    (self.charsPos[playerId][1] // self.cellSize != self.charsPos[0][1] // self.cellSize) ):

                    #print(self.ghostPos)
                    self.ghostPos[playerId - 1][0] = ( self.charsPosCenter[playerId][0]//self.cellSize,self.charsPosCenter[playerId][1]//self.cellSize )

                    if(not self.checkMovementPlayer(playerId) and self.ghostPos[playerId - 1][0]==self.ghostPos[playerId - 1][1]):
                        #print("Corrigiendo direccion", playerId)
                        self.players[playerId].changeDir(self.correctDir(playerId))
                    else:
                        #print("Sin corregir direccion", not self.checkMovementPlayer(playerId), self.ghostPos)
                        self.paths[playerId - 1] = self.calcPath(None, playerId)
                        #print("Path", self.paths[playerId - 1])
                        #print(self.paths[playerId - 1], "id", playerId)
                        if(self.paths[playerId - 1]):
                            self.players[playerId].changeDir(int(self.paths[playerId - 1][0]))

            #For the purple ghost
            # elif(playerId == 2):
            #     #If pakman has not been catched
            #     if( (self.charsPos[playerId][0] // self.cellSize != self.charsPos[0][0] // self.cellSize) or
            #         (self.charsPos[playerId][1] // self.cellSize != self.charsPos[0][1] // self.cellSize) ):

            #         #print(self.charsPos)
            #         self.ghostPos[playerId - 1][0] = ( self.charsPosCenter[playerId][0]//self.cellSize,self.charsPosCenter[playerId][1]//self.cellSize )

            #         if(not self.checkMovementPlayer(playerId) and self.ghostPos[playerId - 1][0]==self.ghostPos[playerId - 1][1]):
            #             self.players[playerId].changeDir(self.correctDir(playerId))
            #         else:
            #             self.paths[playerId - 1] = self.calcPath(None, 2)
            #             #print(self.path)
            #             if(self.paths[playerId - 1]):
            #                 self.players[playerId].changeDir(int(self.paths[playerId - 1][0]))

            #For the orange ghost
            elif(playerId == 3):
                #If pakman has not been catched
                if( (self.charsPos[playerId][0] // self.cellSize != self.charsPos[0][0] // self.cellSize) or
                    (self.charsPos[playerId][1] // self.cellSize != self.charsPos[0][1] // self.cellSize) ):

                    self.ghostPos[playerId - 1][0] = ( self.charsPosCenter[playerId][0]//self.cellSize,self.charsPosCenter[playerId][1]//self.cellSize )

                    #If the ghost is not able to move then correct it's direction
                    if(not self.checkMovementPlayer(playerId) and self.ghostPos[playerId - 1][0]==self.ghostPos[playerId - 1][1]):
                            self.players[playerId].changeDir(self.correctDir(playerId))
                    else:
                        self.paths[playerId - 1] = self.calcPath(None, playerId)
                        self.noObstaclesPath = self.calcPath(self.noObstaclesMap, playerId)
                        if(len(self.noObstaclesPath) < self.visibleDistance and 
                            self.paths[playerId - 1] == self.noObstaclesPath):
                            if(self.paths[playerId - 1]):
                                self.players[playerId].changeDir(int(self.paths[playerId - 1][0]))

            elif(playerId == 4):
                #print("Actualizando direccion")
                #print("Estoy yendo a", self.pacDotPos[self.indexPacDot])
                #print("Estoy en", self.charsPos[playerId][0] // self.cellSize, self.charsPos[playerId][1] // self.cellSize)
                if( (self.charsPosCenter[playerId][0] // self.cellSize == self.pacDotPos[self.indexPacDot][0]) and
                    (self.charsPosCenter[playerId][1] // self.cellSize == self.pacDotPos[self.indexPacDot][1]) ):
                    #print("llegueeeeeeeeeeeeeeeeeeeeeeeeee")
                    self.indexPacDot = (self.indexPacDot + 1) % len(self.pacDotPos)


                else:
                    #print("no he llegado")
                    self.ghostPos[playerId - 1][0] = ( self.charsPosCenter[playerId][0]//self.cellSize,self.charsPosCenter[playerId][1]//self.cellSize )
                    #print(self.ghostPos[playerId - 1])
                    #If the ghost is not able to move then correct it's direction
                    if(not self.checkMovementPlayer(playerId) and self.ghostPos[playerId - 1][0]==self.ghostPos[playerId - 1][1]):
                        #print("Corregire mi direccion")
                        self.players[playerId].changeDir(self.correctDir(playerId))
                    else:
                        destination = self.pacDotPos[self.indexPacDot]
                        self.paths[playerId - 1] = self.calcPath(None, playerId, destination)
                        if(self.paths[playerId - 1]):
                        #print(self.paths[playerId - 1])
                            self.players[playerId].changeDir(int(self.paths[playerId - 1][0]))
                        else:
                            pass
                            #print("YA NO HAY MAS CAMINO PERO NO HE LLEGADO")
        elif(self.level == 2):
            destination = None
            if("followPowerUp" in self.bTree.getActiveNode().getName() ):
                destination = self.powerUpPos
            elif("followPakman" in self.bTree.getActiveNode().getName()):
                destination = self.playerPos[0]
            if(playerId <= 2 and playerId>0 and destination):
            #If destination has not been reached
                if( (self.charsPos[playerId][0] // self.cellSize != destination[0] // self.cellSize) or
                    (self.charsPos[playerId][1] // self.cellSize != destination[1] // self.cellSize) ):

                    #print(self.ghostPos)
                    self.ghostPos[playerId - 1][0] = ( self.charsPosCenter[playerId][0]//self.cellSize,self.charsPosCenter[playerId][1]//self.cellSize )

                    if(not self.checkMovementPlayer(playerId) and self.ghostPos[playerId - 1][0]==self.ghostPos[playerId - 1][1]):
                        #print("Corrigiendo direccion", playerId)
                        self.players[playerId].changeDir(self.correctDir(playerId))
                    else:
                        #print("Sin corregir direccion", not self.checkMovementPlayer(playerId), self.ghostPos)
                        self.paths[playerId - 1] = self.calcPath(None, playerId, destination)
                        #print("Path", self.paths[playerId - 1])
                        #print(self.paths[playerId - 1], "id", playerId)
                        if(self.paths[playerId - 1]):
                            self.players[playerId].changeDir(int(self.paths[playerId - 1][0]))

    def updatePlayerPos(self, playerId):
        """
        Updates the players pos measured in cells
        """
        if(playerId == 0):
            self.playerPos[1] = self.playerPos[0]
        else:  
            self.ghostPos[playerId-1][1] = self.ghostPos[playerId-1][0] 




game = Game(2)


