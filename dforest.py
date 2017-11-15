class dforest(object):
  """union-find with union-by-rank and path compression"""

  def __init__(self,cap=100):
    """creates a disjoint forest with the given capacity"""
    self.__parent = [ i for i in range(cap) ]
    self.__rank = [ 0 for i in range(cap) ]
    self.__count = [ 1 for i in range(cap) ]
    self.__ccount = cap

  def __str__(self):
    """return the string representation of the disjoint forest"""
    return str(self.__parent)

  def __len__(self):
    """return the length of the disjoint forest"""
    return len(self.__parent)

  def find(self,x):
    """return the representative of x in the disjoint forest"""
    ans = self.__parent[x]
    if ans!=x:
      self.__parent[x] = ans = self.find(ans)
    return ans

  def findCount(self, x):
    return self.__count[self.find(x)]

  def getAllCounts(self):
    return self.__count

  def union(self,x,y):
    """union of the trees of x and y"""
    rx,ry = self.find(x),self.find(y)
    if rx!=ry:
      kx,ky = self.__rank[rx],self.__rank[ry]
      if kx>=ky:
        self.__parent[ry] = rx
        self.__count[rx] += self.__count[ry]
        if kx==ky:
          self.__rank[rx] += 1
      else:
        self.__parent[rx] = ry
        self.__count[ry] += self.__count[rx]
      
      self.__ccount -= 1

  def ccount(self):
    """return the number of trees in the dijoint forest"""
    return self.__ccount

  def toMatrix(self, rows):
    matrix = []
    cols = len(self.__parent) // rows
    for r in range(rows):
      #print("r", r, "(rows-1)*r", (rows-1)*r, "cols", cols, "(rows-1)*r+cols", (rows-1)*r+cols)
      matrix.append([x for x in self.__parent[(cols)*r:(cols)*r+cols]])

    return matrix

  def maxCountParent(self):
    return self.find(self.__count.index(max(self.__count)))

  def maxCount(self):
    return max(self.__count)

  def setCount(self, x, count):
    """
    Manually sets count
    """
    self.__count[x] = count


if __name__ == "__main__":
  forest = dforest(20)
  for i in range(19):
    #print(forest.getAllCounts())
    #print(forest)
    #forest.union(i, i+1)
    pass

  print(forest.getAllCounts())
  print(forest)
  print(forest.toMatrix(5))
   