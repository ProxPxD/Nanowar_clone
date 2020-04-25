import pygame
import gameplay
from Button import Button

class Menu:

    def __init__(self, name, x, y, width, height, buttonsNames, columns, additional):
        self.name = name

        self.space = 30
        self.cols = columns
        self.rows = len(buttonsNames["english"]) // columns

        self.buttons = self.createButtons(gameplay.currents["language"], buttonsNames, x, y, width, height)

        if len(additional) > 0:
            self.buttons.append(self.createAdditional(additional) )


    def getName(self):
        lowerName = self.name.lower()
        return lowerName

    def createButtons(self, language, buttonsNames, x, y, width, height):
        buttons = []

        buttonWidth = width // self.cols - self.space
        buttonHeight = height // self.rows - self.space

        if buttonWidth < 0 and buttonHeight < 0:
            buttonWidth = 0
            buttonWidth = 0

        displayedNames = buttonsNames[language]

        for i in range(self.cols):
            for j in range(self.rows):

                buttonX = self.space // 2 + x + (buttonWidth + self.space // 2) * i
                buttonY = self.space // 2 + y + (buttonHeight + self.space // 2) * j

                label = displayedNames[j*self.cols + i]
                tag = buttonsNames["english"][j*self.cols + i]
                button = Button(label, tag, buttonX, buttonY, buttonWidth, buttonHeight)
                buttons.append(button)

        return buttons

    def createAdditional(self, additional):
        (screenWidth, screenHeight) = pygame.display.get_surface().get_size()

        name = additional["name"][gameplay.currents["language"]]
        tag = additional["name"]["english"]
        x = int(float(additional["x"]) * screenWidth)
        y = int(float(additional["y"]) * screenHeight)
        width = int(float(additional["width"]) * screenWidth)
        height = int(float(additional["height"]) * screenHeight)


        button = Button(name, tag, x, y, width, height)
        return button

    def display(self, screen):

        for button in self.buttons:
            button.display(screen)


    def triggerButton(self, mousePosition):
        mouseX = mousePosition[0]
        mouseY = mousePosition[1]

        for button in self.buttons:
            if button.isInRegion(mouseX, mouseY):
                return button.getTag()

        return self.getName()

    def __str__(self):
        string = str(self.getName())
        return string