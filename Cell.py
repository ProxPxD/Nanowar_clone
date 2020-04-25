import math
import gameplay
import pygame

pygame.mixer.init()

slurp = pygame.mixer.Sound('music/tentacleSound.wav')

class Cell:


    def __init__(self, x, y, size, color, health = None):
        self.x = int(x)
        self.y = int(y)
        self.size = size
        self.color = color
        self.setColorRGB()
        self.health = health if health != None else size//2
        self.connections = []


        self.maxTentacleTime = 100
        self.tentaclesTimes = [0, 0, 0]



    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def getPoint(self):
        return (self.x, self.y)

    def getSize(self):
        return self.size

    def getColor(self):
        return self.color

    def getColorRGB(self):
        return self.colorRGB

    def setColor(self, color):
        self.color = color

    def setColorRGB(self):
        if self.color == "red":
            self.colorRGB = (255, 0, 0)
        elif self.color == "green":
            self.colorRGB = (0, 255, 0)
        elif self.color == "blue":
            self.colorRGB = (0, 0, 255)
        elif self.color == "yellow":
            self.colorRGB = (255, 255, 0)
        else:
            self.colorRGB = (150, 150, 150)

    def getHealth(self):
        sumOfLength = 0
        for cell in self.connections:
            time = self.tentaclesTimes[self.connections.index(cell)]

            length = self.getDistributedLife(cell)

            sumOfLength += length*time

        return math.ceil(self.health - sumOfLength/self.maxTentacleTime )

    def getDistributedLife(self, cell):
        length = int(cellDistance(self, cell))

        if self in cell.connections:
            length //= 2

        return 8 * length

    def setHealth(self, health):
        self.health = health

    def modifyHealth(self, amount):
        self.health += amount

    def addCell(self, cell):
        if len(self.connections) < 3 and cell != self and self.getHealth() > 0:
            self.connections.append(cell)
            if gameplay.currents["sounds"]:
                slurp.play()
            self.tentaclesTimes[len(self.connections) - 1] = 0

    def removeCell(self, cell):
        self.tentaclesTimes[self.connections.index(cell)] = 0
        self.connections.remove(cell)

    def checkIfClicked(self, mouseX, mouseY):
        if ((mouseX - self.x)**2 + (mouseY - self.y)**2 )**0.5 <= self.size//2:
            return True
        return False


    def heal(self):
        if self.color != "neutral":
            if self.getHealth() - self.size <= -0.1:
                self.health += 0.045
            elif self.getHealth() - self.size > 0.1:
                self.health -= 0.002
        '''else:
            if self.getHealth() < self.size//2:
                self.health += 0.1'''

    def send(self):
            for cell in reversed(self.connections):
                if self.getHealth() > 0.5:
                    time = self.tentaclesTimes[self.connections.index(cell)]
                    if cell.getColor() != self.getColor() and time >= self.maxTentacleTime:
                        cell.getDamage()
                        self.health -= 0.012
                        #common attack
                        if self in cell.connections:
                            self.health += 0.01
                        if cell.getHealth() < 0:
                            cell.getCaptured(self.color)
                    elif cell.getColor() == self.getColor() and time >= self.maxTentacleTime:
                        cell.receiveHealth()
                        self.health -= 0.04
                else:
                    self.removeCell(cell)

    def receiveHealth(self):
            self.health += 0.03

    def getDamage(self):
        if self.getSize() > 90:
            self.health -= 0.060
        else:
            self.health -= 0.085

    def getCaptured(self, color):
        self.clearAllConnections()
        self.setColor(color)
        self.setColorRGB()
        self.setHealth(1)

    def clearAllConnections(self):
        self.connections = []

    def deleteConnections(self, pointA, pointB):
        for i in reversed(range(len(self.connections))):
            cell = self.connections[i]

            aimPoint = cell.getPoint() if self not in cell.connections else ((self.getX() + cell.getX())//2, (self.getY() + cell.getY())//2)

            if segmentIntersection(pointA, pointB, self.getPoint(), aimPoint) and self.tentaclesTimes[i] >= self.maxTentacleTime:

                #length f tentacle and how many is given
                length = pointsDistance(self.getPoint(), aimPoint)
                lostSide = distanceOfPointFromLine(aimPoint, pointA, pointB) if self not in cell.connections else 0

                #recovering nad giving life and removing cell
                self.splitTentacleHealth(length, lostSide, cell)


    def splitTentacleHealth(self, length, lostSide, cell):
        lostedPercentage = lostSide / length

        lifeOfTentacle = self.getDistributedLife(cell)

        sendedHealth = lostedPercentage * lifeOfTentacle

        self.modifyHealth(-sendedHealth)

        if cell.getColor() != self.getColor():
            cellHealth = cell.getHealth()
            if cellHealth - sendedHealth <= 0:
                cell.modifyHealth(-cellHealth)
                cell.getCaptured(self.getColor())
                cell.modifyHealth(sendedHealth - cellHealth)
            else:
                cell.modifyHealth(-sendedHealth)
        else:
            cell.modifyHealth(sendedHealth)

        self.removeCell(cell)

    def drawSelf(self, screen):
        cellImage = gameplay.cells[self.color, self.size]

        imageX = self.x - self.size // 2
        imageY = self.y - self.size // 2

        screen.blit(cellImage, (imageX, imageY))

        cellHealth = self.getHealth()

        fontSize = self.size// 3
        font = pygame.font.SysFont("monospace", fontSize)

        healthLabel = font.render(str(cellHealth), 1, (255, 255, 255))

        healthX = self.x + self.size // 4
        healthY = self.y + self.size // 4

        screen.blit(healthLabel, (healthX, healthY))


    def drawTentacles(self, screen):


        for cell in self.connections:
            aimX = cell.getX()
            aimY = cell.getY()
            for cell2 in cell.connections:
                if cell2 == self:
                    aimX = (aimX + self.x)//2
                    aimY = (aimY + self.y)//2
                    break
            self.drawTentacleTo(screen, aimX, aimY, self.connections.index(cell))

    def drawTentacleTo(self, screen, aimX, aimY, indexOfTime):

        time = self.tentaclesTimes[indexOfTime]

        lengthX = aimX - self.x
        lengthY = aimY - self.y

        #Length between Cells
        length = (lengthX**2 + lengthY**2)**0.5

        #Length of a tentacle
        tentacleLength = length * time/self.maxTentacleTime

        alpha = math.atan2(lengthY,lengthX)

        iterations = 2 * int(max(abs(lengthX), abs(lengthY) ) )

        (r, g, b) = self.getColorRGB()

        for i in range(iterations):
            tempx = (i*tentacleLength)/iterations
            tempy =  (-1)**i *5*math.sin(tempx*0.3)

            x = int(self.x + tempx*math.cos(alpha) - tempy*math.sin(alpha))
            y = int(self.y + tempx*math.sin(alpha) + tempy*math.cos(alpha))

            ri = r - i * (r - r//5) // iterations
            gi = g - i * (g - g//5) // iterations
            bi = b - i * (b - b//5) // iterations

            pygame.draw.circle(screen, (ri, gi, bi), (x, y), 1)


        if(self.tentaclesTimes[indexOfTime] < self.maxTentacleTime) and gameplay.currents["menu"] == "inlevel":
            self.tentaclesTimes[indexOfTime] += 6*gameplay.cellSizes[0]/length

    def __str__(self):
        cellString = "({},{}) {}, {}, health: {}, connections: {}".format(self.x, self.y, self.size, self.color, int(self.getHealth()), self.connections )
        return cellString


def cellDistance(cell1, cell2):
    distance = ((cell1.getX() - cell2.getX())**2 + (cell1.getY() - cell2.getY())**2)**0.5 /gameplay.cellSizes[0]
    return distance


def segmentIntersection(A, B, C, D):
    return counterclockwise(A, C, D) != counterclockwise(B, C, D) and counterclockwise(A, B, C) != counterclockwise(A, B, D)

def counterclockwise(A,B,C):
    return (C[1]-A[1])*(B[0]-A[0]) > (B[1]-A[1])*(C[0]-A[0])

def pointsDistance(A, B):
    return ((A[0] - B[0])**2 + (A[1] - B[1])**2 )**0.5

def distanceOfPointFromLine(pointC, linePointA, linePointB):

    c = pointsDistance(linePointA, linePointB)
    # times 2
    triangleArea = abs((pointC[0] - linePointA[0]) * (linePointB[1] - linePointA[1]) -
                       (pointC[1] - linePointA[1]) * (linePointB[0] - linePointA[0]))

    if c == 0:
        h = 0
    else:
        h = triangleArea/c

    return h