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
        
        self.imageId = 0
        self.createEvents()
        self.loadSpriteSheet()
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

            self.screen.fill(self.black)
            self.screen.blit(self.background, (0,0))

            self.screen.blit(self.msPakmanImages[self.imageId],(80*4,32*4))
            for j in range(len(self.ghostImages)):
                for i in range(len(self.ghostImages[j])):
                    self.screen.blit(self.ghostImages[j][self.imageId],(80*i,32*j))
            pygame.display.flip()

    def createEvents(self):

        pygame.time.set_timer(pygame.USEREVENT+1,100)

    def loadSpriteSheet(self):

        #Ghosts variables
        ghostHeight, ghostWidth = 32, 33
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
            self.ghostImages.append(self.sSheet.images_at([(initialXGhost+(intervalSizeG*x),initialYGhost+(intervalSizeG*y),ghostWidth ,ghostHeight) for y in range(gSpriteCount)]))
        self.msPakmanImages=self.sSheet.images_at([(initialXMSPak,initialYMSPak+(intervalSizeMSPak*y),msPakWidth,msPakHeight) for y in range(msPakCount)])

game = Game()


