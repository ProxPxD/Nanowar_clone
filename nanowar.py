#!/usr/bin/python
import pygame
import gameplay
import time

def loadFiles():
    imagesNames = {'neutralCell.png', 'greenCell.png', 'redCell.png', "blueCell.png", "yellowCell.png", 'background.png', 'button.png', 'buttonDown.png', 'buttonBlocked.png'}

    imagesPaths = ['pictures/' + name for name in imagesNames]

    gameplay.loadImages(imagesPaths)

    gameplay.scaleCells()

    gameplay.loadMenus()

    gameplay.loadActions()

    gameplay.loadLevels()

pygame.init()

height = 576
width  = 1024

pygame.display.set_caption("NanoWar")

factor = width//gameplay.cellSizes[0]

screen = pygame.display.set_mode((width, height) )

loadFiles()

clock = pygame.time.Clock()
done = False


pygame.mixer.init()

pygame.mixer.music.load("music/soundtrack.wav")

pygame.mixer.music.play(-1)


#time.sleep(0.1)

while not done:
    for event in pygame.event.get():
        gameplay.onPress(event, screen)


        if (event.type == pygame.QUIT or gameplay.isOpen == False):
            done = True

    gameplay.play(screen)


    clock.tick(60)



    pygame.display.flip()


