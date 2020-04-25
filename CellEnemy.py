import Level
from Cell import cellDistance
from random import shuffle
import gameplay
import random

class Enemy:


    def __init__(self, level):
        self.level = level

    def makeTurn(self):
        colors = []

        orderedEnemies = self.divideCells()

        enemiesTypes = {}

        for enemy in orderedEnemies:
            if enemy.getColor() not in colors:
                colors.append(enemy.getColor())
                enemiesTypes[enemy.getColor()] = [enemy]

            enemiesTypes[enemy.getColor()].append(enemy)

        for color in colors:
            #FOR LEARNNG IN LEVEL #1
            if self.level.number != 1:
                self.makeMoves(enemiesTypes[color])


    def makeMoves(self, enemies):

        shuffle(enemies)
        allEnemies = len(enemies)

        if (gameplay.currents["difficulty"] == "normal" or gameplay.currents["difficulty"] == "hard") and gameplay.currents["level"] in [7, 8, 9]:
            enemies = enemies[:2]

        #
        hasHealed = False
        hasAttacked = False
        for enemy in enemies:

            hasAttacked = self.attack(enemy)
            if gameplay.currents["difficulty"] == "easy":
                if hasAttacked:
                    break


            if gameplay.currents["difficulty"] == "normal":
                if hasAttacked:
                    break

            hasHealed = self.heal(enemy)


            if gameplay.currents["difficulty"] == "hard":
                if hasHealed:
                    break

        for enemy in enemies:
            if len(enemy.connections) > 0:
                self.stopConnection(enemy)


    def attack(self, enemy):
        target = self.findTarget(enemy, False)
        if target is not None:
            if enemy.getDistributedLife(target) < enemy.getHealth():
                if enemy.getHealth() > enemy.getSize() * 0.1 and gameplay.currents["difficulty"] == "hard"\
                    or enemy.getHealth() > enemy.getSize() * 0.2 and gameplay.currents["difficulty"] == "normal"\
                    or enemy.getHealth() > enemy.getSize() * 0.6 and gameplay.currents["difficulty"] == "easy":

                        if self.checkIfEndedTentacles(enemy):
                            enemy.addCell(target)
                            return True

        return False


    def stopConnection(self, enemy):
        for cell in reversed(enemy.connections):
            if cell.getColor() == enemy.getColor() and self.findTarget(enemy, False) is not None:
                if cell.getHealth() > cell.getSize()*0.2:
                    enemy.removeCell(cell)


    def checkIfEndedTentacles(self, enemy):
        for i in range(len(enemy.connections)):
            time = enemy.tentaclesTimes[i]
            if time < 90:
                return False
        return True

    def heal(self, enemy):
        if len(enemy.connections) < 2:
            target = self.findTarget(enemy, True)

            if target is not None and enemy.getHealth() > enemy.getSize()*0.5:
                if target.getHealth() < target.getSize()*0.1 and gameplay.currents["difficulty"] == "easy"\
                        or target.getHealth() < target.getSize()*0.3 and gameplay.currents["difficulty"] == "normal"\
                        or enemy.getHealth() >= enemy.getSize() - 1:
                    enemy.addCell(target)
                    return True
        return False


    def divideCells(self):

        enemies = []
        for cell in self.level.cellsArray:
            if cell.getColor() != gameplay.currents["player"] and cell.getColor() != "neutral":
                enemies.append(cell)
        return enemies

    def findTarget(self, enemy, same):

        targets = []

        #taking new targets
        for cell in self.level.cellsArray:
            if not same:
                if cell.getColor() != enemy.getColor():
                    if cell not in enemy.connections:
                        targets.append(cell)
            else:
                if cell.getColor() == enemy.getColor():
                    #enemy is self
                    if cell not in enemy.connections and cell is not enemy:
                        targets.append(cell)


        #calculating distances
        distances = [cellDistance(enemy, target)  for target in targets]



        nearest = None

        for i in range(len(targets)):
            if not self.level.checkIfBlocked(enemy, targets[i]):
                if nearest is None:
                    nearest = i

                if distances[i] < distances[nearest]:
                    nearest = i


        if nearest is None:
            return None
        else:
            return targets[nearest]