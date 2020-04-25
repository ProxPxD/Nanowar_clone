from Cell import Cell
import gameplay
import CellEnemy
import pygame
import re

tick = 120

class Level:

    def __init__(self, number):
        self.number = number

        self.loadLevel()

        self.enemy = CellEnemy.Enemy(self)

    def getPlayers(self):
        return self.numberOfPlayerCells

    def loadLevel(self):

        self.hasEnded = False
        self.winner = None

        self.numberOfPlayerCells = 1

        self.clickedCell = None
        self.triggeredCell = None

        self.clickedPoint = None
        self.isDrawingLine = False


        self.bariers = []
        self.cellsArray = []

        path = "levels/level" + str(self.number) + ".txt"
        level = open(path,"r")


        for line in level.readlines():
            if(line != None):
                if(line[0] == "#"):
                    cellValues = getCells(line)
                    self.cellsArray.append(Cell(cellValues[0], cellValues[1], cellValues[2], cellValues[3], cellValues[4]) )
                elif(line[0] == "!"):
                    barierPoints = getBarier(line)
                    self.bariers.append([(barierPoints[0],barierPoints[1]), (barierPoints[2], barierPoints[3])] )

    def __str__(self):
        return str(self.number) + " "


    def countPlayerCells(self):

        number = 0
        for cell in self.cellsArray:
            if cell.getColor() == gameplay.currents["player"]:
                number += 1

        self.numberOfPlayerCells = number
        if number == len(self.cellsArray) or  number == 0:
            self.hasEnded = True

    def clickCell(self, clickedPoint):

        mouseX = clickedPoint[0]
        mouseY = clickedPoint[1]

        for cell in self.cellsArray:
            if cell.checkIfClicked(mouseX, mouseY):
                self.clickedCell = cell
                return True
        self.clickedCell = None
        return False

    def triggerCell(self):
        if self.triggeredCell is None and self.clickedCell.getColor() == gameplay.currents["player"]:
            self.triggeredCell = self.clickedCell
            self.clickedPoint = self.triggeredCell.getPoint()

    def setTargetCell(self):
        if self.triggeredCell is not None and self.clickedCell is not None:

            blocked = self.checkIfBlocked(self.triggeredCell, self.clickedCell)

            if not blocked:
                self.triggeredCell.addCell(self.clickedCell)

        self.triggeredCell = None

    def checkIfBlocked(self, cell1, cell2):

        cell1Point = cell1.getPoint()
        cell2Point = cell2.getPoint()

        blocked = False

        for barier in self.bariers:
            barierPointA = barier[0]
            barierPointB = barier[1]
            if (not segmentIntersection(barierPointA, barierPointB, cell1Point, cell2Point)):
                blocked = False
            else:
                blocked = True
                break

        # cell intersection
        for cell in self.cellsArray:
            if cell is not cell1 and cell is not cell2:
                if self.cellIntersection(cell, cell1Point, cell2Point):
                    blocked = True
                    break

        # already connected this way
        if cell2 in cell1.connections:
            blocked = True

        # connected the other way and the same colour
        if cell1 in cell2.connections and cell1.getColor() is cell2.getColor():
            blocked = True

        return blocked


    def deleteConnections(self, secondClick):
        if self.isDrawingLine and self.clickedCell is None and self.triggeredCell is None:
            for cell in self.cellsArray:
                if len(cell.connections) > 0 and cell.getColor() == gameplay.currents["player"]:
                    cell.deleteConnections(self.clickedPoint, secondClick)


    def deactiveClick(self):
        self.clickedPoint = None
        self.clickedCell = None
        self.clickedPoint = None
        self.isDrawingLine = False

    def makeAction(self):
        global tick
        for cell in self.cellsArray:
            cell.heal()
            cell.send()

        if tick <= 0:
            self.enemy.makeTurn()
            if gameplay.currents["difficulty"] == "hard":
                tick = 20
            elif gameplay.currents["difficulty"] == "normal":
                tick = 40
            elif gameplay.currents["difficulty"] == "easy":
                tick = 80

        tick -= 1

        self.countPlayerCells()

    def drawLevel(self, screen, mousePosition):


        #drawinf bariers
        for barier in self.bariers:
            self.drawBarier(screen, barier)

        #drawing cells' tentacles
        for cell in self.cellsArray:
            cell.drawTentacles(screen)

        #drawing cells
        for cell in self.cellsArray:
            cell.drawSelf(screen)

        if gameplay.currents["menu"] == "inlevel":
            # drawing cell pointer
            if self.triggeredCell is not None and self.clickedPoint is not None:

                clickedCellPoint = self.triggeredCell.getPoint()

                color = (57, 200, 40)
                #if barier blocks, color red
                for barier in self.bariers:
                    pointA = barier[0]
                    pointB = barier[1]

                    if segmentIntersection(pointA, pointB, mousePosition, clickedCellPoint):
                        color = (150, 0, 0)

                for cell in self.cellsArray:
                    if cell is not self.triggeredCell:

                        #if cell blocks
                        if self.cellIntersection(cell, clickedCellPoint, mousePosition) \
                                and pointsDistance(mousePosition, cell.getPoint()) > cell.getSize()/2:
                            color = (150, 0, 0)

                self.drawLine(screen, self.clickedPoint, mousePosition, color)

            #drawing destroing line, color red
            if self.isDrawingLine and self.triggeredCell is None:
                self.drawLine(screen, self.clickedPoint, mousePosition)


    def drawLine(self, screen, pointA, pointB, color = (200, 200, 200), size = 3):

        Ax = int(pointA[0])
        Ay = int(pointA[1])

        Bx = int(pointB[0])
        By = int(pointB[1])

        lengthX = int(Ax - Bx)
        lengthY = int(Ay - By)

        iterations = int(max(abs(lengthX), abs(lengthY)) )

        for i in range(iterations):
            x = Bx + (i * lengthX) // iterations
            y = By + (i * lengthY) // iterations
            pygame.draw.circle(screen, color, (x, y), int(size) )


    def drawBarier(self, screen, barier):

        pointA = barier[0]
        pointB = barier[1]

        color = (50, 50, 50)
        size = 8

        self.drawLine(screen, pointA, pointB, color, size)


    def cellIntersection(self, cell, pointA, pointB):
        pointC = cell.getPoint()


        distance = distanceOfLineFromPoint(pointC, pointA, pointB)

        lengthX = abs(pointB[0] - pointA[0])
        lengthY = abs(pointB[1] - pointA[1])

        cellRelativeX = cell.getX() - pointA[0]
        cellRelativeY = cell.getY() - pointA[1]

        minX = min(pointA[0], pointB[0])
        minY = min(pointA[1], pointB[1])

        maxX = max(pointA[0], pointB[0])
        maxY = max(pointA[1], pointB[1])

        if distance > cell.size/2:
            return False
        else:
            return minX <= cell.getX() <= maxX and minY <= cell.getY() <= maxY


