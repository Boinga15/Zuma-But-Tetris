from actors import Boss

class Levels:
    def __init__(self):
        self.levelNames = [
            "LEO - Chamber 1", "LEO - Chamber 2", "LEO - Chamber 3", "LEO - Battle",
            "GEMINI - Chamber 1", "GEMINI - Chamber 2", "GEMINI - Chamber 3", "GEMINI - Battle",
            "TARUS - Chamber 1", "TARUS - Chamber 2", "TARUS - Chamber 3", "TARUS - Battle",
            "ORION - Chamber 1", "ORION - Chamber 2", "ORION - Chamber 3", "ORION - Battle",
            "TETRAHEDRON - Ascent", "TETRAHEDRON - Battle", "RNG - Battle"
        ]

        self.levelState = [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1]
        
        self.levelLinesLeft = [
            [20, 40, 60, 80], [25, 45, 65, 85], [25, 45, 65, 85], [20, 40, 60, 80],
            [20, 40, 70, 70], [20, 40, 70, 70], [25, 45, 75, 75], [20, 40, 60, 80],
            [50, 60, 90, 120], [60, 70, 100, 130], [70, 80, 100, 150], [40, 60, 80, 100],
            [50, 70, 90, 120], [60, 80, 100, 130], [60, 80, 100, 140], [20, 40, 60, 80],
            [100, 200, 300, 400], [25, 45, 65, 85], [25, 45, 65, 85]
        ]
        self.levelDropSpeed = [
            [80, 60, 30, 10], [70, 50, 25, 9], [60, 40, 20, 8], [80, 60, 30, 10],
            [40, 30, 20, 10], [35, 25, 15, 5], [30, 20, 15, 4], [40, 30, 20, 5],
            [50, 40, 30, 10], [40, 30, 20, 6], [40, 25, 15, 3], [80, 60, 30, 10],
            [20, 15, 10, 3], [15, 10, 5, 2], [13, 8, 4, 1], [20, 15, 10, 3],
            [30, 20, 10, 0], [35, 25, 15, 5], [80, 60, 30, 10]
        ]
        self.levelGarbage = [
            [0, 0, 0, 500], [0, 0, 0, 450], [0, 0, 0, 400], [0, 0, 0, 500],
            [0, 0, 0, 400], [0, 0, 0, 370], [0, 0, 0, 350], [0, 0, 0, 500],
            [1000, 900, 800, 400], [900, 800, 700, 350], [700, 600, 500, 300], [0, 0, 0, 500],
            [600, 500, 400, 300], [500, 400, 400, 300], [500, 400, 300, 300], [0, 0, 0, 500],
            [0, 0, 300, 200], [0, 0, 0, 450], [0, 0, 0, 450]
        ]
        self.levelBackground = [(138, 102, 52), (138, 102, 52), (138, 102, 52), (138, 102, 52), (138, 102, 52), (138, 102, 52), (138, 102, 52), (138, 102, 52), (138, 102, 52), (138, 102, 52), (138, 102, 52), (138, 102, 52), (138, 102, 52), (138, 102, 52), (138, 102, 52), (138, 102, 52), (0, 0, 0), (0, 0, 0), (138, 102, 52)]

        self.bossFights = [
            [
                Boss([20, 30, 40], [1000, 900, 800], [1, 1, 2], [0, 10, 20], "LEO", 0),
                Boss([30, 40, 50], [800, 700, 600], [1, 2, 2], [20, 40, 60], "LEO", 0),
                Boss([30, 40, 60], [700, 600, 500], [1, 2, 3], [30, 50, 70], "LEO", 0),
                Boss([50, 60, 70], [600, 500, 400], [2, 3, 5], [50, 70, 90], "LEO", 0)
            ],
            [
                Boss([10, 20, 30], [800, 700, 600], [1, 1, 1], [0, 10, 20], "GEMINI", 1),
                Boss([20, 30, 40], [700, 600, 500], [1, 1, 2], [20, 40, 60], "GEMINI", 1),
                Boss([30, 40, 50], [600, 500, 400], [1, 2, 2], [30, 50, 70], "GEMINI", 1),
                Boss([40, 50, 60], [500, 400, 300], [2, 2, 3], [50, 60, 70], "GEMINI", 1)
            ],
            [
                Boss([60, 70, 80], [2000, 1500, 1000], [4, 5, 6], [0, 10, 10], "TARUS", 2),
                Boss([70, 80, 90], [2000, 1500, 1000], [5, 6, 7], [20, 20, 20], "TARUS", 2),
                Boss([80, 90, 100], [1500, 1000, 1500], [6, 7, 25], [40, 40, 40], "TARUS", 2),
                Boss([100, 120, 150], [1200, 1000, 1500], [7, 8, 25], [70, 70, 70], "TARUS", 2)
            ],
            [
                Boss([40, 60, 80], [700, 600, 500], [1, 1, 3], [30, 50, 70], "ORION", 3),
                Boss([50, 60, 80], [700, 600, 450], [2, 2, 3], [30, 50, 70], "ORION", 3),
                Boss([60, 80, 100], [650, 550, 450], [3, 3, 3], [50, 70, 90], "ORION", 3),
                Boss([100, 120, 150], [500, 400, 300], [5, 5, 5], [100, 100, 100], "ORION", 3)
            ],
            [
                Boss([60, 80, 30], [800, 600, 300], [3, 4, 1], [20, 40, 60], "TETRAHEDRON", 4),
                Boss([80, 100, 50], [700, 500, 200], [4, 5, 1], [40, 60, 80], "TETRAHEDRON", 4),
                Boss([100, 120, 60], [700, 500, 100], [5, 6, 1], [50, 70, 90], "TETRAHEDRON", 4),
                Boss([120, 150, 75], [600, 400, 50], [6, 6, 1], [60, 80, 100], "TETRAHEDRON", 4)
            ],
            [
                Boss([70, 100, 60], [600, 400, 1000], [3, 4, 2], [100, 100, 100], "RNG", 5),
                Boss([70, 100, 60], [600, 400, 1000], [3, 4, 2], [100, 100, 100], "RNG", 5),
                Boss([70, 100, 60], [600, 400, 1000], [3, 4, 2], [100, 100, 100], "RNG", 5),
                Boss([70, 100, 60], [600, 400, 1000], [3, 4, 2], [100, 100, 100], "RNG", 5)
            ]
        ]
