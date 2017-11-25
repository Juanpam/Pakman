"""
This modules makes a basic implementation of behaviour trees
"""

class BTree():
    """
    Tree structure used to simulate intelligent behaviour
    """
    __valid_types__ = ["sequence", "selector"]
    __valid_states__ = ["running", "fail", "success"]
    def __init__(self, treeType = "sequence", name = None):
        self.child = []
        self.state = "running"
        self.rcIndex = 0
        self.ready = True
        self.activeNode = self
        self.parent = None
        self.type = treeType
        self.leaf = True
        self.parent = None
        self.data = {}
        self.conditions = []
        if(not name):
            name = str(id(self))
        self.name = name

        assert self.type in self.__valid_types__

    def __str__(self):
        string = "Tree Id: "+str(id(self))+" | Name: "+ self.name +" | Type: "+str(self.type)+" | State: "+self.getState()
        return string
    def addChild(self, child):
        self.child.append(child)
        for key in self.data.keys():
            self.child.addData(key, self.getData(key))
        self.leaf = False
        child.parent = self

    def addChildren(self, children):
        for child in children:
            self.addChild(child)

    def addData(self, key, value = None):
        self.data[key] = value
        for child in self.child:
            child.addData(key, value)

    def getData(self, key):
        return self.data[key]

    def getAllData(self):
        return self.data

    def setData(self, data):
        self.data = data
        for child in self.child:
            child.setData(data)

    def removeChild(self,child):
        self.child.remove(child)
        if(not self.child):
            self.leaf = False

    def addCondition(self, condition):
        """
        THIS MODULE DOES NOT CHECK THAT GIVEN CONDITION IS WELL FORMED!
        """
        self.conditions.append(condition)

    def checkConditions(self):
        if(self.isLeaf()):
            ans = True
            for c in self.conditions:
                if not eval(c, self.data.copy()):
                    ans = False
                print("Checking condition",c,"Result:", eval(c, self.data.copy()))
            return ans

    def setReady(self, ready):
        self.ready = ready

    def updateState(self):
        print(self)
        print("datos")
        print(self.data)
        if(self.isLeaf()):
            print("In leaf")
            if(self.state == "running"):
                if(self.ready):
                    if(self.checkConditions()):
                        self.state = "success"
                        self.activeNode = self
                    else:
                        self.state = "fail"
        
        elif(self.type == "sequence"):
            print("In sequence")
            if(self.state == "running"):
                if(self.rcIndex == len(self.child)):
                    self.state = "success"
                else:   
                    if(self.child[self.rcIndex].getState() == "running"):
                        print("Updating child",str(self.child[self.rcIndex]))
                        self.child[self.rcIndex].updateState()
                        print("Child updated",str(self.child[self.rcIndex]))
                        if(self.child[self.rcIndex].getActiveNode() != self.child[self.rcIndex]):
                            self.activeNode = self.child[self.rcIndex].getActiveNode()
                        if(self.child[self.rcIndex].getState() == "fail"):
                            self.state = "fail"
                        elif(self.child[self.rcIndex].getState() == "success"):
                            self.activeNode = self.child[self.rcIndex].getActiveNode()
                            print("Actualizando activeNode", self.activeNode)
                            self.rcIndex += 1
                            print("DEBUG", self.rcIndex)
                            if(self.rcIndex != len(self.child)):
                                print("debug", self.child[self.rcIndex].isLeaf())
                            if(self.rcIndex == len(self.child) or not self.child[self.rcIndex].isLeaf()):
                                #print("DEBUG", self.rcIndex, self.child[self.rcIndex].isLeaf())
                                self.updateState()
                        
                        
        
        elif(self.type == "selector"):
            print("In selector")
            if(self.state == "running"):
                if(self.rcIndex == len(self.child)):
                    self.state = "fail"
                else:
                    if(self.child[self.rcIndex].getState() == "running"):
                        print("Updating child", str(self.child[self.rcIndex]))
                        self.child[self.rcIndex].updateState()
                        print("Child updated", str(self.child[self.rcIndex]))

                        if(self.child[self.rcIndex].getActiveNode() != self.child[self.rcIndex]):
                            self.activeNode = self.child[self.rcIndex].getActiveNode()
                            print("Actualizando activeNode", self.activeNode)
                        if(self.child[self.rcIndex].getState() == "fail"):
                            self.rcIndex += 1

                            #if(self.rcIndex == len(self.child) or not self.child[self.rcIndex].isLeaf()):
                            self.updateState()
                        elif(self.child[self.rcIndex].getState() == "success"):
                            self.activeNode = self.child[self.rcIndex].getActiveNode()
                            print("Actualizando activeNode", self.activeNode)
                            self.state = "success"



                    
    def restartTree(self):
        self.state = "running"
        for c in self.child:
            c.restartTree()


    def getActiveNode(self):
        return self.activeNode

    def getState(self):
        return self.state

    def getName(self):
        return self.name

    def setName(self, name):
        self.name = name

    def isLeaf(self):
        return self.leaf

    def runTree(self):
        pass

    def findNode(self, name):
        if(self.getName() == name):
            return self
        else:
            if(self.isLeaf()):
                return None
            else:
                for c in self.child:
                    ans = c.findNode(name)
                    if ans:
                        return ans
                return None


    def treeToString(self):
        string = str(self)
        if(not self.isLeaf()):
            string += "\nChildren of "+self.getName()+"\n"
            for c in self.child:
                string += c.treeToString()+"\n"
            # string += "---------"
            string = string[:]
        return string




def main():
    tree = BTree()
    # tree.addData("x", 6)
    tree.addCondition("x == 5")
    tree2 = BTree()
    # tree2.addData("y", 6)
    tree2.addCondition("y < 5")
    tree3 = BTree("selector")
    # print(tree.checkConditions(), tree2.checkConditions())
    tree3.addChildren([tree,tree2])
    

    treeT = BTree()
    treeT.addCondition("True")

    tree3.addChild(treeT)
    #tree3.updateState()
    #tree3.updateState()
    
    tree4 = BTree()
    tree4.addChild(tree3)

    tree4.addData("x", 6)
    tree4.addData("y", 6)

    print("Before",tree,tree2,treeT,tree3,tree4,"",sep="\n")
    tree4.updateState()
    print("between updates")
    # tree4.updateState()
    # tree4.updateState()
    # tree4.updateState()
    # tree4.updateState()
    print(tree,tree2,treeT,tree3,tree4,sep="\n")
    print("Nodo activo", tree4.getActiveNode().name)
    print("--------------------------------")
    print("--------------------------------")
    print("--------------------------------")
    print(tree4.treeToString())


if __name__ == "__main__":
    main()