def clarifyLine(line):

    line = re.sub("[#! ]", '', line)
    line = re.sub("\n",'', line)

    return line
# from file
def getCells(line):
    global sizes

    line = clarifyLine(line)

    lineList = line.split(",")

    (screenWidth, screenHeight) = pygame.display.get_surface().get_size()

    #cordinates
    lineList[0] = float(lineList[0]) * screenWidth
    lineList[1] = float(lineList[1]) * screenHeight

    #size
    lineList[2] = gameplay.cellSizes[int(lineList[2]) ]

    #color
    if lineList[3] == "p":
        lineList[3] = gameplay.currents["player"]
    elif lineList[3] == "0":
        lineList[3] = "neutral"
    else:
        index = int(lineList[3]) - 1
        i=0
        for color in gameplay.colors:
            if i == index:
                lineList[3] = color
            if color != gameplay.currents["player"]:
                i += 1


    #health
    lineList[4] = int(lineList[4])

    return lineList


def getBarier(line):
    line = clarifyLine(line)

    lineList = line.split(",")

    (screenWidth, screenHeight) = pygame.display.get_surface().get_size()

    #first point coordinates
    lineList[0] = float(lineList[0]) * screenWidth
    lineList[1] = float(lineList[1]) * screenHeight

    #second point coordinates
    lineList[2] = float(lineList[2]) * screenWidth
    lineList[3] = float(lineList[3]) * screenHeight

    return lineList

def segmentIntersection(A, B, C, D):
    return counterclockwise(A, C, D) != counterclockwise(B, C, D) and counterclockwise(A, B, C) != counterclockwise(A, B, D)

def counterclockwise(A,B,C):
    return (C[1]-A[1])*(B[0]-A[0]) > (B[1]-A[1])*(C[0]-A[0])

def pointsDistance(A,B):
    return ((A[0] - B[0])**2 + (A[1] - B[1])**2)**0.5

def distanceOfLineFromPoint(pointC, linePointA, linePointB):

    c = pointsDistance(linePointA, linePointB)
    # times 2
    triangleArea = abs((pointC[0] - linePointA[0]) * (linePointB[1] - linePointA[1]) -
                       (pointC[1] - linePointA[1]) * (linePointB[0] - linePointA[0]))

    if c == 0:
        h = 0
    else:
        h = triangleArea/c

    return h


