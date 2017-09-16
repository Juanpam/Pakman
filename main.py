"""
Artificial Intelligence for Videogames
Pontificia Universidad Javeriana Cali
Members:
    Paula Correa
    Juan Pablo Méndez


Main file for the Pakman project.   
Makes use of the Pygame and Sys module.
"""


import sys, pygame, spritesheet, map, player
pygame.init()


class Game():
    """
    Class created to store the most used game methods
    """
    black = 0, 0, 0
    playersCount = 2
    def __init__(self):


        #Configuration variables
        #Setting screen proportions
        self.wideScreen = False
        if(self.wideScreen):
            self.ratio = 9/16
        else:
            self.ratio = 1
        self.width = 600
        self.height = int(self.width * self.ratio)
        size = self.width, self.height
        self.screen = pygame.display.set_mode(size)
        self.cellSize = 50
        
        self.imageId = 0
        self.gameMap = map.Map()
        self.loadSpriteSheet()
        self.charsPos = self.getCharsPos() #Character positions on top-left edge
        self.charsPosCenter = self.getCharPosCenter()
        self.background = self.drawMap()
        

        for i in self.gameMap.matrix:
            print(i)


        
        self.player = player.msPakman()
        self.player.setPos(*self.charsPos[0])
        self.createEvents()
        self.infiniteLoop()

    def infiniteLoop(self):
        """
        Infinite loop for the game
        """
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()
                if event.type == pygame.USEREVENT+1:
                    self.imageId = (self.imageId + 1)%8
                if event.type == pygame.KEYDOWN and event.key==pygame.K_UP:
                    self.player.changeDir(4)
                if event.type == pygame.KEYDOWN and event.key==pygame.K_DOWN:
                    self.player.changeDir(3)
                if event.type == pygame.KEYDOWN and event.key==pygame.K_LEFT:
                    self.player.changeDir(2)
                if event.type == pygame.KEYDOWN and event.key==pygame.K_RIGHT:
                    self.player.changeDir(1)


            self.movePlayer()
            self.background=self.drawMap()
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
        pygame.time.set_timer(pygame.USEREVENT+1,100)

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

        self.images=[self.wallImage,self.pillImage,self.tomatoImage,self.msPakmanImages[0],self.ghostImages[2][0]]

    def drawMap(self):

        background = pygame.Surface((self.cellSize*self.gameMap.dimensions[0],self.cellSize*self.gameMap.dimensions[1]))
            
        background.fill(self.black)

        for i in range(self.gameMap.dimensions[0]):
            for j in range(self.gameMap.dimensions[1]):
                if(self.gameMap.getCell(i,j)>0 and self.gameMap.getCell(i,j)<4):
                    background.blit(self.images[self.gameMap.getCell(i,j)-1], (self.cellSize*i, self.cellSize*j))


        background = self.drawCharacters(background)
        background = pygame.transform.smoothscale(background,(self.width,self.height))
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
            print(i)
            charPosCenter.append((self.charsPos[0][0]+(self.images[3+i].get_width()//2),self.charsPos[0][1]+(self.images[3+i].get_height()//2)))
        return charPosCenter

    def updateMapPlayer(self):
        #Updates the player position on the logical map using the default cellsize


        pos = ((self.charsPos[0][0]+(self.images[4].get_width()//2))//self.cellSize,
            (self.charsPos[0][1]+(self.images[4].get_height()//2))//self.cellSize)
        #print(pos)
        self.gameMap.updateMap(*pos, 4)

    def movePlayer(self):

        #Checks if the player can move in the desired direction
        print(self.charsPosCenter)
        if((self.player.dir==1 and self.gameMap.getCell((self.charsPosCenter[0][0]//self.cellSize)+1,self.charsPosCenter[0][1]//self.cellSize)!=1) or
            (self.player.dir==2 and self.gameMap.getCell((self.charsPosCenter[0][0]//self.cellSize)-1,self.charsPosCenter[0][1]//self.cellSize)!=1) or
            (self.player.dir==3 and self.gameMap.getCell((self.charsPosCenter[0][0]//self.cellSize),(self.charsPosCenter[0][1]//self.cellSize)-1)!=1) or
            (self.player.dir==4 and self.gameMap.getCell((self.charsPosCenter[0][0]//self.cellSize),(self.charsPosCenter[0][1]//self.cellSize)+1)!=1)):
            
            self.player.updatePos()

        print(self.player.dir,((self.charsPosCenter[0][0]//self.cellSize),self.charsPosCenter[0][1]//self.cellSize))
        self.charsPos[0] = self.player.getPos()
        self.charsPosCenter=self.getCharPosCenter()
        self.updateMapPlayer()

game = Game()


