import pygame
import time
import copy
import random
import sys

from actors import *
from data import *

pygame.init()

# Game properties
screenWidth = 1600
screenHeight = 950
tickDelay = 0.01  # Time between updates. Lower time = faster game.
gameTitle = "Zuma but Tetris"

screen = pygame.display.set_mode([screenWidth, screenHeight])
pygame.display.set_caption(gameTitle)

# Game class
class Game:
    def __init__(self):
        # Data
        self.dataManager = Levels()
        
        # Game values
        self.gameState = 4  # 0 = Single Player, 1 = Boss Fight, 2 = Game Over, 3 = Victory, 4 = Main Menu, 5 = Help Screen, 6 = Play Menu, 7 = Story Screen

        # Sprite Sheets
        self.pieceSheet = pygame.image.load("sprites/TetrisBlocks.png").convert()

        # Fonts
        self.gameplayFont = pygame.font.SysFont('Agency FB', 25)
        self.headerFont = pygame.font.SysFont('Agency FB', 35)
        self.titleFont = pygame.font.SysFont('Agency FB', 50)

        # Level
        self.level = 16
        self.difficulty = 0
        self.cBoss = 4
        self.displayLevel = "Tetrahedron - Boss"
        
        # Progression
        self.nextLevel = [0, 0, 0, 0]
        self.highScores = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        ]
        self.cutscenes = [0, 0, 0, 0, 0, 0, 0, 0]

        # Play screen
        self.currentChapter = 0
        self.clickedMosue = False

        # Story Screen
        self.storyPart = 0

        # Gameplay
        self.bgColour = (138, 102, 52)
        
        self.pBoard = Board()
        self.pPiece = Piece(1)
        self.ghostPiece = self.pPiece
        
        self.dropDelay = 0
        self.nextDrop = self.dropDelay

        self.isDASing = False
        self.DASDelay = 4
        self.staticDASDelay = 16

        self.didSave = False

        self.tRotates = 0
        self.prevTLoc = [-999, -999]

        self.heldPiece = None
        self.pressedHold = False

        self.staticSlideFreeze = 30
        self.slideFreeze = self.staticSlideFreeze
        
        self.cMDelay = 0
        self.cDropDelay = 0

        self.pScore = 0
        self.linesLeft = 100
        self.combo = 0
        self.tetrisCombo = 0

        self.recClear = ""
        self.recDelay = 0

        self.recalculateGhost = True

        self.hasGarbage = True
        self.garbageDelay = 500
        self.nextGarbage = self.garbageDelay

        self.nextQueue = [0, 0, 0]
        self.nextPieces = []
        self.nextPiecesDisplayAdjust = [[1055, 135], [1040, 170], [1040, 120], [1060, 120], [1050, 140], [1050, 140], [1040, 120]]
        self.pieceBag = [0, 1, 2, 3, 4, 5, 6]

        # Gameplay - Boss
        self.boss = Boss([30, 40, 80], [1200, 1000, 300], [3, 5, 1], [40, 60, 100], "Tetrahedron", 4)
        self.bossStun = 0

        self.geminiAttackDelay = 0
        self.geminiIsAttacking = False

        self.orionAttackDelay = 0
        self.orionIsAttacking = False
        self.heldDropSpeed = 0

        # Gameplay - Background
        self.isSpace = False
        self.stars = []
        self.nStarDelay = 0

        # Gameplay - Pauses
        self.gameOverDelay = 0
        self.victoryDelay = 0

        # Control Lock
        self.pressedRotate = False
        self.hardDropped = False
        self.held = False


        f = open("data/progression.txt", "r")
        index = 0
        for line in f.readlines():
            self.nextLevel[index] = int(line.strip())
            index += 1
        f.close()

        f = open("data/cutscenes.txt", "r")
        index = 0
        for line in f.readlines():
            self.cutscenes[index] = int(line.strip())
            index += 1
        f.close()

        files = ["data/1S.txt", "data/2S.txt", "data/3S.txt", "data/4S.txt"]
        index1 = 0
        index2 = 0
        for file in files:
            f = open(file, "r")

            for line in f.readlines():
                self.highScores[index1][index2] = int(line.strip())
                index2 += 1
            
            f.close()
            index1 += 1
            index2 = 0
        
        self.transition()

    # In-built functions
    def getPieceSprite(self, colour):
        return {
            'P': (70, 35, 35, 35),
            'O': (35, 35, 35, 35),
            'B': (0, 35, 35, 35),
            'L': (0, 0, 35, 35),
            'R': (70, 0, 35, 35),
            'G': (35, 0, 35, 35),
            'Y': (104, 0, 35, 35),
            'C': (104, 35, 35, 35)
        }.get(colour, (0, 0, 35, 35))

    def renderText(self, text, font, x, y, colour=(255, 255, 255)):
        text = font.render(text, True, colour)
        text_rect = text.get_rect(center=((text.get_rect().width / 2) + x, (text.get_rect().height / 2) + y))
        screen.blit(text, text_rect)

    def renderTextCenter(self, text, font, x, y, colour=(255, 255, 255)):
        line = font.render(text, False, colour)
        line_rect = line.get_rect(center = (x, y))
        screen.blit(line, line_rect)

    def transition(self):
        self.pieceBag = [0, 1, 2, 3, 4, 5, 6]
        self.nextQueue = [0, 0, 0]
        self.nextPieces = []
        self.pressedHold = False
        self.stars = []
        self.pBoard = Board()
        self.pScore = 0
        self.combo = 0
        self.tetrisCombo = 0
        self.recalculateGhost = True
        self.recClear = ""
        self.recDelay = 0
        self.prevTLoc = [-999, -999]
        self.didSave = False
        self.bossStun = 0
        self.geminiAttackDelay = 0
        self.geminiIsAttacking = False
        self.orionAttackDelay = 0
        self.orionIsAttacking = False

        if self.gameState == 0 or self.gameState == 1:
            self.gameState = self.dataManager.levelState[self.level]
        
        if self.gameState == 0:
            self.displayLevel = self.dataManager.levelNames[self.level]
            self.linesLeft = self.dataManager.levelLinesLeft[self.level][self.difficulty]
            self.dropDelay = self.dataManager.levelDropSpeed[self.level][self.difficulty]
            self.bgColour = self.dataManager.levelBackground[self.level]
            if self.bgColour == (0, 0, 0):
                self.isSpace = True
            else:
                self.isSpace = False
            self.cDropDelay = 100
            if self.dataManager.levelGarbage[self.level][self.difficulty] > 0:
                self.hasGarbage = True
                self.garbageDelay = self.dataManager.levelGarbage[self.level][self.difficulty]
                self.nextGarbage = self.garbageDelay
            else:
                self.hasGarbage = False
            
            cPiece = random.choice(self.pieceBag)
            self.pPiece = Piece(cPiece)
            self.pieceBag.remove(cPiece)

            self.heldPiece = None
            
            for i in range(0, 3):
                cPiece = random.choice(self.pieceBag)
                self.nextQueue[i] = copy.deepcopy(cPiece)
                self.nextPieces.append(Piece(cPiece))
                self.pieceBag.remove(cPiece)
            
        elif self.gameState == 1:
            self.displayLevel = self.dataManager.levelNames[self.level]
            self.dropDelay = self.dataManager.levelDropSpeed[self.level][self.difficulty]
            self.bgColour = self.dataManager.levelBackground[self.level]
            if self.bgColour == (0, 0, 0):
                self.isSpace = True
            else:
                self.isSpace = False
            self.boss = copy.deepcopy(self.dataManager.bossFights[self.cBoss][self.difficulty])
            self.cDropDelay = 100
            self.hasGarbage = False
            
            cPiece = random.choice(self.pieceBag)
            self.pPiece = Piece(cPiece)
            self.pieceBag.remove(cPiece)

            self.heldPiece = None
            
            for i in range(0, 3):
                cPiece = random.choice(self.pieceBag)
                self.nextQueue[i] = copy.deepcopy(cPiece)
                self.nextPieces.append(Piece(cPiece))
                self.pieceBag.remove(cPiece)

            self.geminiAttackDelay = 400

    def newPiece(self):
        self.held = False
        self.prevTLoc = [-999, -999]

        linesCleared = 0
        for i in range(0, len(self.pBoard.board)):
            lineFull = True
            for j in range(0, len(self.pBoard.board[i])):
                if self.pBoard.board[i][j] == " ":
                    lineFull = False
                    break
            if lineFull:
                linesCleared += 1
                for j in range(0, len(self.pBoard.board[i])):
                    self.pBoard.board[i][j] = " "
                currentIndex = i - 1
                while currentIndex > 0:
                    for j in range(0, len(self.pBoard.board[i])):
                        self.pBoard.board[currentIndex + 1][j] = self.pBoard.board[currentIndex][j]
                    currentIndex -= 1
                for j in range(0, len(self.pBoard.board[0])):
                    self.pBoard.board[0][j] = " "

        lineScores = [0, 500, 2500, 4500, 10000, 30000]
        damageVals = [0, 1, 3, 5, 8, 15]
        chargeVals = [0, 10, 30, 40, 60]
        self.linesLeft -= linesCleared
        if self.linesLeft <= 0:
            self.linesLeft = 0

        if linesCleared > 0:
            self.combo += 1
        else:
            self.combo = 0

        if self.pPiece.storedShape == 0 and self.tRotates > 0 and linesCleared > 0:
            if self.tRotates == 1:
                self.pScore += 10000
                self.boss.health -= 5
                self.boss.atkCharge -= int(self.boss.atkSpeeds[self.boss.phase] * ((20 / 100) + (self.combo / 20)))
            elif self.tRotates == 2:
                self.pScore += 30000
                self.boss.health -= 8
                self.boss.atkCharge -= int(self.boss.atkSpeeds[self.boss.phase] * ((40 / 100) + (self.combo / 20)))
            else:
                self.pScore += 50000
                self.boss.health -= 10
                self.boss.atkCharge -= int(self.boss.atkSpeeds[self.boss.phase] * ((60 / 100) + (self.combo / 20)))

        self.pScore += lineScores[linesCleared] + self.combo * 1000
        self.boss.health -= (damageVals[linesCleared] + self.combo)
        self.boss.atkCharge -= int(self.boss.atkSpeeds[self.boss.phase] * ((chargeVals[linesCleared] / 100) + (self.combo / 20)))

        if linesCleared == 4:
            self.pScore += self.tetrisCombo * 5000
            self.boss.health -= self.tetrisCombo * 4
            self.boss.atkCharge -= int(self.boss.atkSpeeds[self.boss.phase] * (self.tetrisCombo / 10))
            self.tetrisCombo += 1
        elif linesCleared > 0:
            self.tetrisCombo = 0
        
        if linesCleared > 0:
            self.recDelay = 150
            if linesCleared == 1:
                self.recClear = "SINGLE"
            elif linesCleared == 2:
                self.recClear = "DOUBLE"
            elif linesCleared == 3:
                self.recClear = "TRIPLE"
            elif linesCleared == 4:
                self.recClear = "TETRIS"

        if self.pPiece.storedShape == 0 and self.tRotates > 0:
            if self.tRotates == 1:
                self.recClear = "T-SPIN"
            elif self.tRotates == 2:
                self.recClear = "DOUBLE T-SPIN"
            else:
                self.recClear = "TRIPLE T-SPIN"

        # Check for all-clears
        allClear = True
        for i in range(0, 24):
            for j in range(0, 10):
                if self.pBoard.board[i][j] != "" and self.pBoard.board[i][j] != " ":
                    allClear = False
                    break
        
        if allClear and not self.pressedHold:
            self.recClear = "! ALL CLEAR !"
            self.boss.health -= 50
            self.boss.atkCharge = 0
            self.pScore += 100000
        
        self.pPiece = Piece(self.nextQueue[0])
        if self.gameState == 1 and self.boss.bossId == 5 and self.boss.phase >= 1:
            self.pPiece.colour = random.choice(["P", "Y", "O", "B", "G", "R", "L", "C"])
        
        self.nextQueue[0] = self.nextQueue[1]
        self.nextQueue[1] = self.nextQueue[2]

        if self.gameState == 1 and self.boss.bossId == 5 and self.boss.phase >= 1:
            self.nextQueue[2] = random.choice(range(0, 7))
        else:
            cPiece = random.choice(self.pieceBag)
            self.nextQueue[2] = copy.deepcopy(cPiece)
            self.pieceBag.remove(cPiece)

        self.nextPieces = []
        for i in self.nextQueue:
            self.nextPieces.append(Piece(i))

        if len(self.pieceBag) <= 0:
            for i in range(0, 7):
                self.pieceBag.append(i)
        
        self.recalculateGhost = True
        
        if self.boss.health <= 0:
            self.boss.health = 0
        if self.boss.atkCharge <= 0:
            self.boss.atkCharge = 0

        self.pressedHold = False
        self.tRotates = 0
    
    def logic(self):
        if self.gameState == 0:
            if self.gameOverDelay <= 0 and self.victoryDelay <= 0:  # Regular game
                # Stars
                if self.isSpace:
                    self.nStarDelay -= 1
                    if self.nStarDelay <= 0:
                        self.stars.append([random.choice(range(0, 1601)), -20, random.choice(range(-5, 5)), random.choice(range(10, 20))])
                        self.nStarDelay = 2
                        
                    for star in range(0, len(self.stars)):
                        self.stars[star][0] += self.stars[star][2]
                        self.stars[star][1] += self.stars[star][3]

                    for star in self.stars:
                        if star[1] > 1000:
                            self.stars.remove(star)
                
                if self.linesLeft <= 0:
                    self.victoryDelay = 200
                
                # Player piece
                self.nextDrop -= 1
                if self.nextDrop <= 0:
                    self.nextDrop = self.dropDelay
                    self.pPiece.yLoc += 1
                    result = self.pPiece.isColliding(self.pBoard.board)
                    if result:
                        self.pPiece.yLoc -= 1
                        if self.slideFreeze <= 0:
                            for i in range(0, len(self.pPiece.shape)):
                                for j in range(0, len(self.pPiece.shape[i])):
                                    if self.pPiece.shape[i][j] == "P":
                                        try:
                                            location = [self.pPiece.xLoc - self.pPiece.centre[0] + j, self.pPiece.yLoc - self.pPiece.centre[1] + i]
                                            self.pBoard.board[location[1]][location[0]] = self.pPiece.colour
                                        except IndexError:
                                            pass
                            self.newPiece()
                            if self.pPiece.isColliding(self.pBoard.board):
                                self.gameOverDelay = 200
                            self.slideFreeze = self.staticSlideFreeze
                        else:
                            self.nextDrop = 0
                            self.slideFreeze -= 1
                    else:
                        self.slideFreeze = self.staticSlideFreeze
                        self.tRotates = 0

                # Ghost piece
                if self.recalculateGhost:
                    self.ghostPiece = Piece(self.pPiece.storedShape)
                    self.ghostPiece.xLoc = self.pPiece.xLoc
                    self.ghostPiece.yLoc = copy.deepcopy(self.pPiece.yLoc)
                    self.ghostPiece.shape = self.pPiece.shape
                    while not self.ghostPiece.isColliding(self.pBoard.board):
                        self.ghostPiece.yLoc += 1
                    self.ghostPiece.yLoc -= 1
                    self.recalculateGhost = False

                # Garbage Pieces
                self.nextGarbage -= 1
                if self.nextGarbage <= 0 and self.hasGarbage:
                    self.nextGarbage = self.garbageDelay
                    emptyBottomLayer = True
                    for i in range(0, 10):
                        if self.pBoard.board[23][i] != "" and self.pBoard.board[23][i] != " ":
                            emptyBottomLayer = False
                            break
                    if not emptyBottomLayer:
                        self.pPiece.yLoc -= 1
                        for i in range(1, 24):
                            for j in range(0, 10):
                                self.pBoard.board[i-1][j] = copy.deepcopy(self.pBoard.board[i][j])
                        hasHole = False
                        for i in range(0, 10):
                            self.pBoard.board[23][i] = copy.deepcopy(self.pBoard.board[22][i])
                            if self.pBoard.board[23][i] != "" and self.pBoard.board[23][i] != " ":
                                self.pBoard.board[23][i] = "C"
                            elif not hasHole:
                                hasHole = True
                            else:
                                self.pBoard.board[23][i] = "C"
                        self.recalculateGhost = True

                # Keyboard Input
                keys = pygame.key.get_pressed()
                if (keys[pygame.K_UP] or keys[pygame.K_x]) and not self.pressedRotate:
                    self.recalculateGhost = True
                    self.pressedRotate = True
                    prevRot = self.pPiece.cRot
                    self.pPiece.cRot += 1
                    if self.pPiece.cRot > len(self.pPiece.rotations) - 1:
                        self.pPiece.cRot = 0

                    self.pPiece.shape = self.pPiece.rotations[self.pPiece.cRot]
                    result = self.pPiece.isColliding(self.pBoard.board, True, prevRot)
                    if result:
                        self.pPiece.cRot -= 1
                        if self.pPiece.cRot < 0:
                            self.pPiece.cRot = len(self.pPiece.rotations) - 1
                        self.pPiece.shape = self.pPiece.rotations[self.pPiece.cRot]
                    else:
                        self.slideFreeze = self.staticSlideFreeze
                        if self.prevTLoc != [self.pPiece.xLoc, self.pPiece.yLoc]:
                            self.prevTLoc = [self.pPiece.xLoc, self.pPiece.yLoc]

                            surroundingBlocks = 0
                            blockOffsets = [[1, 1], [-1, 1], [1, -1], [-1, -1]]
                            for offset in blockOffsets:
                                try:
                                    if self.pBoard.board[self.pPiece.yLoc + offset[1]][self.pPiece.xLoc + offset[0]] != "" and self.pBoard.board[self.pPiece.yLoc + offset[1]][self.pPiece.xLoc + offset[0]] != " ":
                                        surroundingBlocks += 1
                                except IndexError:
                                    surroundingBlocks += 1

                            if surroundingBlocks >= 3:
                                self.tRotates += 1
                elif (keys[pygame.K_z]) and not self.pressedRotate:
                    self.recalculateGhost = True
                    self.pressedRotate = True
                    prevRot = self.pPiece.cRot
                    self.pPiece.cRot -= 1
                    if self.pPiece.cRot < 0:
                        self.pPiece.cRot = len(self.pPiece.rotations) - 1

                    self.pPiece.shape = self.pPiece.rotations[self.pPiece.cRot]
                    result = self.pPiece.isColliding(self.pBoard.board, True, prevRot)
                    if result:
                        self.pPiece.cRot += 1
                        if self.pPiece.cRot >= len(self.pPiece.rotations):
                            self.pPiece.cRot = 0
                        self.pPiece.shape = self.pPiece.rotations[self.pPiece.cRot]
                    else:
                        self.slideFreeze = self.staticSlideFreeze
                        if self.prevTLoc != [self.pPiece.xLoc, self.pPiece.yLoc]:
                            self.prevTLoc = [self.pPiece.xLoc, self.pPiece.yLoc]

                            surroundingBlocks = 0
                            blockOffsets = [[1, 1], [-1, 1], [1, -1], [-1, -1]]
                            for offset in blockOffsets:
                                try:
                                    if self.pBoard.board[self.pPiece.yLoc + offset[1]][self.pPiece.xLoc + offset[0]] != "" and self.pBoard.board[self.pPiece.yLoc + offset[1]][self.pPiece.xLoc + offset[0]] != " ":
                                        surroundingBlocks += 1
                                except IndexError:
                                    surroundingBlocks += 1

                            if surroundingBlocks >= 3:
                                self.tRotates += 1
                elif not (keys[pygame.K_UP] or keys[pygame.K_x] or keys[pygame.K_z]):
                    self.pressedRotate = False
                
                if keys[pygame.K_c] and not self.held:
                    self.tRotates = 0
                    if self.heldPiece == None:
                        self.pressedHold = True
                        self.heldPiece = Piece(self.pPiece.storedShape)
                        self.newPiece()
                    else:
                        temp = self.heldPiece.storedShape
                        self.heldPiece = Piece(self.pPiece.storedShape)
                        self.pPiece = Piece(temp)
                    self.held = True
                    self.recalculateGhost = True

                if keys[pygame.K_DOWN] and self.cDropDelay <= 0:
                    self.tRotates = 0
                    self.pPiece.yLoc += 1
                    if self.pPiece.isColliding(self.pBoard.board):
                        self.pPiece.yLoc -= 1
                    self.cDropDelay = 2

                if keys[pygame.K_SPACE] and not self.hardDropped:
                    self.hardDropped = True
                    self.tRotates = 0
                    while not self.pPiece.isColliding(self.pBoard.board):
                        self.pPiece.yLoc += 1
                        self.pScore += 10
                    self.pPiece.yLoc -= 1
                    for i in range(0, len(self.pPiece.shape)):
                        for j in range(0, len(self.pPiece.shape[i])):
                            if self.pPiece.shape[i][j] == "P":
                                try:
                                    location = [self.pPiece.xLoc - self.pPiece.centre[0] + j, self.pPiece.yLoc - self.pPiece.centre[1] + i]
                                    self.pBoard.board[location[1]][location[0]] = self.pPiece.colour
                                except IndexError:
                                    pass
                    self.newPiece()
                    if self.pPiece.isColliding(self.pBoard.board):
                        self.gameOverDelay = 200
                
                elif not keys[pygame.K_SPACE]:
                    self.hardDropped = False
                
                if keys[pygame.K_LEFT] and self.cMDelay <= 0:
                    self.tRotates = 0
                    self.recalculateGhost = True
                    self.pPiece.xLoc -= 1
                    if self.pPiece.isColliding(self.pBoard.board):
                        self.pPiece.xLoc += 1
                    else:
                        self.slideFreeze = self.staticSlideFreeze
                    
                    if self.isDASing:
                        self.cMDelay = self.DASDelay
                    else:
                        self.isDASing = True
                        self.cMDelay = self.staticDASDelay
                elif keys[pygame.K_RIGHT] and self.cMDelay <= 0:
                    self.recalculateGhost = True
                    self.pPiece.xLoc += 1
                    if self.pPiece.isColliding(self.pBoard.board):
                        self.pPiece.xLoc -= 1
                    else:
                        self.slideFreeze = self.staticSlideFreeze

                    if self.isDASing:
                        self.cMDelay = self.DASDelay
                    else:
                        self.isDASing = True
                        self.cMDelay = self.staticDASDelay
                elif not(keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):
                    self.isDASing = False
                    self.cMDelay = 0

                self.cMDelay -= 1
                self.cDropDelay -= 1

                self.recDelay -= 1
                if self.recDelay <= 0:
                    self.recClear = ""
            elif self.victoryDelay > 0: # Victory
                self.victoryDelay -= 1
                if self.victoryDelay <= 0:
                    self.gameState = 3
                
            else:  # Game Over
                self.gameOverDelay -= 1
                if self.gameOverDelay <= 0:
                    self.gameState = 2
            
        elif self.gameState == 1: # Boss level
            if self.gameOverDelay <= 0 and self.victoryDelay <= 0:
                # Stars
                if self.isSpace:
                    self.nStarDelay -= 1
                    if self.nStarDelay <= 0:
                        self.stars.append([random.choice(range(0, 1601)), -20, random.choice(range(-5, 5)), random.choice(range(10, 20))])
                        self.nStarDelay = 2
                        
                    for star in range(0, len(self.stars)):
                        self.stars[star][0] += self.stars[star][2]
                        self.stars[star][1] += self.stars[star][3]

                    for star in self.stars:
                        if star[1] > 1000:
                            self.stars.remove(star)

                # Player piece
                self.nextDrop -= 1
                if self.nextDrop <= 0:
                    self.nextDrop = self.dropDelay
                    self.pPiece.yLoc += 1
                    result = self.pPiece.isColliding(self.pBoard.board)
                    if result:
                        self.pPiece.yLoc -= 1
                        if self.slideFreeze <= 0:
                            for i in range(0, len(self.pPiece.shape)):
                                for j in range(0, len(self.pPiece.shape[i])):
                                    if self.pPiece.shape[i][j] == "P":
                                        try:
                                            location = [self.pPiece.xLoc - self.pPiece.centre[0] + j, self.pPiece.yLoc - self.pPiece.centre[1] + i]
                                            self.pBoard.board[location[1]][location[0]] = self.pPiece.colour
                                        except IndexError:
                                            pass
                            self.newPiece()
                            if self.pPiece.isColliding(self.pBoard.board):
                                self.gameOverDelay = 200
                            self.slideFreeze = self.staticSlideFreeze
                        else:
                            self.nextDrop = 0
                            self.slideFreeze -= 1
                    else:
                        self.slideFreeze = self.staticSlideFreeze
                        self.tRotates = 0

                # Boss
                if self.bossStun <= 0:
                    self.boss.atkCharge += 1
                    if self.boss.atkCharge >= self.boss.atkSpeeds[self.boss.phase]:
                        self.boss.atkCharge = 0
                        linesSent = 0
                        print("Lines - Part 1")
                        while linesSent < self.boss.atkPowers[self.boss.phase]:
                            linesSent += 1
                            if random.choice(range(1, 101)) <= self.boss.atkRandomness[self.boss.phase]:
                                for i in range(0, 10):
                                    if self.pBoard.board[23][i] != "" and self.pBoard.board[23][i] != " ":
                                        emptyBottomLayer = False
                                        break
                                if not emptyBottomLayer:
                                    for i in range(1, 24):
                                        for j in range(0, 10):
                                            self.pBoard.board[i-1][j] = copy.deepcopy(self.pBoard.board[i][j])

                                for i in range(0, 10):
                                    self.pBoard.board[23][i] = "C"
                                self.pBoard.board[23][random.choice(range(0, 10))] = " "
                            else:
                                emptyBottomLayer = True
                                for i in range(0, 10):
                                    if self.pBoard.board[23][i] != "" and self.pBoard.board[23][i] != " ":
                                        emptyBottomLayer = False
                                        break
                                if not emptyBottomLayer:
                                    for i in range(1, 24):
                                        for j in range(0, 10):
                                            self.pBoard.board[i-1][j] = copy.deepcopy(self.pBoard.board[i][j])
                                    hasHole = False

                                    for i in range(0, 10):
                                        self.pBoard.board[23][i] = copy.deepcopy(self.pBoard.board[22][i])
                                        if self.pBoard.board[23][i] != "" and self.pBoard.board[23][i] != " ":
                                            self.pBoard.board[23][i] = "C"
                                        elif not hasHole:
                                            hasHole = True
                                        else:
                                            self.pBoard.board[23][i] = "C"

                            self.pPiece.yLoc -= 1
                            breaker = 20
                            while self.pPiece.isColliding(self.pBoard.board):
                                self.pPiece.yLoc += 1
                                breaker -= 1
                                if breaker <= 0:
                                    break
                            
                            self.recalculateGhost = True
                
                # Gemini - Block Break
                if ((self.boss.phase >= 1 and self.boss.bossId == 1) or (self.boss.phase == 1 and self.boss.bossId == 4)) and self.boss.health > 0:
                    self.geminiAttackDelay -= 1
                    if self.geminiAttackDelay <= 0:
                        if self.geminiIsAttacking:
                            self.geminiIsAttacking = False
                            self.geminiAttackDelay = 1100 - (self.boss.phase * 200)
                            
                            for i in range(0, 24):
                                targets = []
                                doDestroy = False
                                parity = 0
                                
                                for j in range(0, 10):
                                    if self.pBoard.board[i][j] == "C":
                                        targets.append([i, j])

                                    if self.pBoard.board[i][j] != "C":
                                        if (self.pBoard.board[i][j] != "" and self.pBoard.board[i][j] != " ") or parity >= 1:
                                            doDestroy = True
                                        else:
                                            parity += 1

                                if doDestroy:
                                    for target in targets:
                                        self.pBoard.board[target[0]][target[1]] = " "
                        else:
                            self.geminiIsAttacking = True
                            self.geminiAttackDelay = 400
                            
                            availableSpots = []
                            for i in range(0, 24):
                                for j in range(0, 10):
                                    if self.pBoard.board[i][j] != "" and self.pBoard.board[i][j] != " " and self.pBoard.board[i][j] != "C":
                                        availableSpots.append([i, j])

                            targets = []
                            if len(availableSpots) <= (3 * self.boss.phase):
                                targets = availableSpots
                            else:
                                for i in range(0, 3 * self.boss.phase):
                                    newTarget = random.choice(availableSpots)
                                    targets.append(copy.deepcopy(newTarget))
                                    availableSpots.remove(newTarget)

                            for i in targets:
                                self.pBoard.board[i[0]][i[1]] = "C"

                # Orion - Double Speed
                if self.boss.phase >= 2 and (self.boss.bossId == 3 or self.boss.bossId == 4) and not self.orionIsAttacking and self.boss.health > 0:
                    self.orionIsAttacking = True
                    self.dropDelay /= 2
                elif ((self.boss.phase == 1 and self.boss.bossId == 3) or (self.boss.phase == 1 and self.boss.bossId == 4)) and self.boss.health > 0:
                    self.orionAttackDelay -= 1
                    if self.orionAttackDelay <= 0:
                        if self.orionIsAttacking:
                            self.dropDelay = self.heldDropSpeed
                            self.orionIsAttacking = False
                            self.orionAttackDelay = 1000
                        else:
                            self.orionIsAttacking = True
                            self.heldDropSpeed = copy.deepcopy(self.dropDelay)
                            self.dropDelay /= 2
                            if self.cDropDelay > self.dropDelay:
                                self.cDropDelay = self.dropDelay
                            self.orionAttackDelay = 200

                # Boss Death
                if self.boss.health <= 0 and self.bossStun <= 0:
                    self.bossStun = 300
                    self.boss.atkCharge = 0
                elif self.boss.health <= 0 and self.bossStun > 0:
                    self.bossStun -= 1
                    if self.boss.phase >= 2:
                        self.victoryDelay = 300
                    if self.bossStun <= 0:
                        self.boss.phase += 1
                        self.boss.health = self.boss.healthVals[self.boss.phase]
                
                # Ghost piece
                if self.recalculateGhost:
                    self.ghostPiece = Piece(self.pPiece.storedShape)
                    self.ghostPiece.xLoc = self.pPiece.xLoc
                    self.ghostPiece.yLoc = copy.deepcopy(self.pPiece.yLoc)
                    self.ghostPiece.shape = self.pPiece.shape
                    while not self.ghostPiece.isColliding(self.pBoard.board):
                        self.ghostPiece.yLoc += 1
                    self.ghostPiece.yLoc -= 1
                    self.recalculateGhost = False

                # Keyboard Input
                keys = pygame.key.get_pressed()
                if (keys[pygame.K_UP] or keys[pygame.K_x]) and not self.pressedRotate:
                    self.recalculateGhost = True
                    self.pressedRotate = True
                    prevRot = self.pPiece.cRot
                    self.pPiece.cRot += 1
                    if self.pPiece.cRot > len(self.pPiece.rotations) - 1:
                        self.pPiece.cRot = 0

                    self.pPiece.shape = self.pPiece.rotations[self.pPiece.cRot]
                    result = self.pPiece.isColliding(self.pBoard.board, True, prevRot)
                    if result:
                        self.pPiece.cRot -= 1
                        if self.pPiece.cRot < 0:
                            self.pPiece.cRot = len(self.pPiece.rotations) - 1
                        self.pPiece.shape = self.pPiece.rotations[self.pPiece.cRot]
                    else:
                        if self.prevTLoc != [self.pPiece.xLoc, self.pPiece.yLoc]:
                            self.prevTLoc = [self.pPiece.xLoc, self.pPiece.yLoc]

                            surroundingBlocks = 0
                            blockOffsets = [[1, 1], [-1, 1], [1, -1], [-1, -1]]
                            for offset in blockOffsets:
                                try:
                                    if self.pBoard.board[self.pPiece.yLoc + offset[1]][self.pPiece.xLoc + offset[0]] != "" and self.pBoard.board[self.pPiece.yLoc + offset[1]][self.pPiece.xLoc + offset[0]] != " ":
                                        surroundingBlocks += 1
                                except IndexError:
                                    surroundingBlocks += 1

                            if surroundingBlocks >= 3:
                                self.tRotates += 1
                        self.slideFreeze = self.staticSlideFreeze
                elif (keys[pygame.K_z]) and not self.pressedRotate:
                    self.recalculateGhost = True
                    self.pressedRotate = True
                    prevRot = self.pPiece.cRot
                    self.pPiece.cRot -= 1
                    if self.pPiece.cRot < 0:
                        self.pPiece.cRot = len(self.pPiece.rotations) - 1

                    self.pPiece.shape = self.pPiece.rotations[self.pPiece.cRot]
                    result = self.pPiece.isColliding(self.pBoard.board, True, prevRot)
                    if result:
                        self.pPiece.cRot += 1
                        if self.pPiece.cRot >= len(self.pPiece.rotations):
                            self.pPiece.cRot = 0
                        self.pPiece.shape = self.pPiece.rotations[self.pPiece.cRot]
                    else:
                        if self.prevTLoc != [self.pPiece.xLoc, self.pPiece.yLoc]:
                            self.prevTLoc = [self.pPiece.xLoc, self.pPiece.yLoc]

                            surroundingBlocks = 0
                            blockOffsets = [[1, 1], [-1, 1], [1, -1], [-1, -1]]
                            for offset in blockOffsets:
                                try:
                                    if self.pBoard.board[self.pPiece.yLoc + offset[1]][self.pPiece.xLoc + offset[0]] != "" and self.pBoard.board[self.pPiece.yLoc + offset[1]][self.pPiece.xLoc + offset[0]] != " ":
                                        surroundingBlocks += 1
                                except IndexError:
                                    surroundingBlocks += 1

                            if surroundingBlocks >= 3:
                                self.tRotates += 1
                        self.slideFreeze = self.staticSlideFreeze
                elif not (keys[pygame.K_UP] or keys[pygame.K_x] or keys[pygame.K_z]):
                    self.pressedRotate = False
                
                if keys[pygame.K_c] and not self.held:
                    self.tRotates = 0
                    if self.heldPiece == None:
                        self.pressedHold = True
                        self.heldPiece = Piece(self.pPiece.storedShape)
                        self.newPiece()
                    else:
                        temp = self.heldPiece.storedShape
                        self.heldPiece = Piece(self.pPiece.storedShape)
                        self.pPiece = Piece(temp)
                    self.held = True
                    self.recalculateGhost = True

                if keys[pygame.K_DOWN] and self.cDropDelay <= 0:
                    self.tRotates = 0
                    self.pPiece.yLoc += 1
                    if self.pPiece.isColliding(self.pBoard.board):
                        self.pPiece.yLoc -= 1
                    self.cDropDelay = 2

                if keys[pygame.K_SPACE] and not self.hardDropped:
                    self.tRotates = 0
                    self.hardDropped = True
                    while not self.pPiece.isColliding(self.pBoard.board):
                        self.pPiece.yLoc += 1
                        self.pScore += 10
                    self.pPiece.yLoc -= 1
                    for i in range(0, len(self.pPiece.shape)):
                        for j in range(0, len(self.pPiece.shape[i])):
                            if self.pPiece.shape[i][j] == "P":
                                try:
                                    location = [self.pPiece.xLoc - self.pPiece.centre[0] + j, self.pPiece.yLoc - self.pPiece.centre[1] + i]
                                    self.pBoard.board[location[1]][location[0]] = self.pPiece.colour
                                except IndexError:
                                    pass
                    self.newPiece()
                    if self.pPiece.isColliding(self.pBoard.board):
                        self.gameOverDelay = 200
                
                elif not keys[pygame.K_SPACE]:
                    self.hardDropped = False
                
                if keys[pygame.K_LEFT] and self.cMDelay <= 0:
                    self.tRotates = 0
                    self.recalculateGhost = True
                    self.pPiece.xLoc -= 1
                    if self.pPiece.isColliding(self.pBoard.board):
                        self.pPiece.xLoc += 1
                    else:
                        self.slideFreeze = self.staticSlideFreeze
                    
                    if self.isDASing:
                        self.cMDelay = self.DASDelay
                    else:
                        self.isDASing = True
                        self.cMDelay = self.staticDASDelay
                elif keys[pygame.K_RIGHT] and self.cMDelay <= 0:
                    self.tRotates = 0
                    self.recalculateGhost = True
                    self.pPiece.xLoc += 1
                    if self.pPiece.isColliding(self.pBoard.board):
                        self.pPiece.xLoc -= 1
                    else:
                        self.slideFreeze = self.staticSlideFreeze

                    if self.isDASing:
                        self.cMDelay = self.DASDelay
                    else:
                        self.isDASing = True
                        self.cMDelay = self.staticDASDelay
                elif not(keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):
                    self.isDASing = False
                    self.cMDelay = 0

                self.cMDelay -= 1
                self.cDropDelay -= 1

                self.recDelay -= 1
                if self.recDelay <= 0:
                    self.recClear = ""
            elif self.victoryDelay > 0: # Victory
                self.victoryDelay -= 1
                if self.victoryDelay <= 0:
                    self.gameState = 3
                
            else:  # Game Over
                self.gameOverDelay -= 1
                if self.gameOverDelay <= 0:
                    self.gameState = 2
            
        elif self.gameState == 2:  # Game over screen
            if pygame.mouse.get_pressed()[0]:
                x, y = pygame.mouse.get_pos()
                if 740 <= x <= 854 and 803 <= y <= 837:
                    self.gameState = 0
                    self.transition()
                elif 711 <= x <= 885 and 853 <= y <= 887:
                    self.gameState = 4
                    self.transition()
        
        elif self.gameState == 3:  # Victory screen
            if not self.didSave:
                self.didSave = True
                if self.pScore > self.highScores[self.difficulty][self.level]:
                    self.highScores[self.difficulty][self.level] = self.pScore
                    files = ["data/1S.txt", "data/2S.txt", "data/3S.txt", "data/4S.txt"]
                    f = open(files[self.difficulty], "w")
                    for score in self.highScores[self.difficulty]:
                        f.write(str(score) + "\n")
                    f.close()

                    self.nextLevel[self.difficulty] = max(self.nextLevel[self.difficulty], (self.level + 1))
                    f = open("data/progression.txt", "w")
                    for score in self.nextLevel:
                        f.write(str(score) + "\n")
                    f.close()                    
            
            if pygame.mouse.get_pressed()[0]:
                x, y = pygame.mouse.get_pos()
                print(x, y)

                storyLevels = [3, 7, 11, 15, 17, 18]
                if self.level in storyLevels and ((717 <= x <= 876 and 803 <= y <= 837) or (711 <= x <= 885 and 853 <= y <= 887)):
                    storyToCutscene = [[3, 1], [7, 2], [11, 3], [15, 4], [17, 5 if self.difficulty < 3 else 6], [18, 7]]
                    for cPart in storyToCutscene:
                        if self.level == cPart[0]:
                            self.gameState = 7
                            self.storyPart = cPart[1]
                            break
                
                elif 717 <= x <= 876 and 803 <= y <= 837:
                    self.gameState = 0
                    self.level += 1
                    self.transition()
                elif 711 <= x <= 885 and 853 <= y <= 887:
                    self.gameState = 4
                    self.transition()

        elif self.gameState == 4:  # Main Menu
            if pygame.mouse.get_pressed()[0]:
                x, y = pygame.mouse.get_pos()
                if 750 <= x <= 846 and 586 <= y <= 626:  # Play
                    if self.cutscenes[0] == 0:
                        self.cutscenes[0] = 1

                        f = open("data/cutscenes.txt", "w")
                        for cutscene in self.cutscenes:
                            f.write(str(cutscene) + "\n")
                        f.close() 
                        
                        self.gameState = 7
                        self.storyPart = 0
                        self.currentChapter = 0
                    else:
                        self.gameState = 6
                        self.currentChapter = 0
                elif 402 <= x <= 500 and 486 <= y <= 519:  # Help
                    self.gameState = 5
                elif 1101 <= x <= 1195 and 487 <= y <= 516:  # Quit
                    pygame.display.quit()
                    pygame.quit()
                    sys.exit()
                else:  # Difficulty Select
                    difficultyButtons = [[498, 598, 783, 820], [484, 613, 855, 886], [994, 1102, 785, 820], [948, 1144, 853, 886]]
                    for button in difficultyButtons:
                        if button[0] <= x <= button[1] and button[2] <= y <= button[3]:
                            if difficultyButtons.index(button) < 3:
                                self.difficulty = difficultyButtons.index(button)
                            elif self.nextLevel[2] >= 18:
                                self.difficulty =3

        elif self.gameState == 5:  # Help
            if pygame.mouse.get_pressed()[0]:
                x, y = pygame.mouse.get_pos()
                if 744 <= x <= 851 and 885 <= y <= 917:
                    self.gameState = 4

        elif self.gameState == 6:  # Play
            if pygame.mouse.get_pressed()[0] and self.clickedMosue == False:
                self.clickedMosue = True
                x, y = pygame.mouse.get_pos()
                if 17 <= x <= 79 and 914 <= y <= 940:
                    self.currentChapter = max(0, self.currentChapter - 1)
                elif 1521 <= x <= 1581 and 910 <= y <= 941 and ((self.difficulty == 3 and self.currentChapter < 5) or (self.difficulty < 3 and self.currentChapter < 4)) and (((self.nextLevel[self.difficulty] >= (self.currentChapter * 4) + 4) and self.currentChapter < 4) or ((self.nextLevel[self.difficulty] >= 18 and self.currentChapter == 4))):
                    self.currentChapter = min(5, self.currentChapter + 1)
                elif 744 <= x <= 848 and 886 <= y <= 917:
                    self.gameState = 4
                else:
                    if self.currentChapter < 4:
                        levels = [[711, 877, 533, 565], [414, 580, 886, 916], [1012, 1178, 886, 916], [745, 852, 713, 741]]
                        for button in levels:
                            if button[0] <= x <= button[1] and button[2] <= y <= button[3] and self.nextLevel[self.difficulty] >= (self.currentChapter * 4) + levels.index(button):
                                self.gameState = 0
                                self.level = levels.index(button) + (4 * self.currentChapter)
                                self.cBoss = self.currentChapter
                                self.transition()
                                break
                            
                    elif self.currentChapter == 4:
                        levels = [[712, 878, 533, 570, 16], [709, 883, 709, 739, 17]]
                        for button in levels:
                            if button[0] <= x <= button[1] and button[2] <= y <= button[3] and self.nextLevel[self.difficulty] >= 16 + levels.index(button):
                                self.gameState = 0
                                self.level = button[4]
                                self.cBoss = 4
                                self.transition()
                                break
                    else:
                        if 754 <= x <= 841 and 709 <= y <= 742 and self.nextLevel[self.difficulty] >= 18:
                            self.gameState = 0
                            self.level = 18
                            self.cBoss = 5
                            self.transition()

            elif not pygame.mouse.get_pressed()[0]:
                self.clickedMosue = False

        elif self.gameState == 7:  # Story
            if pygame.mouse.get_pressed()[0]:
                x, y = pygame.mouse.get_pos()
                if 744 <= x <= 851 and 905 <= y <= 937:
                    self.gameState = 4 if (self.storyPart == 5 or self.storyPart == 7) else 6
                    self.clickedMosue = True

    def draw(self):
        global screen
        
        if self.gameState == 0:  # Gameplay: Single Player
            screen.fill(self.bgColour)
            if self.gameOverDelay > 0:
                screen.fill((100, 0, 0))

            if self.isSpace:
                for star in self.stars:
                    pygame.draw.circle(screen, (255, 255, 255), (star[0], star[1]), 3)

            # Drawing the board
            pygame.draw.rect(screen, (20, 20, 20), pygame.Rect(625, 55, 350, 840))
            for i in range(0, len(self.pBoard.board)):
                for j in range(0, len(self.pBoard.board[i])):
                    if self.pBoard.board[i][j] != "" and self.pBoard.board[i][j] != " ":
                        rect = pygame.Rect((625 + j * 35), (55 + i * 35), 35, 35)
                        image = pygame.Surface(rect.size).convert()
                        image.blit(self.pieceSheet, (0, 0), self.getPieceSprite(self.pBoard.board[i][j]))
                        screen.blit(image, rect)
             # Draw ghost piece
            for i in range(0, len(self.ghostPiece.shape)):
                for j in range(0, len(self.ghostPiece.shape[i])):
                    if self.ghostPiece.shape[i][j] != "" and 0 <= self.ghostPiece.yLoc + i < 25:
                        pygame.draw.rect(screen, (100, 100, 100), pygame.Rect((625 + 35 * (j + self.ghostPiece.xLoc - self.ghostPiece.centre[0])), (55 + 35 * (i + self.ghostPiece.yLoc - self.ghostPiece.centre[1])), 35, 35))
            
            # Draw player piece
            for i in range(0, len(self.pPiece.shape)):
                for j in range(0, len(self.pPiece.shape[i])):
                    if self.pPiece.shape[i][j] != "" and 0 <= self.pPiece.yLoc + i < 25:
                        rect = pygame.Rect((625 + 35 * (j + self.pPiece.xLoc - self.pPiece.centre[0])), (55 + 35 * (i + self.pPiece.yLoc - self.pPiece.centre[1])), 35, 35)
                        image = pygame.Surface(rect.size).convert()
                        image.blit(self.pieceSheet, (0, 0), self.getPieceSprite(self.pPiece.colour))
                        screen.blit(image, rect)
            
            # Next Queue
            self.renderText("NEXT", self.gameplayFont, 1051, 100)
            for i in range(0, 3):
                pygame.draw.rect(screen, (20, 20, 20), pygame.Rect(1000, 130 + (i * 160), 150, 150))
                wPiece = self.nextPieces[i]
                for j in range(0, len(wPiece.shape)):
                    for k in range(0, len(wPiece.shape[j])):
                        if wPiece.shape[j][k] != "":
                            rect = pygame.Rect((self.nextPiecesDisplayAdjust[wPiece.storedShape][0] + 35 * (k - wPiece.centre[0])), (self.nextPiecesDisplayAdjust[wPiece.storedShape][1] + 35 * (j + wPiece.centre[1]) + 160 * i), 35, 35)
                            image = pygame.Surface(rect.size).convert()
                            image.blit(self.pieceSheet, (0, 0), self.getPieceSprite(wPiece.colour))
                            screen.blit(image, rect)
            
            # Held Piece
            self.renderText("HOLD", self.gameplayFont, 515, 100)
            heldColour = (20, 20, 20)
            if self.held:
                heldColour = (100, 0, 0)
            pygame.draw.rect(screen, heldColour, pygame.Rect(464, 130, 150, 150))
            if self.heldPiece != None:
                for j in range(0, len(self.heldPiece.shape)):
                    for k in range(0, len(self.heldPiece.shape[j])):
                        if self.heldPiece.shape[j][k] != "":
                            rect = pygame.Rect((self.nextPiecesDisplayAdjust[self.heldPiece.storedShape][0] - 532 + 35 * (k - self.heldPiece.centre[0])), (self.nextPiecesDisplayAdjust[self.heldPiece.storedShape][1] + 35 * (j + self.heldPiece.centre[1])), 35, 35)
                            image = pygame.Surface(rect.size).convert()
                            image.blit(self.pieceSheet, (0, 0), self.getPieceSprite(self.heldPiece.colour))
                            screen.blit(image, rect)

            # Scoreboard
            self.renderText("SCORE: " + str(self.pScore), self.gameplayFont, 1000, 650)

            linesColour = (255, 255, 255)
            if self.linesLeft <= 0:
                linesColour = (0, 255, 0)
            self.renderText("LINES LEFT: " + str(self.linesLeft), self.gameplayFont, 1000, 680, linesColour)

            if self.combo > 1:
                self.renderText("COMBO: X" + str(self.combo), self.gameplayFont, 1000, 740, (255, 255, 0))

            if self.tetrisCombo > 1:
                self.renderText("B2B TETRISES: " + str(self.tetrisCombo), self.gameplayFont, 1000, 770, (255, 255, 0))

            self.renderText(self.recClear, self.gameplayFont, 1000, 800, (0, 255, 255))

        elif self.gameState == 1:  # Gameplay: Boss Level
            screen.fill(self.bgColour if not self.isSpace else (0, 0, 0))
            if self.gameOverDelay > 0:
                screen.fill((100, 0, 0))

            if self.isSpace:
                for star in self.stars:
                    pygame.draw.circle(screen, (255, 255, 255), (star[0], star[1]), 3)

            # Drawing the board
            pygame.draw.rect(screen, (20, 20, 20) if not self.orionIsAttacking else (100, 0, 0), pygame.Rect(325, 55, 350, 840))
            if not (self.boss.bossId == 5 and self.boss.phase >= 2):
                for i in range(0, len(self.pBoard.board)):
                    for j in range(0, len(self.pBoard.board[i])):
                        if self.pBoard.board[i][j] != "" and self.pBoard.board[i][j] != " ":
                            rect = pygame.Rect((325 + j * 35), (55 + i * 35), 35, 35)
                            image = pygame.Surface(rect.size).convert()
                            image.blit(self.pieceSheet, (0, 0), self.getPieceSprite(self.pBoard.board[i][j]))
                            screen.blit(image, rect)
             # Draw ghost piece
            for i in range(0, len(self.ghostPiece.shape)):
                for j in range(0, len(self.ghostPiece.shape[i])):
                    if self.ghostPiece.shape[i][j] != "" and 0 <= self.ghostPiece.yLoc + i < 25:
                        pygame.draw.rect(screen, (100, 100, 100), pygame.Rect((325 + 35 * (j + self.ghostPiece.xLoc - self.ghostPiece.centre[0])), (55 + 35 * (i + self.ghostPiece.yLoc - self.ghostPiece.centre[1])), 35, 35))
            
            # Draw player piece
            for i in range(0, len(self.pPiece.shape)):
                for j in range(0, len(self.pPiece.shape[i])):
                    if self.pPiece.shape[i][j] != "" and 0 <= self.pPiece.yLoc + i < 25:
                        rect = pygame.Rect((325 + 35 * (j + self.pPiece.xLoc - self.pPiece.centre[0])), (55 + 35 * (i + self.pPiece.yLoc - self.pPiece.centre[1])), 35, 35)
                        image = pygame.Surface(rect.size).convert()
                        image.blit(self.pieceSheet, (0, 0), self.getPieceSprite(self.pPiece.colour))
                        screen.blit(image, rect)
            
            # Next Queue
            displayCount = 3
            if self.boss.bossId == 2 or self.boss.bossId == 4:
                if self.boss.phase == 1:
                    displayCount = 1
                elif self.boss.phase == 2 and not self.boss.bossId == 4:
                    displayCount = 0
            elif self.boss.bossId == 5 and self.boss.phase >= 1:
                displayCount = 0
            
            self.renderText("NEXT", self.gameplayFont, 751, 100)
            for i in range(0, displayCount):
                pygame.draw.rect(screen, (20, 20, 20), pygame.Rect(700, 130 + (i * 160), 150, 150))
                wPiece = self.nextPieces[i]
                for j in range(0, len(wPiece.shape)):
                    for k in range(0, len(wPiece.shape[j])):
                        if wPiece.shape[j][k] != "":
                            rect = pygame.Rect((self.nextPiecesDisplayAdjust[wPiece.storedShape][0] - 300 + 35 * (k - wPiece.centre[0])), (self.nextPiecesDisplayAdjust[wPiece.storedShape][1] + 35 * (j + wPiece.centre[1]) + 160 * i), 35, 35)
                            image = pygame.Surface(rect.size).convert()
                            image.blit(self.pieceSheet, (0, 0), self.getPieceSprite(wPiece.colour))
                            screen.blit(image, rect)
            
            # Held Piece
            self.renderText("HOLD", self.gameplayFont, 215, 100)
            heldColour = (20, 20, 20)
            if self.held:
                heldColour = (100, 0, 0)
            pygame.draw.rect(screen, heldColour, pygame.Rect(164, 130, 150, 150))
            if self.heldPiece != None:
                for j in range(0, len(self.heldPiece.shape)):
                    for k in range(0, len(self.heldPiece.shape[j])):
                        if self.heldPiece.shape[j][k] != "":
                            rect = pygame.Rect((self.nextPiecesDisplayAdjust[self.heldPiece.storedShape][0] - 832 + 35 * (k - self.heldPiece.centre[0])), (self.nextPiecesDisplayAdjust[self.heldPiece.storedShape][1] + 35 * (j + self.heldPiece.centre[1])), 35, 35)
                            image = pygame.Surface(rect.size).convert()
                            image.blit(self.pieceSheet, (0, 0), self.getPieceSprite(self.heldPiece.colour))
                            screen.blit(image, rect)

            # Boss Display
            self.renderTextCenter(self.boss.name, self.headerFont, 1200, 170)

            borderColour = (0, 0, 0)
            if self.victoryDelay > 0:
                borderColour = (0, 100, 0)
            elif self.boss.health <= 0:
                borderColour = (100, 0, 0)
            pygame.draw.rect(screen, borderColour, pygame.Rect(1000, 200, 400, 400))

            bossImages = ["Leo", "Gemini", "Tarus", "Orion", "Tetrahedron", "RNG"]
            bossImg = pygame.image.load("sprites/" + bossImages[self.boss.bossId] + ".png").convert_alpha()
            screen.blit(bossImg, (1000, 200))

            pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(1000, 650, 400, 50))
            pygame.draw.rect(screen, (0, 150, 0), pygame.Rect(1000, 650, 400 * (self.boss.health / self.boss.healthVals[self.boss.phase]), 50))

            pygame.draw.rect(screen, (0, 0, 0), pygame.Rect(1000, 720, 400, 50))
            pygame.draw.rect(screen, (0, 0, 150), pygame.Rect(1000, 720, 400 * (self.boss.atkCharge / self.boss.atkSpeeds[self.boss.phase]), 50))

            # Scoreboard
            self.renderText("SCORE: " + str(self.pScore), self.gameplayFont, 700, 650)

            linesColour = (255, 255, 255)

            if self.combo > 1:
                self.renderText("COMBO: X" + str(self.combo), self.gameplayFont, 700, 740, (255, 255, 0))

            if self.tetrisCombo > 1:
                self.renderText("B2B TETRISES: " + str(self.tetrisCombo), self.gameplayFont, 700, 770, (255, 255, 0))

            self.renderText(self.recClear, self.gameplayFont, 700, 800, (0, 255, 255))
            
        elif self.gameState == 2:  # Game over screen
            # Background and board
            screen.fill((100, 0, 0))
            pygame.draw.rect(screen, (20, 20, 20), pygame.Rect(625, 55, 350, 840))

            # Text
            self.renderTextCenter("GAME OVER", self.headerFont, 800, 90, (255, 0, 0))
            self.renderTextCenter("Level: " + self.displayLevel, self.gameplayFont, 800, 130)
            self.renderTextCenter("Score: " + str(self.pScore), self.gameplayFont, 800, 160)

            self.renderTextCenter("> RETRY <", self.headerFont, 800, 820)
            self.renderTextCenter("> MAIN MENU <", self.headerFont, 800, 870)

        elif self.gameState == 3:  # Victory screen
            # Background and board
            screen.fill(self.bgColour)
            pygame.draw.rect(screen, (20, 20, 20), pygame.Rect(625, 55, 350, 840))

            # Text
            self.renderTextCenter("VICTORY", self.headerFont, 800, 90, (0, 255, 0))
            self.renderTextCenter("Level: " + self.displayLevel, self.gameplayFont, 800, 130)
            self.renderTextCenter("Score: " + str(self.pScore), self.gameplayFont, 800, 160)

            self.renderTextCenter("> NEXT LEVEL <", self.headerFont, 800, 820)
            self.renderTextCenter("> MAIN MENU <", self.headerFont, 800, 870)

        elif self.gameState == 4:  # Main Menu
            # Background
            screen.fill((253, 94, 83))

            # Sun
            pygame.draw.circle(screen, (248, 255, 59), (800, 600), 300)
            
            # Ground
            pygame.draw.rect(screen, (194, 94, 0), pygame.Rect(0, 700, 1600, 250))
            pygame.draw.polygon(screen, (60, 60, 60), ((700, 950), (900, 950), (810, 700), (790, 700)))

            # Temple
            pygame.draw.polygon(screen, (166, 97, 2), ((600, 700), (1000, 700), (900, 500), (850, 450), (750, 450), (700, 500)))
            pygame.draw.polygon(screen, (0, 0, 0), ((770, 700), (830, 700), (815, 660), (785, 660)))
            pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(797, 0, 6, 450))

            # Pillars
            pygame.draw.rect(screen, (166, 97, 2), pygame.Rect(400, 300, 100, 400))
            pygame.draw.rect(screen, (166, 97, 2), pygame.Rect(1100, 300, 100, 400))

            # Title
            self.renderTextCenter("ZUMA", self.titleFont, 800, 50, (255, 158, 66))
            self.renderTextCenter("But Tetris", self.headerFont, 800, 100, (255, 158, 66))

            # Buttons
            self.renderTextCenter("> Play <", self.headerFont, 800, 600, (255, 158, 66))
            self.renderTextCenter("> Help <", self.headerFont, 450, 500, (255, 158, 66))
            self.renderTextCenter("> Quit <", self.headerFont, 1150, 500, (255, 158, 66))
            
            self.renderTextCenter("> Easy <", self.headerFont, 550, 800, (255, 158, 66) if self.difficulty != 0 else (255, 255, 255))
            self.renderTextCenter("> Normal <", self.headerFont, 550, 870, (255, 158, 66) if self.difficulty != 1 else (255, 255, 255))
            self.renderTextCenter("> Hard <", self.headerFont, 1050, 800, (255, 158, 66) if self.difficulty != 2 else (255, 255, 255))
            if self.nextLevel[2] >= 18:
                self.renderTextCenter("> Grandmaster <", self.headerFont, 1050, 870, (255, 158, 66) if self.difficulty != 3 else (255, 255, 255))

        elif self.gameState == 5:  # Help Screen
            # Background
            screen.fill((253, 94, 83))

            # Pillar and Sun
            pygame.draw.rect(screen, (166, 97, 2), pygame.Rect(200, 0, 1200, 950))
            pygame.draw.circle(screen, (248, 255, 59), (1900, 475), 500)

            # Text
            self.renderTextCenter("ZUMA", self.titleFont, 800, 50, (255, 158, 66))
            self.renderTextCenter("But Tetris", self.headerFont, 800, 100, (255, 158, 66))

            self.renderTextCenter("=== CONTROLS ===", self.headerFont, 800, 200, (255, 158, 66))
            self.renderTextCenter("Left and right: Move current piece", self.headerFont, 800, 240, (255, 158, 66))
            self.renderTextCenter("Down: Push current piece down", self.headerFont, 800, 280, (255, 158, 66))
            self.renderTextCenter("Up or Z and X: Rotate current piece", self.headerFont, 800, 320, (255, 158, 66))
            self.renderTextCenter("Space: Hard-drop Piece", self.headerFont, 800, 360, (255, 158, 66))
            self.renderTextCenter("C: Hold Piece", self.headerFont, 800, 400, (255, 158, 66))

            self.renderTextCenter("=== HOW TO PLAY ===", self.headerFont, 800, 500, (255, 158, 66))
            self.renderTextCenter("Fill rows in the board to clear lines", self.headerFont, 800, 540, (255, 158, 66))
            self.renderTextCenter("Clear lines to get points and proress through the level", self.headerFont, 800, 580, (255, 158, 66))
            self.renderTextCenter("Beat each level to unlock the next one for that difficulty", self.headerFont, 800, 620, (255, 158, 66))

            self.renderTextCenter("> Back <", self.headerFont, 800, 900, (255, 158, 66))

        elif self.gameState == 6:  # Play
            skyColours = [(253, 94, 83), (75, 61, 96), (21, 40, 82), (8, 24, 58), (0, 0, 0), (random.choice(range(0, 41)), random.choice(range(0, 41)), random.choice(range(0, 41)))]
            levelNames = ["LEO", "GEMINI", "TARUS", "ORION", "TETRAHEDRON", "RNG"]
            titleNames = ["Test of Skill", "Test of Speed", "Test of Endurance", "Test of Perseverence", "The Final Test", "Test of Insanity"]
            
            # Sky and sun
            screen.fill(skyColours[self.currentChapter])
            pygame.draw.circle(screen, (248, 255, 59), (800, (600 + self.currentChapter * 100)), 500)

            # Temple
            pygame.draw.rect(screen, (166, 97, 2), pygame.Rect(0, 450, 1600, 950))

            # Text
            self.renderTextCenter(levelNames[self.currentChapter], self.titleFont, 800, 50, (255, 255, 255))
            self.renderTextCenter(titleNames[self.currentChapter], self.headerFont, 800, 100, (255, 255, 255))

            if self.currentChapter == 5:
                if self.nextLevel[self.difficulty] >= 18:
                    self.renderTextCenter("> ??? <", self.headerFont, 800, 725, (255, 255, 255))
                    self.renderTextCenter("High Score: " + str(self.highScores[self.difficulty][18]), self.gameplayFont, 800, 755, (255, 255, 255))
            elif self.currentChapter == 4:
                if self.nextLevel[self.difficulty] >= 16:
                    self.renderTextCenter("> Ascension <", self.headerFont, 800, 550, (255, 255, 255))
                    self.renderTextCenter("High Score: " + str(self.highScores[self.difficulty][16]), self.gameplayFont, 800, 580, (255, 255, 255))

                if self.nextLevel[self.difficulty] >= 17:
                    self.renderTextCenter("> Final Battle <", self.headerFont, 800, 725, (255, 255, 255))
                    self.renderTextCenter("High Score: " + str(self.highScores[self.difficulty][17]), self.gameplayFont, 800, 755, (255, 255, 255))
            else:
                if self.nextLevel[self.difficulty] >= (self.currentChapter * 4):
                    self.renderTextCenter("> Chamber 1 <", self.headerFont, 800, 550, (255, 255, 255))
                    self.renderTextCenter("High Score: " + str(self.highScores[self.difficulty][(self.currentChapter * 4)]), self.gameplayFont, 800, 580, (255, 255, 255))
                if self.nextLevel[self.difficulty] >= (self.currentChapter * 4) + 1:
                    self.renderTextCenter("> Chamber 2 <", self.headerFont, 500, 900, (255, 255, 255))
                    self.renderTextCenter("High Score: " + str(self.highScores[self.difficulty][(self.currentChapter * 4) + 1]), self.gameplayFont, 500, 930, (255, 255, 255))
                if self.nextLevel[self.difficulty] >= (self.currentChapter * 4) + 2:
                    self.renderTextCenter("> Chamber 3 <", self.headerFont, 1100, 900, (255, 255, 255))
                    self.renderTextCenter("High Score: " + str(self.highScores[self.difficulty][(self.currentChapter * 4) + 2]), self.gameplayFont, 1100, 930, (255, 255, 255))
                if self.nextLevel[self.difficulty] >= (self.currentChapter * 4) + 3:
                    self.renderTextCenter("> Battle <", self.headerFont, 800, 725, (255, 255, 255))
                    self.renderTextCenter("High Score: " + str(self.highScores[self.difficulty][(self.currentChapter * 4) + 3]), self.gameplayFont, 800, 755, (255, 255, 255))

            self.renderTextCenter("> Back <", self.headerFont, 800, 900, (255, 255, 255))

            if (self.difficulty == 3 and self.currentChapter < 5) or (self.difficulty < 3 and self.currentChapter < 4) and (((self.nextLevel[self.difficulty] >= (self.currentChapter * 4) + 4) and self.currentChapter < 4) or ((self.nextLevel[self.difficulty] >= 18 and self.currentChapter == 4))):
                self.renderTextCenter("-->", self.titleFont, 1550, 920, (255, 255, 255))
            if self.currentChapter > 0:
                self.renderTextCenter("<--", self.titleFont, 50, 920, (255, 255, 255))

        elif self.gameState == 7:  # Story
            skyColours = [(253, 94, 83), (75, 61, 96), (21, 40, 82), (8, 24, 58), (0, 0, 0), (253, 94, 83), (random.choice(range(0, 41)), random.choice(range(0, 41)), random.choice(range(0, 41))), (253, 94, 83)]

            screen.fill(skyColours[self.storyPart])
            if self.storyPart == 0:  # Opening
                pygame.draw.rect(screen, (166, 97, 2), pygame.Rect(200, 0, 1200, 950))
                
                self.renderTextCenter("Tetrahedron welcomes you to the Tetris Temple! Welcome!", self.headerFont, 800, 50, (255, 255, 255))
                self.renderTextCenter("The temple houses riches only told in myths and fairy-tales.", self.headerFont, 800, 90, (255, 255, 255))
                self.renderTextCenter("Many have already tried their hand at sieging the impregnable temple.", self.headerFont, 800, 130, (255, 255, 255))
                self.renderTextCenter("Their skulls and bones now line the walls of the hallways.", self.headerFont, 800, 170, (255, 255, 255))

                self.renderTextCenter("You may attempt your own adventure into the temple.", self.headerFont, 800, 250, (255, 255, 255))
                self.renderTextCenter("Clear the puzzles ahead and evade the obstacles.", self.headerFont, 800, 290, (255, 255, 255))
                self.renderTextCenter("Defeat all four of Tetrahedron's Champions to earn a match with it.", self.headerFont, 800, 330, (255, 255, 255))
                self.renderTextCenter("Their names - Leo, Gemini, Tarus, Orion.", self.headerFont, 800, 370, (255, 255, 255))
                self.renderTextCenter("Now for your first challenge. A test of skill to see if you are ready:", self.headerFont, 800, 450, (255, 255, 255))
                self.renderTextCenter("LEO", self.headerFont, 800, 490, (255, 255, 255))

            elif self.storyPart == 1:  # LEO defeated
                pygame.draw.rect(screen, (166, 97, 2), pygame.Rect(200, 0, 1200, 950))
                
                self.renderTextCenter("With the fall of Leo, a second path shall open up.", self.headerFont, 800, 50, (255, 255, 255))
                self.renderTextCenter("Adventurers beware! This path is terribly dangerous!", self.headerFont, 800, 90, (255, 255, 255))
                self.renderTextCenter("Those who are too slow shall be trampled and crushed.", self.headerFont, 800, 130, (255, 255, 255))
                self.renderTextCenter("While those who are swift enough may wake up again tomorrow.", self.headerFont, 800, 170, (255, 255, 255))
                self.renderTextCenter("Prepare yourself for the test of speed:", self.headerFont, 800, 210, (255, 255, 255))
                self.renderTextCenter("GEMINI", self.headerFont, 800, 250, (255, 255, 255))
                
                self.renderTextCenter("> Next <", self.headerFont, 800, 920, (255, 255, 255))

            elif self.storyPart == 2:  # GEMINI defeated
                pygame.draw.rect(screen, (166, 97, 2), pygame.Rect(200, 0, 1200, 950))
                
                self.renderTextCenter("Through speed, adventurers may find themselves in the third path.", self.headerFont, 800, 50, (255, 255, 255))
                self.renderTextCenter("Your endurance will be put to the test, for this path is long and exhausting.", self.headerFont, 800, 90, (255, 255, 255))
                self.renderTextCenter("Many fell, losing the strength and will to continue after several minutes.", self.headerFont, 800, 130, (255, 255, 255))
                self.renderTextCenter("You must rise up and press onwards for however long if you wish to keep your life.", self.headerFont, 800, 170, (255, 255, 255))
                self.renderTextCenter("Prepare yourself for the test of endurance:", self.headerFont, 800, 210, (255, 255, 255))
                self.renderTextCenter("TARUS", self.headerFont, 800, 250, (255, 255, 255))
                
                self.renderTextCenter("> Next <", self.headerFont, 800, 920, (255, 255, 255))

            elif self.storyPart == 3:  # TARUS defeated
                pygame.draw.rect(screen, (166, 97, 2), pygame.Rect(200, 0, 1200, 950))
                
                self.renderTextCenter("With endurance and speed, only perseverence is needed to delve into the temple.", self.headerFont, 800, 50, (255, 255, 255))
                self.renderTextCenter("The temple is unforgiving, and puts its adventurers in peril time and time again.", self.headerFont, 800, 90, (255, 255, 255))
                self.renderTextCenter("Only one who can continue onwards no matter what may find themselves evading an early grave.", self.headerFont, 800, 130, (255, 255, 255))
                self.renderTextCenter("Only if you can remain calm under pressure and not crack will you be allowed onwards.", self.headerFont, 800, 170, (255, 255, 255))
                self.renderTextCenter("Prepare yourself for the test of perseverence:", self.headerFont, 800, 210, (255, 255, 255))
                self.renderTextCenter("ORION", self.headerFont, 800, 250, (255, 255, 255))
                
                self.renderTextCenter("> Next <", self.headerFont, 800, 920, (255, 255, 255))

            elif self.storyPart == 4:  # ORION defeated
                pygame.draw.rect(screen, (166, 97, 2), pygame.Rect(200, 0, 1200, 950))
                
                self.renderTextCenter("When all four guardians fall, Tetrahedron shall reveal himself.", self.headerFont, 800, 50, (255, 255, 255))
                self.renderTextCenter("Head up the white beam shooting into the stars and bring yourself to his realm.", self.headerFont, 800, 90, (255, 255, 255))
                self.renderTextCenter("Survive Tetrahedron's final challenge and prepare yourself to be face to face with the being.", self.headerFont, 800, 130, (255, 255, 255))
                self.renderTextCenter("Prepare yourself for your final test:", self.headerFont, 800, 210, (255, 255, 255))
                self.renderTextCenter("TETRAHEDRON", self.headerFont, 800, 250, (255, 255, 255))
                
                self.renderTextCenter("> Next <", self.headerFont, 800, 920, (255, 255, 255))

            elif self.storyPart == 5:  # TETRAHEDRON defeated (Easy to Hard)
                pygame.draw.rect(screen, (166, 97, 2), pygame.Rect(200, 0, 1200, 950))
                
                self.renderTextCenter("Should you best Tetrahedron, the final room will reveal itself.", self.headerFont, 800, 50, (255, 255, 255))
                self.renderTextCenter("Treasures collected over milleniums will burst forth from the room.", self.headerFont, 800, 90, (255, 255, 255))
                self.renderTextCenter("Only someone worthy of such wealth will be able to hold it.", self.headerFont, 800, 130, (255, 255, 255))
                self.renderTextCenter("Only someone deemed to posses the necessary skill will reach it.", self.headerFont, 800, 170, (255, 255, 255))
                self.renderTextCenter("However, those with far more skill may find themselves with a different choice.", self.headerFont, 800, 210, (255, 255, 255))
                self.renderTextCenter("The choice to face the real mastermind behind the temple.", self.headerFont, 800, 250, (255, 255, 255))

                self.renderTextCenter("Thanks for playing.", self.headerFont, 800, 370, (255, 255, 255))
                
                self.renderTextCenter("> Next <", self.headerFont, 800, 920, (255, 255, 255))

            elif self.storyPart == 6:  # TETRAHEDRON defeated (Grandmaster)
                pygame.draw.rect(screen, (166, 97, 2), pygame.Rect(200, 0, 1200, 950))
                
                self.renderTextCenter("Should you best Tetrahedron, the final room will reveal itself.", self.headerFont, 800, 50, (255, 255, 255))
                self.renderTextCenter("Treasures collected over milleniums will burst forth from the room.", self.headerFont, 800, 90, (255, 255, 255))
                self.renderTextCenter("Only someone worthy of such wealth will be able to hold it.", self.headerFont, 800, 130, (255, 255, 255))
                self.renderTextCenter("Only someone deemed to posses the necessary skill will reach it.", self.headerFont, 800, 170, (255, 255, 255))
                self.renderTextCenter("However, those with far more skill may find themselves with a different choice.", self.headerFont, 800, 210, (255, 255, 255))
                self.renderTextCenter("The choice to face the real mastermind behind the temple.", self.headerFont, 800, 250, (255, 255, 255))

                for i in range(0, random.choice(range(3, 6))):
                    self.renderTextCenter("RNG", self.headerFont, random.choice(range(400, 1200)), random.choice(range(300, 900)), (255, 255, 255))

            elif self.storyPart == 7:  # RNG defeated
                self.renderTextCenter("You've done it! You've defeated the mastermind behind the temple!", self.headerFont, 800, 50, (255, 255, 255))
                self.renderTextCenter("As the temple collapses, you've realised you gained something from exploring it.", self.headerFont, 800, 90, (255, 255, 255))
                self.renderTextCenter("You may not have secured all of the riches and gold inside of the place.", self.headerFont, 800, 130, (255, 255, 255))
                self.renderTextCenter("However, that didn't matter.", self.headerFont, 800, 170, (255, 255, 255))
                self.renderTextCenter("That stuff was never real.", self.headerFont, 800, 210, (255, 255, 255))
                self.renderTextCenter("Neither was that temple.", self.headerFont, 800, 250, (255, 255, 255))

                self.renderTextCenter("You gained skill. Skill that will always stick with you.", self.headerFont, 800, 330, (255, 255, 255))
                self.renderTextCenter("And that was the real reward of the temple.", self.headerFont, 800, 370, (255, 255, 255))
                self.renderTextCenter("The real reward of this game.", self.headerFont, 800, 410, (255, 255, 255))

                self.renderTextCenter("THE END", self.headerFont, 800, 490, (255, 255, 255))
                self.renderTextCenter("Thanks for playing!", self.headerFont, 800, 530, (255, 255, 255))
                
            self.renderTextCenter("> Next <", self.headerFont, 800, 920, (255, 255, 255))

        pygame.display.flip() # Display drawn objects on screen

# Run the actual game
game = Game() # Game object

gameRunning = True
while gameRunning:
    ev = pygame.event.get()

    # Handing player pressing the "X" button. Put any player input into the "game.logic" function to keep this section clutter-free.
    for event in ev:
        if event.type == pygame.QUIT:
            gameRunning = False
    
    # Run game functions
    game.logic()
    game.draw()

    time.sleep(tickDelay)

pygame.quit()
