class Boss:
    def __init__(self, healthVals, atkSpeeds, atkPowers, atkRandomness, name, bossId):
        self.healthVals = healthVals
        self.atkSpeeds = atkSpeeds
        self.atkPowers = atkPowers
        self.atkRandomness = atkRandomness
        self.name = name
        self.bossId = bossId
        
        self.phase = 0
        self.health = self.healthVals[0]
        self.atkCharge = 0

class Piece:
    def __init__(self, shape):
        self.storedShape = shape

        # Wall kicks
        self.wallKickIndexes = [[0, 1], [1, 0], [1, 2], [2, 1], [2, 3], [3, 2], [3, 0], [0, 3]]
        self.wallKicks = [
            [[0, 0], [-1, 0], [-1, 1], [0, -2], [-1, -2]],
            [[0, 0], [1, 0], [1, -1], [0, 2], [1, 2]],
            [[0, 0], [1, 0], [1, -1], [0, 2], [1, 2]],
            [[0, 0], [-1, 0], [-1, 1], [0, -2], [-1, -2]],
            [[0, 0], [1, 0], [1, 1], [0, -2], [1, -2]],
            [[0, 0], [-1, 0], [-1, -1], [0, 2], [-1, 2]],
            [[0, 0], [-1, 0], [-1, -1], [0, 2], [-1, 2]],
            [[0, 0], [1, 0], [1, 1], [0, -2], [1, -2]]
        ]
        
        if shape == 0:  # T-Piece
            self.rotations = [
                [["", "P", ""],
                ["P", "P", "P"],
                ["", "", ""]],
                [["", "P", ""],
                ["", "P", "P"],
                ["", "P", ""]],
                [["", "", ""],
                ["P", "P", "P"],
                ["", "P", ""]],
                [["", "P", ""],
                ["P", "P", ""],
                ["", "P", ""]]
            ]
            self.colour = "P"
            self.centre = [1, 1]
            self.yLoc = 1
        elif shape == 1:  # O-Piece
            self.rotations = [
                [["P", "P"],
                ["P", "P"]],
                [["P", "P"],
                ["P", "P"]],
                [["P", "P"],
                ["P", "P"]],
                [["P", "P"],
                ["P", "P"]]
            ]
            self.colour = "Y"
            self.centre = [0, 0]
            self.yLoc = 0
        elif shape == 2:  # L-Piece
            self.rotations = [
                [["", "", "P"],
                ["P", "P", "P"],
                ["", "", ""]],
                [["", "P", ""],
                ["", "P", ""],
                ["", "P", "P"]],
                [["", "", ""],
                ["P", "P", "P"],
                ["P", "", ""]],
                [["P", "P", ""],
                ["", "P", ""],
                ["", "P", ""]]
            ]
            self.colour = "O"
            self.centre = [1, 1]
            self.yLoc = 1
        elif shape == 3:  # J-Piece
            self.rotations = [
                [["P", "", ""],
                ["P", "P", "P"],
                ["", "", ""]],
                [["", "P", "P"],
                ["", "P", ""],
                ["", "P", ""]],
                [["", "", ""],
                ["P", "P", "P"],
                ["", "", "P"]],
                [["", "P", ""],
                ["", "P", ""],
                ["P", "P", ""]]
            ]
            self.colour = "B"
            self.centre = [1, 1]
            self.yLoc = 1
        elif shape == 4:  # S-Piece
            self.rotations = [
                [["", "P", "P"],
                ["P", "P", ""],
                ["", "", ""]],
                [["", "P", ""],
                ["", "P", "P"],
                ["", "", "P"]],
                [["", "", ""],
                ["", "P", "P"],
                ["P", "P", ""]],
                [["P", "", ""],
                ["P", "P", ""],
                ["", "P", ""]]
            ]
            self.colour = "G"
            self.centre = [1, 1]
            self.yLoc = 1
        elif shape == 5:  # Z-Piece
            self.rotations = [
                [["P", "P", ""],
                ["", "P", "P"],
                ["", "", ""]],
                [["", "", "P"],
                ["", "P", "P"],
                ["", "P", ""]],
                [["", "", ""],
                ["P", "P", ""],
                ["", "P", "P"]],
                [["", "P", ""],
                ["P", "P", ""],
                ["P", "", ""]]
            ]
            self.colour = "R"
            self.centre = [1, 1]
            self.yLoc = 1
        else:  # I-Piece
            self.rotations = [
                [["", "", "", ""],
                ["P", "P", "P", "P"],
                ["", "", "", ""],
                ["", "", "", ""]],
                [["", "", "P", ""],
                ["", "", "P", ""],
                ["", "", "P", ""],
                ["", "", "P", ""]],
                [["", "", "", ""],
                ["", "", "", ""],
                ["P", "P", "P", "P"],
                ["", "", "", ""]],
                [["", "P", "", ""],
                ["", "P", "", ""],
                ["", "P", "", ""],
                ["", "P", "", ""]]
            ]
            self.colour = "L"
            self.centre = [1, 1]
            self.yLoc = 1

            self.wallKicks = [
                [[0, 0], [-2, 0], [1, 0], [-2, -1], [1, 2]],
                [[0, 0], [2, 0], [-1, 0], [2, 1], [-1, -2]],
                [[0, 0], [-1, 0], [2, 0], [-1, 2], [2, -1]],
                [[0, 0], [1, 0], [-2, 0], [1, -2], [-2, 1]],
                [[0, 0], [2, 0], [-1, 0], [2, 1], [-1, -2]],
                [[0, 0], [-2, 0], [1, 0], [-2, -1], [1, 2]],
                [[0, 0], [1, 0], [-2, 0], [1, -2], [-2, 1]],
                [[0, 0], [-1, 0], [2, 0], [-1, 2], [2, -1]]
            ]

        self.cRot = 0
        self.shape = self.rotations[self.cRot]
        self.xLoc = 4

    def isColliding(self, board, autoAdjust=False, prevRot=0, kick=0):
        # Wall kick
        wallKick = [0, 0]
        for i in self.wallKickIndexes:
            if i[1] == self.cRot and i[0] == prevRot:
                wallKick = self.wallKicks[self.wallKickIndexes.index(i)][kick]

        self.xLoc += wallKick[0]
        self.yLoc += wallKick[1]
        
        for i in range(0, len(self.shape)):
            for j in range(0, len(self.shape[i])):
                if self.shape[i][j] == "P":
                    location = [self.xLoc - self.centre[0] + j, self.yLoc - self.centre[1] + i]
                    try:
                        if board[location[1]][location[0]] != " " or location[0] < 0 or location[1] < 0:
                            if autoAdjust:
                                self.xLoc -= wallKick[0]
                                self.yLoc -= wallKick[1]
                                if kick >= 4:
                                    return True
                                else:
                                    return self.isColliding(board, True, prevRot, kick+1)
                            else:
                                return True
                    except IndexError:
                        if autoAdjust:
                            self.xLoc -= wallKick[0]
                            self.yLoc -= wallKick[1]
                            if kick >= 4:
                                return True
                            else:
                                return self.isColliding(board, True, prevRot, kick+1)
                        else:
                            return True
        return False
    
class Board:
    def __init__(self):
        self.board = [
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " "],
            [" ", " ", " ", " ", " ", " ", " ", " ", " ", " "]
        ]
