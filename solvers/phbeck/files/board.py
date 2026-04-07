import numpy as np
import itertools as it

from .cell import Cell
from .units import Unit, Row, Col, Block


def flatten(lst_of_lsts):
    flat_list = []
    for row in lst_of_lsts:
        flat_list.extend(row)
    return flat_list


class Sudoku():
    def __init__(self, board=None):
        if board is None:
            self.board = self.default_board()
        else:
            self.board = board



        # Cells
        self.Cells = [[Cell(self, row,col,Block.findBlock(row,col)) for col in range(9)] for row in range(9)]

        # rows
        self.rows = [Row(unitCells = self.Cells[r]) for r in range(9)]

        # cols
        self.cols = [Col(unitCells=[self.Cells[r][c] for r in range(9)]) for c in range(9)]

        # blocks
        self.blocks = [Block(
            unitCells = flatten(
                [row[(b%3)*3:(b%3)*3+3] for row in self.Cells[(b//3)*3:(b//3)*3+3]]
            ) ) for b in range(9)]
        
        # allUnits
        self.Units = self.rows + self.cols + self.blocks


    # -------------------------------------------------------------------------------------------
    # SOLVE SUDOKU    
    def solveSudoku(self):

        self.prepareBoard()

        # print("\nInitial Sudoku:") 
        # self.printSudoku()

        t = 50
        flag = True
        while t > 0 and flag and not self.complete():
            
            t -= 1
            flag = False

            sN, sC = self.existsSingles()
            if sN:
                flag = True
                self.fillSingleCells(sN, sC)

            flag |= self.eliminateCandidates() 

        # self.printCandidates()
            
        # print("\nSolved Sudoku:") 
        # self.printSudoku()
    
        # if not self.correct() or not self.complete():
        #     print("Sudoku is correct: ", self.correct())
        #     print("Sudoku is complete: ", self.complete())

        return np.array([list(map(lambda c: c.value, row)) for row in self.Cells])

       
    # -------------------------------------------------------------------------------------------
    # PREPARE BOARD   
    def prepareBoard(self):
        Cells, rows, cols, blocks = self.Cells, self.rows, self.cols, self.blocks

        # fills in all values into the Cells
        for r in range(9):
            for c in range(9):
                value = self.board[r][c]
                Cells[r][c].value = value
                Cells[r][c].full = bool(value)



            
        # setzt die Parameter "numbersCount", "numbersInUnit" für alle Reihen/Spalten/Blöcke
        for unit in self.Units:
            unit.setNumbersInUnit()

        # setzt die Kandidaten in den Zellen
        for block in self.blocks:
            block.setCandidatesInCells()

        # setzt den Parameter "candidatesInUnit" für alle Reihen/Spalten/Blöcke
        for unit in self.Units:
            unit.updateCandidatesInUnit()


    
    # -------------------------------------------------------------------------------------------
    # ELIMINATING CANDIDATES
    def eliminateCandidates(self):
        
        flag1, flag2, flag3 = False, False, False

        for unit in self.Units:
            flag1 = unit.removeObviousPair()
            flag2 = unit.removeHiddenPair()
            flag3 = unit.removePointingOrReduction()
        
        return np.any([flag1, flag2, flag3])

    
    
    # -------------------------------------------------------------------------------------------
    # FINDING SINGLES
    def existsSingles(self):
        singleNumbers = []
        singleCells = []
        seenCells = set()
        for i in range(9):
            sN, sC = self.blocks[i].hasSingleCell()
            singleNumbers.extend(sN)
            singleCells.extend(sC)
            seenCells.update(sC)

        for i in range(9):
            sNr, sCr = self.rows[i].hasSingleNumber()
            sNc, sCc = self.cols[i].hasSingleNumber()
            sNb, sCb = self.blocks[i].hasSingleNumber()

        
            for n, cell in zip(sNr + sNc + sNb, sCr + sCc + sCb):
                if cell not in seenCells:
                    
                    singleNumbers.append(n)
                    singleCells.append(cell)
                    seenCells.add(cell)
                
        return singleNumbers, singleCells
    
    # -------------------------------------------------------------------------------------------
    # FILLING IN SINGLE CELLS

    def fillSingleCells(self, sN, sC):
        Cells, rows, cols, blocks = self.Cells, self.rows, self.cols, self.blocks

        for idx, cell in enumerate(sC):
            if cell.full:
                if cell.value != sN[idx]:
                    print("error!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            else:
                cell.fillCell(sN[idx])



   
        

    # -------------------------------------------------------------------------------------------
    # CORRECTNESS & COMPLETENESS  
    def correct(self):
        flag = True
        for i in range(9):
            numbersR = set()
            numbersC = set()
            numbersB = set()

            for cell in self.rows[i].unitCells:
                if cell.full:
                    if cell.value not in numbersR:
                        numbersR.add(cell.value)
                    else:
                        print("R: ", numbersR)
                        print("mistake at ", cell.r, ", ", cell.c)
                        flag = False
            
            for cell in self.cols[i].unitCells:
                if cell.full:
                    if cell.value not in numbersC:
                        numbersC.add(cell.value)
                    else:
                        print("C: ", numbersC)
                        print("mistake at ", cell.r, ", ", cell.c)
                        flag = False
            
            for cell in self.blocks[i].unitCells:
                if cell.full:
                    if cell.value not in numbersB:
                        numbersB.add(cell.value)
                    else:
                        print("B: ", numbersB)
                        print("mistake at ", cell.r, ", ", cell.c)
                        flag = False
        return flag

    def complete(self):
        flag = True
        for i in range(9):
            for j in range(9):
                if not self.Cells[i][j].full:
                    flag = False
        return flag

    

    # -------------------------------------------------------------------------------------------
    # DEFAULT BOARD

    def default_board(self):
        return np.array([
            [0,2,7,5,9,4,0,0,0],
            [0,4,9,0,1,3,0,0,7],
            [0,0,0,6,0,7,9,0,4],
            [4,0,0,1,0,0,0,0,2],
            [2,0,0,0,0,0,7,0,0],
            [7,5,0,0,0,0,0,9,6],
            [0,7,4,9,0,0,0,6,0],
            [1,0,5,7,0,6,0,0,9],
            [9,6,2,4,5,1,3,7,8]
        ])


    # -------------------------------------------------------------------------------------------
    # PRINT
    def printSudoku(self):
        for row in self.Cells: 
            print(" ".join(str(Cell.value) for Cell in row)) 

    def printCandidates(self):
        for row in self.Cells:
            for cell in row:
                print(cell.r, ", ", cell.c, ", ", np.where(cell.candidates)[0]+1, ", ", cell.candidatesCount)   



    # -------------------------------------------------------------------------------------------















