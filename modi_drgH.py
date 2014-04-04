# Created by T. J. Tkacik
# Spring of 2014 at the University of North Carolina
import sys, time, os, math, random, numpy
from numpy import linalg

class modi(object):
    def __init__(self, files, loud):
        self.loud = loud
        self.cdk = files + ".dragonH"
        self.act = files + ".act"
        self.descriptorMatrix = []
        self.distanceMatrix = []
        self.compounds = []
        self.neighbor = []
        self.activities = {}
        self.startTime = time.clock()
        
        toDrop = []
        for lines in open(self.cdk):
            self.descriptorMatrix.append(lines.strip().split("\t"))
        for x in range(3, len(self.descriptorMatrix)):
            for y in range(2, len(self.descriptorMatrix[x])):
                self.descriptorMatrix[x][y] = float(self.descriptorMatrix[x][y])
                if self.descriptorMatrix[x][y] == -999 and y not in toDrop:
                    #print -999, "found! Appending", y
                    toDrop.append(y)
            self.compounds.append(self.descriptorMatrix[x][1])
            self.descriptorMatrix[x] = self.descriptorMatrix[x][2:]
        self.descriptorMatrix = self.descriptorMatrix[3:]
        toDrop.sort(reverse=True)
        for y in toDrop:
            #print "deleting column", y
            for x in range(0, len(self.descriptorMatrix)):
                #print "deleting", self.descriptorMatrix[x-3][y-2]
                del self.descriptorMatrix[x-3][y-2]
                
        self.printMatrix(self.descriptorMatrix, "Original Descriptors")
        timeInt = self.reportTime("To Load Descriptors")
                
        self.normColumn(self.descriptorMatrix)
        
        self.printMatrix(self.descriptorMatrix, "Normalized Descriptors")
        timeInt = self.reportTime("To Normalize Descriptors", timeInt)
        
        """self.distanceMatrix = self.calcDistances(self.descriptorMatrix)
        self.printMatrix(self.distanceMatrix, "Euclidean Distances")
        timeInt = self.reportTime("To Calculate Distances", timeInt)
        self.neighbor = self.calcNeighbor(self.distanceMatrix)"""
        
        self.neighbor = self.calcMinNeighbors(self.descriptorMatrix)
        
        timeInt = self.reportTime("To Calculate Neighbors", timeInt)
                
        for lines in open(self.act):
            activity = (lines.strip().split(" "))
            self.activities[activity[0]] = activity[1]
        
        timeInt = self.reportTime("Total Run Time", None, True)
        print "MODI:", self.calcMODI()
        
        """for x in range(0, len(self.compounds)):
            print self.compounds[x], self.neighbor[x]
        """
    def reportTime(self, message = None, start = None, override = False):
        #if not self.loud or not override:
        #    return
        if start == None:
            start = self.startTime
        print message, ":", round(time.clock() - start, 3)
        return time.clock()
        
    def calcMODI(self):
        cats = {}
        modi = 0.0
        N = 0
        for x in range(0, len(self.neighbor)):
            category = self.activities[self.compounds[x]]
            if category not in cats:
                cats[category] = (0, 0)
                N += 1
            if category == self.activities[self.neighbor[x]]:
                cats[category] = (cats[category][0]+1, cats[category][1]+1)
            else:   cats[category] = (cats[category][0], cats[category][1]+1)  
        for category in cats:
            modi += float(cats[category][0])/cats[category][1]
       
        return modi/N
    
    def calcNeighbor(self, distanceMatrix):
        neighbor = [None]*len(distanceMatrix)
        
        for x in range(0, len(distanceMatrix)):
            distance = float("inf")
            for y in range(0, x):
                if distanceMatrix[y][x] < distance:
                    distance = distanceMatrix[y][x]
                    neighbor[x] = self.compounds[y]
            for y in range(x+1, len(distanceMatrix)):
                if distanceMatrix[x][y] < distance:
                    distance = distanceMatrix[x][y]
                    neighbor[x] = self.compounds[y]
        return neighbor

    def calcDistances(self, descriptorMatrix):
        distanceMatrix = [None]*len(descriptorMatrix)
        for x in range(0, len(descriptorMatrix)):
            distanceMatrix[x] = [0]*len(descriptorMatrix)
            for y in range(x+1, len(descriptorMatrix)):
                distance = numpy.linalg.norm(numpy.array(descriptorMatrix[x])-numpy.array(descriptorMatrix[y]))
                distanceMatrix[x][y] = float(distance)
        return distanceMatrix
    
    def calcMinNeighbors(self, descriptorMatrix): #TODO: Distinguish Descriptor and Distance Matrices
        neighbors = [None]*len(descriptorMatrix)
        distanceMatrix = [None]*len(descriptorMatrix)
        for x in range(0, len(descriptorMatrix)):
            distanceMatrix[x] = [0]*len(descriptorMatrix)
        for x in range(0, len(distanceMatrix)):
            min = float("inf")
            for y in range(0, x):
                if distanceMatrix[x][y] == 0:
                    if distanceMatrix[y][x] < min:
                        distance = float(numpy.linalg.norm(numpy.array(descriptorMatrix[x])-numpy.array(descriptorMatrix[y])))
                        distanceMatrix[x][y] = distance
                if distanceMatrix[x][y] != 0 and distanceMatrix[x][y] < min:
                    min = distanceMatrix[x][y]
                    neighbors[x] = self.compounds[y]
              #  min = min(min, distanceMatrix[x][y])
            for y in range(x+1, len(descriptorMatrix)):
                if distanceMatrix[x][y] < min:
                    distance = float(numpy.linalg.norm(numpy.array(descriptorMatrix[x])-numpy.array(descriptorMatrix[y])))
                    distanceMatrix[x][y] = distance
                    distanceMatrix[y][x] = distance
                    if distance < min: 
                        min = distance
                        neighbors[x] = self.compounds[y]
                    for xx in range(x+1, y):
                        diff = abs(distanceMatrix[x][y] - distanceMatrix[y][xx])
                        if diff < distanceMatrix[xx][y]:
                            distanceMatrix[xx][y] = diff
                       
        return neighbors

    def normColumn(self, descriptorMatrix):
        toDrop = []
        for y in range(0, len(descriptorMatrix[0])):
            column = []          
            for x in range(0, len(descriptorMatrix)):
                column.append(descriptorMatrix[x][y])
