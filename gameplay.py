import pygame
import os
import Level
import Menu
import json

imageLibrary = {}

cellSizes = [60, 80, 120]

cells = {}

levels = []
enemy = None

menus = {}
menusNames = []

actions = {}
actionsTypes = []

colors = [
    "red",
    "blue",
    "yellow",
    "green"
]

#options
currents = {
    "language": "english",
    "menu": "main",
    "level": -1,
    "player": "green",
    "music": True,
    "sounds": True,
    "difficulty": "normal",
    "max level": 1
}


isOpen = True


def loadImages( paths):
    global imageLibrary

    for path in paths:
        if(os.path.exists(path)):
            image = pygame.image.load(path)
            imageLibrary[path] = image

def loadLevels():
    global levels, menus
    levels = []
    for i in range(12):
        levels.append( Level.Level(i + 1) )

def loadMenus():
    global menus, menusNames, currents
    menus = {}
    menusNames = []

    with open("data/menus.json") as f:
         data = json.load(f)

    (screenWidth, screenHeight) = pygame.display.get_surface().get_size()


    for menuName in data["menus"]:

        menusNames.append(menuName)

        heightRatio = data["menus"][menuName]["height"]
        widthRatio = data["menus"][menuName]["width"]

        menuHeight = int(screenHeight * heightRatio)
        menuWidth = int(screenWidth * widthRatio)

        menuPointX = (screenWidth - menuWidth) // 2
        menuPointY = (screenHeight - menuHeight) // 2

        columns = data["menus"][menuName]["columns"]
        buttons = data["menus"][menuName]["buttons"]

        additional = data["menus"][menuName]["additional"]

        menu = Menu.Menu(menuName, menuPointX, menuPointY, menuWidth, menuHeight, buttons, columns, additional)
        menus[menuName] = menu

def loadActions():
    global actions, actionsTypes

    with open("data/actions.json") as f:
         data = json.load(f)

    for actionType in data["actions"]:

        actionsTypes.append(actionType)

        actions[actionType] = data["actions"][actionType]


def scaleCells():
    global imageLibrary
    global cells, cellSizes
    global colors

    allCells = colors.copy()
    allCells.append("neutral")

    for color in allCells:
        for key in imageLibrary.keys():
            if color in key:
                for size in cellSizes:
                    cells[color, size] = pygame.transform.scale(imageLibrary[key], (size, size) )
                break


def getImage(path):
    global imageLibrary

    image = imageLibrary.get(path)
    if image is None:
        image = imageLibrary.get

    return image

# END OF LOADING FROM DICTIONARY

#keys
keyUP = False
keyDOWN = False
keyRIGHT = False
keyLEFT = False

mouseClick = False
mouseDown = False


def pres(event, screen):
    keyPressed = pygame.key.get_pressed()

    global keyUP, keyDOWN, keyRIGHT, keyLEFT
    global mouseClick, mouseDown


    if keyPressed[pygame.K_UP]:
        keyUP = True
    else: keyUP = False

    if keyPressed[pygame.K_DOWN]: keyDOWN = True
    else: keyDOWN = False

    if keyPressed[pygame.K_RIGHT]: keyRIGHT = True
    else: keyRIGHT = False

    if keyPressed[pygame.K_LEFT]: keyLEFT = True
    else: keyLEFT = False

    if keyPressed[pygame.K_r] and currents["level"] >= 0:
        executeAction("restart")

    if keyPressed[pygame.K_p] and currents["level"] >= 0:
        currents["menu"] = "#"

    if keyPressed[pygame.K_n] and currents["level"] >= 0:
        level = levels[currents["level"]]
        level.hasEnded = True


    if event.type == pygame.MOUSEBUTTONUP:
        mouseDown = False
        mouseClick = True

        mousePosition = pygame.mouse.get_pos()

        triggerMenu(mousePosition)

        if currents["level"] >= 0 and currents["menu"] == "inlevel":

            level = levels[currents["level"]]

            level.clickCell(mousePosition)

            level.deleteConnections(mousePosition)
            level.setTargetCell()

            level.deactiveClick()

    else:
        mouseClick = False

    if event.type == pygame.MOUSEBUTTONDOWN:
        mouseDown = True
        if currents["level"] >= 0 and currents["menu"] == "inlevel":

            level = levels[currents["level"]]

            if not level.hasEnded:
                clickedPoint = pygame.mouse.get_pos()
                level.clickedPoint = clickedPoint

                level.clickCell(clickedPoint)
                if level.clickedCell is not None:
                    level.triggerCell()

                level.isDrawingLine = True


