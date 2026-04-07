import numpy as np

class Cell():
    def __init__(self, board, r, c, b):
        self.r = r
        self.c = c
        self.b = b
        self.board = board
        self.value = 0                              # Wert in der Zelle
        self.full = False                           # boolean ob Zelle ausgefüllt ist
        self.candidatesCount = 9                    # Wieviele Kandidaten die Zelle hat
        self.candidates = np.ones(9, dtype=bool)    # Welche Zahlen kandidieren
        



    # -------------------------------------------------------------------------------------------
    # REMOVING CANDIDATES
    def removeCandidate(self, i):
        brd = self.board 

        if self.candidates[i]:
            self.candidates[i] = False
            self.candidatesCount -= 1

            brd.rows[self.r].candidatesInUnit[i] -= 1
            brd.cols[self.c].candidatesInUnit[i] -= 1
            brd.blocks[self.b].candidatesInUnit[i] -= 1

    # -------------------------------------------------------------------------------------------
    # FILLING IN CELL
    def fillCell(self, value):
        self.value = value
        self.full = True
        self.candidates = np.zeros(9, dtype=bool)
        self.candidatesCount = 0

        # print("filling in ", value, " at cell ", self.r, ", ", self.c)
        
        brd = self.board

        for i in range(9):
            # entfernt alle kandidaten von der neu ausgefüllten zelle
            self.removeCandidate(i)

            # entfernt diesen Kandidaten von allen Zellen aus verbundenen Reihen/Spalten/Block
            brd.rows[self.r].unitCells[i].removeCandidate(self.value - 1)
            brd.cols[self.c].unitCells[i].removeCandidate(self.value - 1)
            brd.blocks[self.b].unitCells[i].removeCandidate(self.value - 1)
            

        self.updateUnitOfCell()

    # -------------------------------------------------------------------------------------------
    # UPDATES TO UNITS   
    def updateUnitOfCell(self):
                
        brd = self.board
        rows, cols, blocks = brd.rows, brd.cols, brd.blocks
        r, c, b = self.r, self.c, self.b
        

        rows[r].updateCandidatesInUnit()
        cols[c].updateCandidatesInUnit()
        blocks[b].updateCandidatesInUnit()

        rows[r].setNumbersInUnit()
        cols[c].setNumbersInUnit()
        blocks[b].setNumbersInUnit()