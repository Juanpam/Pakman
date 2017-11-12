"""
Artificial Intelligence for Videogames
Pontificia Universidad Javeriana Cali
Members:
    Paula Correa
    Juan Pablo Méndez


Main file for the Pakman project.   
Makes use of the Pygame and Sys module.
"""


import sys, pygame, spritesheet, map, player, astar
pygame.init()


class Game():
    """
    Class created to store the most used game methods
    """
    black = 0, 0, 0
    #playersCount = 2
    def __init__(self):


        #Configuration variables
        #Setting screen proportions
        self.wideScreen = False
        if(self.wideScreen):
            self.ratio = 9/16
        else:
            self.ratio = 1

        #Default width
        self.width = 600
        self.height = int(self.width * self.ratio)
        size = self.width, self.height
        self.screen = pygame.display.set_mode(size)

        #Cell size in pixels
        self.cellSize = 50

        #Map set-up
        mapToLoad = "map6.txt"
        self.gameMap = map.Map(mapToLoad)
        self.originalGameMap = map.Map(mapToLoad)
        self.noObstaclesMap = self.gameMap.getNoObstaclesMap()
        self.AStarMap = self.gameMap.getAStarMap()
        self.playersCount = self.gameMap.playersCount
        #Uncomment to print map
        #for row in self.gameMap.matrix:
            #print(row)

        #Load sprites
        self.loadSpriteSheet()
        self.charsPos = self.getCharsPos() #Characters top-left edge position
        #print(self.charsPos) 
        self.charsPosCenter = self.getCharPosCenter() #Characters center position

        #Draw map based on the gameMap
        self.background = self.drawMap()

        #There are at least 2 players always
        self.players = [player.msPakman(), player.ghost()]

        #Add additional players/ghosts
        for i in range(2,self.playersCount):
            self.players.append(player.ghost())

        #Find path to follow Ms. Pakman
        self.path = self.calcPath()
        self.noObstaclesPath = self.calcPath(self.noObstaclesMap)
        #Uncomment to print calculated path
        #print(self.path)
        
        #Update players logical position based on the position in the drawn map
        for p in range(len(self.players)):
            self.players[p].setPos(*self.charsPos[p])

        #Initial ghost position in cells 
        #Actual position is stored on the first position of each tuple on this array and old position on the second one
        self.ghostPos = [[( self.charsPosCenter[p][0]//self.cellSize,self.charsPosCenter[p][1]//self.cellSize ),
                            ( self.charsPosCenter[p][0]//self.cellSize,self.charsPosCenter[p][1]//self.cellSize )] for p in range(1,len(self.players))]

        
        #If there is a path between Ms. Pakman and the ghost the direction is updated and the path is consumed
        if(self.path):
            self.players[1].changeDir(int(self.path[0]))
            self.path=self.path[1:]
        
        
        self.refreshImagesTime = 100
        self.createEvents()
        self.infiniteLoop()

    def calcPath(self, gameMap=None):
        """
        Calculates path and translates it to being compatible with the actual map
        """
        if(not gameMap):
            gameMap = self.AStarMap 
        path = astar.pathFind(gameMap,astar.directions,astar.dx,astar.dy,self.charsPosCenter[1][0]//self.cellSize,self.charsPosCenter[1][1]//self.cellSize,self.charsPosCenter[0][0]//self.cellSize,self.charsPosCenter[0][1]//self.cellSize)
        path = astar.translatePath(path)
        #print(path)
        return path

    def infiniteLoop(self):
        """
        Infinite loop for the game
        """
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()
                if event.type == pygame.USEREVENT+1:
                    self.updateImages()
                if event.type == pygame.KEYDOWN and event.key==pygame.K_UP:
                    self.players[0].changeDir(4)
                if event.type == pygame.KEYDOWN and event.key==pygame.K_DOWN:
                    self.players[0].changeDir(3)
                if event.type == pygame.KEYDOWN and event.key==pygame.K_LEFT:
                    self.players[0].changeDir(2)
                if event.type == pygame.KEYDOWN and event.key==pygame.K_RIGHT:
                    self.players[0].changeDir(1)


            self.updateGhostDir(1)
            for i,p in enumerate(self.players):
                self.movePlayer(i)
            # self.movePlayer(1)
            # self.movePlayer(0)
            self.updateGhostsPos(1)
            self.background=self.drawMap(False)
            self.screen.fill(self.black)
            self.screen.blit(self.background, (0,0))

            # self.screen.blit(self.msPakmanImages[self.imageId],(50*4,50*4))
            # for j in range(len(self.ghostImages)):
            #     for i in range(len(self.ghostImages[j])):
            #         self.screen.blit(self.ghostImages[j][self.imageId],(50*i,50*j))
            #print(pygame.mouse.get_pos(), self.charsPos)
            # print(self.charsPos)
            pygame.display.flip()

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
        ghostsCount = 4

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

        ## Re arranging image order
        temp = self.ghostImages[1]
        self.ghostImages[1] = self.ghostImages[3]
        self.ghostImages[3] = temp 
        for i in range(self.playersCount-2):
            if(i == 0):
                self.images.append(self.ghostImages[3][0])

    def drawMap(self, debug=False):

        background = pygame.Surface((self.cellSize*self.gameMap.dimensions[0],self.cellSize*self.gameMap.dimensions[1]))
            
        background.fill(self.black)

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
        
        for i in range(self.gameMap.dimensions[0]):
            for j in range(self.gameMap.dimensions[1]):
                if(self.gameMap.getCell(i,j)>=4 and self.gameMap.getCell(i,j)<9):
                    charId = self.gameMap.getCell(i,j) #Which character are we painting
                    #print(charId,self.charsPos,self.cellSize*i, self.cellSize*j,pygame.mouse.get_pos())
                    background.blit(self.images[charId-1], (self.charsPos[charId-4][0], self.charsPos[charId-4][1]))
        return background

    def getCharsPos(self):

        charPos = [0 for i in range(self.playersCount)]
        for i in range(self.gameMap.dimensions[0]):
            for j in range(self.gameMap.dimensions[1]):
                if(self.gameMap.getCell(i,j) in range(4,9)):
                    charPos[self.gameMap.getCell(i,j)-4]=(self.cellSize*i,self.cellSize*j)
        return charPos

    def getCharPosCenter(self):
        charPosCenter = []
        for i in range(len(self.charsPos)):
            #print(i)
            charPosCenter.append((self.charsPos[i][0]+(self.images[3+i].get_width()//2),self.charsPos[i][1]+(self.images[3+i].get_height()//2)))
        return charPosCenter

    def updateMapPlayer(self,playerId):
        #Updates the player position on the logical map using the default cellsize


        pos = ((self.charsPos[playerId][0]+(self.images[3+playerId].get_width()//2))//self.cellSize,
            (self.charsPos[playerId][1]+(self.images[3+playerId].get_height()//2))//self.cellSize)
        
        oldPos = self.ghostPos[playerId-1][1]

        #print(pos)
        
        if(playerId == 0):
            self.gameMap.updateMap(*pos, 4+playerId)
            self.originalGameMap.updateMap(*pos, 4+playerId)
        else:
            self.gameMap.updateMap(*oldPos, self.originalGameMap.getCell(*oldPos))
            

    def checkMovementPlayer(self,playerId):
        #Checks if the player can move in the desired direction using the borders and the center
        #Also, it on some cases adds the image width and heigth through the conditions
        
        width, height = self.images[playerId+3].get_width(), self.images[playerId+3].get_width()

        #print("Direccion: ",self.players[playerId].dir)
        return (((self.players[playerId].dir==1 and self.gameMap.getCell(((self.charsPos[playerId][0]+width+1)//self.cellSize),self.charsPos[playerId][1]//self.cellSize)!=1) and
            (self.players[playerId].dir==1 and self.gameMap.getCell(((self.charsPos[playerId][0]+width+1)//self.cellSize),(self.charsPos[playerId][1]+height)//self.cellSize)!=1)) or
            
            ((self.players[playerId].dir==2 and self.gameMap.getCell(((self.charsPos[playerId][0]-1)//self.cellSize),self.charsPos[playerId][1]//self.cellSize)!=1) and
            (self.players[playerId].dir==2 and self.gameMap.getCell(((self.charsPos[playerId][0]-1)//self.cellSize),(self.charsPos[playerId][1]+height)//self.cellSize)!=1)) or

            ((self.players[playerId].dir==3 and self.gameMap.getCell((self.charsPos[playerId][0]//self.cellSize),((self.charsPos[playerId][1]+height+1)//self.cellSize))!=1) and
            (self.players[playerId].dir==3 and self.gameMap.getCell(((self.charsPos[playerId][0] + width)//self.cellSize),((self.charsPos[playerId][1]+height+1)//self.cellSize))!=1)) or
            
            ((self.players[playerId].dir==4 and self.gameMap.getCell((self.charsPos[playerId][0]//self.cellSize),((self.charsPos[playerId][1]-1)//self.cellSize))!=1)) and
            (self.players[playerId].dir==4 and self.gameMap.getCell(((self.charsPos[playerId][0] + width)//self.cellSize),((self.charsPos[playerId][1]-1)//self.cellSize))!=1))
       

    def movePlayer(self,playerId):
        #print(self.charsPosCenter)
        
        if(self.checkMovementPlayer(playerId)):
            self.players[playerId].updatePos()
            
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

        #print("Corrigiendo direccion a ", ans)
        
        return ans
       


    def updateGhostDir(self, playerId):
        """
        Updates the ghost direction
        """
           
        #For the red ghost
        if(playerId == 1):
            #If pakman has not been catched
            if( (self.charsPos[playerId][0] // self.cellSize != self.charsPos[0][0] // self.cellSize) or
                (self.charsPos[playerId][1] // self.cellSize != self.charsPos[0][1] // self.cellSize) ):

                #print(self.charsPos)
                self.ghostPos[playerId - 1][0] = ( self.charsPosCenter[playerId][0]//self.cellSize,self.charsPosCenter[playerId][1]//self.cellSize )

                if(not self.checkMovementPlayer(1) and self.ghostPos[playerId - 1][0]==self.ghostPos[playerId - 1][1]):
                    self.players[1].changeDir(self.correctDir(playerId))
                else:
                    self.path = self.calcPath()
                    #print(self.path)
                    if(self.path):
                        self.players[playerId].changeDir(int(self.path[0]))

        #For the orange ghost
        # elif(playerId == 2):
        #     pass

    def updateGhostsPos(self, playerId):
        """
        Updates the ghosts pos measured in cells
        """
        self.ghostPos[playerId-1][1] = self.ghostPos[playerId-1][0] 




game = Game()