def triggerMenu(mousePosition):
    global currents, menusNames, menu

    menu = menus[currents["menu"]]

    action = menu.triggerButton(mousePosition)

    if action in menusNames:
        currents["menu"] = action

    executeAction(action)


def executeAction(action):
    global actions, actionsTypes

    for actionType in actionsTypes:
        if action in actions[actionType]:
            if actionType == "change level":
                changeLevel(action)

            elif actionType == "change language":
                changeLanguage(action)

            elif actionType == "return":
                goBack(action)

            elif actionType == "restart":
                levels[currents["level"]].loadLevel()
                currents["menu"] = "inlevel"

            elif actionType == "change difficulty":
                currents["difficulty"] = action

            elif actionType == "change player color":
                currents["player"] = action
                loadLevels()

            elif actionType == "music settings":
                setMusic(action)

            elif actionType == "credits":
                currents["level"] = -1
                currents["menu"] = "main"




#tmp funtions

def changeLevel(level):
    global currents, isInMenu
    if currents["level"] < len(levels) - 1:
        if level == "next level":
            currents["level"] = currents["level"] + 1
            currents["menu"] = "inlevel"
        elif int(level) <= currents["max level"]:
            level = int(level)
            currents["level"] = level - 1
            currents["menu"] = "inlevel"

        levels[currents["level"]].loadLevel()
    else:
        currents["menu"] = menus["game won"]
        currents["level"] = -1

def changeLanguage(language):
    global currents
    currents["language"] = language
    loadMenus()

def goBack(action):
    global isOpen, currents, menus
    if action == "return":
        #To END
        for menuName in menusNames:
            menu = menus[menuName]
            for button in menu.buttons:
                if button.getTag() == currents["menu"]:
                    currents["menu"] = menu.getName()
    elif action == "select level":
        currents["level"] = -1
    elif action == "quit":
        isOpen = False

def setMusic(action):
    if action == "music":
        currents["music"] = not currents["music"]
        if currents["music"]:
            pygame.mixer.music.play(-1)
        else:
            pygame.mixer.music.stop()
    elif action == "sounds":
        currents["sounds"] = not currents["sounds"]

#end of temp funtions

def play(screen):
    global isInMenu
    #makeEvents()

    if currents["level"] >= 0 and currents["menu"] == "inlevel":
        level = levels[currents["level"]]
        level.makeAction()
        if level.hasEnded:
            if level.numberOfPlayerCells == 0:
                currents["menu"] = "lost"
            elif currents["level"] < len(levels) - 1 :
                currents["max level"] = max(currents["level"], currents["max level"] + 1)
                currents["menu"] = "won"
            else:
                currents["menu"] = "game won"



    draw(screen)


def draw(screen):

    drawBackground(screen)

    if currents["level"] >= 0:
        mousePosition = pygame.mouse.get_pos()

        level = levels[currents["level"]]
        level.drawLevel(screen, mousePosition)

    #print(currents["menu"])
    #print(menus[currents["menu"]])
    #print(menusNames)
    menus[currents["menu"]].display(screen)
    #menus["game won"].display(screen)



def drawBackground(screen):
    screen.fill((0, 0, 0))

    background = getImage("pictures/background.png")

    screenResolution = pygame.display.get_surface().get_size()

    scaledBackground = pygame.transform.scale(background, screenResolution)
    screen.blit(scaledBackground, (0,0) )


def findMenu(menuToFind):
    global menusNames
    for menu in  menusNames:
        for i in range(len( menusNames[menu])):
            if(menusNames[menu][i] == menuToFind):
                return menu
    return "main"
