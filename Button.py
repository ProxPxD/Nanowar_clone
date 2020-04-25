import pygame
import gameplay

class Button:

    def __init__(self, name, tag, x, y, width, height):
        self.name = str(name)
        self.tag = str(tag)
        self.x = x
        self.y = y
        self.width = width
        self.height = height


    def getName(self):
        lowerName = self.name.lower()
        return lowerName

    def getTag(self):
        lowerTag = self.tag.lower()
        return lowerTag

    def display(self, screen):

        buttonImage = None

        if self.getTag() in gameplay.currents.values()\
                or (self.getTag() in gameplay.currents.keys() and gameplay.currents[self.getTag()] is True):
            buttonImage = gameplay.getImage("pictures/buttonDown.png")
        elif str(self.getTag()) in gameplay.actions["change level"] and self.getTag() != "next level":
            if int(self.getTag()) > gameplay.currents["max level"]:
                buttonImage = gameplay.getImage("pictures/buttonBlocked.png")

        if buttonImage is None:
            buttonImage = gameplay.getImage("pictures/button.png")


        if self.width != 0 and self.height != 0:

            resizedImage = pygame.transform.scale(buttonImage, (self.width, self.height) )

            fontSize = self.height//2
            font = pygame.font.SysFont("Avrile Serif", fontSize)
            label = font.render(self.name, 0, (255, 255, 255))


            textLength = len(self.name)

            labelX = self.x + (self.width - textLength * fontSize * 0.34) // 2
            labelY = self.y + self.height // 3

            screen.blit(resizedImage, (self.x, self.y) )
            screen.blit(label, (labelX, labelY))


    def isInRegion(self, mouseX, mouseY):
        return self.x < mouseX < self.x + self.width and  self.y < mouseY < self.y + self.height

    def __str__(self):
        string = str(self.name) +  " (" + str(self.x) + ", " + str(self.y) + ") "
        return string