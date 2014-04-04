# Created by T. J. Tkacik
# Spring of 2014 at the University of North Carolina
import sys, time, os, math, random, numpy
from numpy import linalg

class modi(object):
    def __init__(self, files, loud):
        self.loud = loud
        self.cdk = files + ".cdk"
        self.act = files + ".act"
        self.descriptorMatrix = []
        self.distanceMatrix = []
        self.compounds = []
        self.neighbor = []
        self.activities = {}
        
        for lines in open(self.cdk):
            self.descriptorMatrix.append(lines.strip().split("\t"))
        for x in range(1, len(self.descriptorMatrix)):
            for y in range(1, len(self.descriptorMatrix[0])):
                self.descriptorMatrix[x][y] = float(self.descriptorMatrix[x][y])
            self.compounds.append(self.descriptorMatrix[x][0])
            self.descriptorMatrix[x] = self.descriptorMatrix[x][1:]
        self.descriptorMatrix = self.descriptorMatrix[1:]

        self.printMatrix(self.descriptorMatrix, "Original Descriptors")
                
        self.normColumn(self.descriptorMatrix)
        
        self.printMatrix(self.descriptorMatrix, "Normalized Descriptors")
        
        self.distanceMatrix = self.calcDistances(self.descriptorMatrix)
        
        self.printMatrix(self.distanceMatrix, "Euclidean Distances")
        
        self.neighbor = self.calcNeighbor(self.distanceMatrix)
                
        for lines in open(self.act):
            activity = (lines.strip().split(" "))
            self.activities[activity[0]] = activity[1]
        
        #print self.neighbor 
        print self.calcMODI()
        
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
        for x in range(0, len(descriptorMatrix)):
            distanceMatrix[x] = [0]*len(descriptorMatrix)
            for y in range(x+1, len(descriptorMatrix)):
                distance = numpy.linalg.norm(numpy.array(descriptorMatrix[x])-numpy.array(descriptorMatrix[y]))
                distanceMatrix[x][y] = float(distance)
        return distanceMatrix

    def normColumn(self, descriptorMatrix):
        for y in range(0, len(descriptorMatrix[0])):
            row = []          
            for x in range(0, len(descriptorMatrix)):
                row.append(descriptorMatrix[x][y])
            mean = numpy.mean(row)
            stdv = numpy.std(row)
            if stdv == 0:
                for x in range(0, len(descriptorMatrix)):
                    descriptorMatrix[x][y] = (descriptorMatrix[x][y] - mean)
            else:
                for x in range(0, len(descriptorMatrix)):
                    descriptorMatrix[x][y] = (descriptorMatrix[x][y] - mean)/stdv
            
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
    
    modi("mini", loud)
    
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