#             print column
            mean = numpy.mean(column)
            stdv = numpy.std(column)
            #print mean, stdv
            if stdv == 0:
                toDrop.append(y)
                #for x in range(0, len(descriptorMatrix)):
                #    descriptorMatrix[x][y] = (descriptorMatrix[x][y] - mean)
            else:
                for x in range(0, len(descriptorMatrix)):
                    descriptorMatrix[x][y] = (descriptorMatrix[x][y] - mean)/stdv
        toDrop.reverse()
        for y in toDrop:
            for x in range(0, len(descriptorMatrix)):
                del descriptorMatrix[x][y]
            
    def printMatrix(self, matrix, title = None, override = False):
        if self.loud or override:
            print ""
            if title != None:
                print title
            for rows in matrix:
                print rows

          
if  __name__ =='__main__':
    
    if "-l" in sys.argv:
        loud = True
    else: loud = False
    
    if "-f" in sys.argv:
        file = sys.argv[sys.argv.index("-f")+1]
    else: file = "25"
    
    modi(file, loud)
    
    ''' board = "game_boards/ReesesPieces.txt"
    heuristic = ""
    loud = False
    p1 = "human"
    p2 = "human"
    if "--help" in sys.argv:
        print """
        candyGame.py by T. J. Tkacik
        
        Accepted flags:

        --help    for this help information
        -l        for loud output, default False
        -b        for game board source, default ReesesPieces.txt
        -p1       for player one, default is human, see below
        -p2       for player two, default is human, see below
            players are given in form <playertype><depth>
                Acceptable playertypes: human minimax alphabeta quiescence
            Default depth is used if none is given
                Default depths: human:0 minimax:3 alphabeta:4 quiescence:2
                
        Examples:   candyGame.py -l -p2 minimax3 -b Ayds.txt
                    candyGame.py -b long.txt -p1 minimax -p2 alphabeta3
                    candyGame.py -b oases.txt -p1 human -p2 quiescence
        """
        sys.exit(0)

    if "-b" in sys.argv:
        board = "game_boards/" + sys.argv[sys.argv.index("-b")+1]
    if "-p1" in sys.argv:
        p1 = sys.argv[sys.argv.index("-p1")+1]
    if "-p2" in sys.argv:
        p2 = sys.argv[sys.argv.index("-p2")+1]
    
    game = candyGame(board, p1, p2, loud)
'''