"""
This module implements the flock class used for the Pak-man game
"""
from player import *


class Flock():

    def __init__(self, target, distanceFromTarget):
        print("Creating flock")
        self.target = target
        self.distanceFromTarget = distanceFromTarget
        self.followers = []
        self.arriveForces = []
        self.separationForces = []
        self.evadeForces = []

        self.flockCount = 0

        self.slowDownDistance = self.distanceFromTarget/2


        self.baseForce = (self.target.spdx, self.target.spdy)
        self.arriveBaseForce = [bf for bf in self.baseForce]
        self.separationBaseForce = [bf for bf in self.baseForce]
        self.evadeBaseForce = [bf for bf in self.baseForce]

        self.forceNorm = self.calcNorm(*self.baseForce)
        self.arriveNorm = self.calcNorm(*self.arriveBaseForce)
        self.separationNorm = self.calcNorm(*self.separationBaseForce) 
        self.evadeNorm = self.calcNorm(*self.evadeBaseForce)
        
        self.updateBehind()

    def updateBehind(self):
        """
        Updates the "behind" location that the followers should move to
        """
        self.behind = [self.target.posx, self.target.posy]
        print("Behind before update", self.behind)
        #If target is going to the right
        if(self.target.dir == 1):
            self.behind[0] -= self.distanceFromTarget
        #If target is going to the left 
        elif(self.target.dir == 2):
            self.behind[0] += self.distanceFromTarget
        #If target is going down
        elif(self.target.dir == 3):
            self.behind[1] -= self.distanceFromTarget
        #If target is going up
        elif(self.target.dir == 4):
            self.behind[0] += self.distanceFromTarget

        print("Behind after update", self.behind)

    def addFollower(self, follower):
        """
        Appends a new follower to the flock. It's expected to be a player object
        """
        self.followers.append(follower)
        self.arriveForces.append(self.arriveBaseForce)
        self.separationForces.append(self.separationBaseForce)
        self.evadeForces.append(self.evadeBaseForce)
        self.flockCount += 1


    def updateFollowerByID(self, followerId):
        """
        Updates the follower current speed adding all the forces
        """
        print("UPDATING FOLLOWER", followerId)
        self.updateBehind()
        self.updateForcesByID(followerId)
        print("FORCES UPDATED")
        # self.followers[followerId].spdx = self.arriveForces[followerId][0]
        # self.followers[followerId].spdy = self.arriveForces[followerId][1]
        # self.followers[followerId].spdx = sum(self.arriveForces[followerId][0],self.separationForces[followerId][0],
        #                                         self.evadeForces[followerId][0])

        # self.followers[followerId].spdy = sum(self.arriveForces[followerId][1],self.separationForces[followerId][1],
        #                                         self.evadeForces[followerId][1])



        self.followers[followerId].spdx += int(self.arriveForces[followerId][0])
        self.followers[followerId].spdy += int(self.arriveForces[followerId][1])

    def updateForcesByID(self, followerId):
        """
        Updates the forces of a single follower
        """
        self.updateArriveForceByID(followerId)

    def updateArriveForceByID(self, followerId):

        vector = (self.behind[0]-self.followers[followerId].posx, self.behind[1]-self.followers[followerId].posy) 
        
        print("vector",vector)
        normalizedVector = self.normalizeVector(*vector)

        print("normalized",normalizedVector)
        desiredVelocity = (normalizedVector[0] * self.arriveNorm,  normalizedVector[1] * self.arriveNorm)

        distance = self.getDistance(self.behind[0],self.behind[1],self.followers[followerId].posx,self.followers[followerId].posy)
        if(distance <= self.slowDownDistance):
            print("Decreasing speed")
            desiredVelocity = (desiredVelocity[0] * (distance/self.slowDownDistance), desiredVelocity[1] * (distance/self.slowDownDistance))
        print("desired",desiredVelocity)
        self.arriveForces[followerId] = (desiredVelocity[0] - self.followers[followerId].spdx, 
                                            desiredVelocity[1] - self.followers[followerId].spdy)
        
    def getDistance(self,x1,y1,x2,y2):
        return ((x2-x1)**2 + (y2-y1)**2)**(1/2)

    def calcNorm(self, x, y):
        return (x**2+y**2)**(1/2)

    def normalizeVector(self, x, y):
        norm = self.calcNorm(x,y)
        if(norm != 0):
            return (x/norm, y/norm)
        else:
            return (0, 0)

    def followerToString(self, followerId):
        string = "Follower No. "+str(followerId)+"\n"
        string += "Current pos: ("+str(self.followers[followerId].posx)+", "+str(self.followers[followerId].posy)+")\n"
        string += "Current speed: ("+str(self.followers[followerId].spdx)+", "+str(self.followers[followerId].spdy)+")\n"
        string += "Arrive force: "+str(self.arriveForces[followerId])
        return string

    def targetToString(self):
        string = "Target details: "+"\n"
        string += "Current pos: ("+str(self.target.posx)+", "+str(self.target.posy)+")\n"
        string += "Current speed: ("+str(self.target.spdx)+", "+str(self.target.spdy)+")\n"
        return string

        
def main():
    p1 = genericPlayer()
    p2 = genericPlayer()
    p2.setPos(10,10)
    flock = Flock(p1, 10)
    flock.addFollower(p2)

    for i in range(7):
        print("\n\nBEFORE UPDATE",i)
        print(flock.followerToString(0))
        flock.updateFollowerByID(0)
        print("\n\nAFTER UPDATE",i)
        print(flock.followerToString(0))
        p2.updatePosNoDir()
        print("\n\nAFTER POS UPDATE",i)
        print(flock.followerToString(0))
        print("\n")
        print(flock.targetToString())



if __name__ == "__main__":
    main()

