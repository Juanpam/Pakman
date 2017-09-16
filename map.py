"""
This module implements a Map class used to represent in a logic way the map in Pakman


"""
from random import *

class Map():
    """
    This class implements using a matrix the Pakman map. It's used to generate the optimal path for each
    ghost and to draw the map object's in the screen acordingly
    """

    def __init__(self):
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
        #5 represents a blue ghost
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


    def getCell(self, x, y):
        """
        Returns the cell in the (x,y) position
        """
        if(x>=len(self.matrix) or y>=len(self.matrix[0])):
            return 0
        return self.matrix[y][x]

    def updateMap(self, x, y, cellContent):
        """
        Updates the cell in the x,y position for with the given cellContent
        """

        self.matrix[y][x]=cellContent