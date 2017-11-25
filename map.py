"""
This module implements a Map class used to represent in a logic way the map in Pakman


"""
from random import *
from os import path

class Map():
    """
    This class implements using a matrix the Pakman map. It's used to generate the optimal path for each
    ghost and to draw the map object's in the screen accordingly
    """

    def __init__(self,filename=""):
        """
        Class initialization
        """

        self.dimensions = (20,20)
        self.tomatoCount = 2
        #Random initialization of the map
        #0 represents an empty cell
        #1 represents a wall
        #2 represents a pill
        #3 represents a tomato (Big pill)
        #4 represents Ms Pakman
        #5 represents a red ghost
        #6 represents a purple ghost
        #7 represents a orange ghost
        #8 represents a blue ghost
        if(not filename):
            self.matrix = [[0 for i in range(self.dimensions[0])]for j in range(self.dimensions[1])]
            for i in range(self.dimensions[0]):
                for j in range(self.dimensions[1]):
                    cellId = randint(0,3)
                    while(cellId == 3 and self.tomatoCount<=0):
                        cellId = randint(0,3)
                    if(cellId == 3):
                        self.tomatoCount -= 1 
                    self.matrix[i][j] = cellId
            self.matrix[randint(0,self.dimensions[0]-1)][randint(0,self.dimensions[0]-1)] = 4
            self.matrix[randint(0,self.dimensions[0]-1)][randint(0,self.dimensions[0]-1)] = 5        


        else:
            self.load_map(filename)
            self.dimensions = (len(self.matrix[0]),len(self.matrix))

        self.updatePlayersCount()

        if(not self.playersCount>=2):
            #A valid map contains at least to the player and a ghost
            try:
                raise Exception("Loaded map must have at least 2 players. Exiting...")

            except Exception as error:
                raise


    def load_map(self,filename):
        """
        Loads map from txt file ö called 'filename'
        The map must contain at least Ms. Pakman (a number 4)
        """
        folder=path.dirname(__file__)
        self.matrix=[]
        with open(path.join(folder,filename),'rt') as f:
            for line in f:
                row = [int(character) for character in str.strip(line)]
                self.matrix.append(row)

    def getCell(self, x, y):
        """
        Returns the cell in the (x,y) position
        """
        if(x>=len(self.matrix) or x<0 or y>=len(self.matrix[0]) or y<0):
            return 1
        return self.matrix[y][x]

    def updateMap(self, x, y, cellContent):
        """
        Updates the cell in the x,y position for with the given cellContent
        """

        self.matrix[y][x]=cellContent

    def getAStarMap(self):
        """
        Returns a valid map to be used with the AStar algorithm
        """
        AStarMap = [[0 for i in range(self.dimensions[0])]for j in range(self.dimensions[1])]
        for i in range(len(self.matrix)):
            for j in range(len(self.matrix[i])):
                if(self.matrix[i][j]==1):
                    AStarMap[i][j] = 1
        return AStarMap

    def getNoObstaclesMap(self):
        """
        Returns the same as getAStarMap but without obstacles
        """

        AStarMap = self.getAStarMap()
        for i in range(len(AStarMap)):
            for j in range(len(AStarMap[i])):
                if(AStarMap[i][j] == 1):
                    AStarMap[i][j] = 0

        return AStarMap

    def getDistanceInCells(self,x1,y1,x2,y2):
        return int(((x2-x1)**2 + (y2-y1)**2)**(1/2))

    def getFarthestEmptyPoint(self,x1,y1):
        """
        Given a (x1,y1) coordinate, the farthest empty point to that coordinate is returned
        """
        farthestPoint = (x1, y1)
        maxDistance = 0
        for y2 in range(self.dimensions[0]):
            for x2 in range(self.dimensions[1]):
                distance = self.getDistanceInCells(x1,y1,x2,y2)
                if(distance > maxDistance and self.getCell(x2,y2) == 0):
                    maxDistance = distance
                    farthestPoint = (x2,y2)
        
        return farthestPoint

    def getRunawayMap(self):
        #Arrays used to check cells adjacency
        dx = [0, 1, 0, -1, 1, -1, 1, -1]
        dy = [-1, 0, 1, 0, 1, 1, -1, -1]
        runAwayMap = [[0 for i in range(self.dimensions[0])]for j in range(self.dimensions[1])]
        for i in range(len(self.matrix)):
            for j in range(len(self.matrix[i])):
                if(self.matrix[i][j]==1):
                    runAwayMap[i][j] = 1
                elif(self.matrix[i][j] == 4):
                    for k in range(len(dx)):
                        u,v = j+dx[k], i+dy[k]
                        if(0 <= u < self.dimensions[0] and 
                            0 <= v < self.dimensions[1]):
                            runAwayMap[v][u] = 1

        return runAwayMap
    def getLevel2Map(self):
        """
        Returns a map with no tomatoes for the level 2
        """
        level2Map = [[c if c!=3 else 0 for c in r] for r in self.matrix]
        # for i in range(len(self.matrix)):
        #     for j in range(len(self.matrix[i])):
        #         if(self.matrix[i][j]==1):
        #             level2Map[i][j] = 1
        return level2Map

    def updatePlayersCount(self):
        """
        Updates the players count using the current map
        """
        self.playersInMap = []
        self.playersCount = 0
        for row in self.matrix:
            for cell in row:
                if(cell >= 4):
                    self.playersInMap.append(cell)
                    self.playersCount += 1
