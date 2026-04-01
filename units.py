import numpy as np
import itertools as it

from .cell import Cell

class Unit:
    def __init__(self, unitCells=None):
        self.numbersCount = 0                           # Wieviele Zellen im Unit ausgefüllt sind
        self.numbersInUnit = np.zeros(9, dtype=bool)    # Welche numbers bereits ausgefüllt sind
        self.candidatesInUnit = 9 * np.ones(9)          # Welche Zahl wie oft als Kandidat in den Zellen vorkommt
        if unitCells is None:                           
            self.unitCells = []                         # die Zellen des Unit aus Sudoku.board
        else:
            self.unitCells = unitCells

    # gibt True zurück, wenn im Unit die number i bereits ausgefüllt ist, sonst False
    def contains(self, i):
        if self.numbersInUnit[i]:
            return True
        return False
    
    def removePointingOrReduction(self):
        raise NotImplementedError
    



    # -------------------------------------------------------------------------------------------
    # UPDATING UNITS

    # INITIAL
    # bringt die candidates der cells in unitCells auf den neusten Stand
    def setCandidatesInCells(self):
        for cell in self.unitCells:
            
            if cell.full:
                cell.candidatesCount = 0
                cell.candidates = np.zeros(9, dtype=bool)
                for i in range(9):
                    self.unitCells[i].candidates[cell.value - 1] = False
            else:
                for i in range(9):
                    if (cell.board.rows[cell.r].contains(i) or 
                        cell.board.cols[cell.c].contains(i)) or self.contains(i):
                        # print("cell ", cell.r, ", ", cell.c, " contains ", i, "in the row/col")
                        cell.candidatesCount -= 1
                        cell.candidates[i] = False
            # print("updating cell ", cell.r, ", ", cell.c, ": ", np.where(cell.candidates)[0]+1, ", ", cell.candidatesCount, ", ", cell.full)
            
    # UPDATE        
    # bringt numbersInUnit und numbersCount auf den neusten Stand
    def setNumbersInUnit(self):
        number = 0
        for cell in self.unitCells:
            if cell.full:
                number += 1
                self.numbersInUnit[cell.value - 1] = True
        self.numbersCount = number


    # bringt candidatesInUnit auf den neusten Stand
    def updateCandidatesInUnit(self):
        canInUnit = np.zeros(9)
        for i in range(9):
            for cell in self.unitCells:
                if cell.candidates[i]:
                    canInUnit[i] += 1
        self.candidatesInUnit = canInUnit





    # -------------------------------------------------------------------------------------------
    # FINDING SINGLES

    # gibt einen Array mit der Zahl und ein Array aller Zellen in der Unit zurück, die nur einen einzigen Kandidaten haben und noch nicht ausgefüllt wurden
    def hasSingleCell(self):
        numArr = []
        cellArr = []
        for idx, cell in enumerate(self.unitCells):
            if not cell.full and cell.candidatesCount == 1:
                # print(cell.r, ", ", cell.c, ", ", np.where(cell.candidates)[0]+1)
                numArr.append(int(np.where(cell.candidates)[0][0] + 1))
                cellArr.append(cell) 
            
        return numArr, cellArr
    
    # gibt alle Zahlen zurück, die nur in einer einzigen Zelle der Unit als Kandidat vorkommen und dort noch nicht ausgefüllt wurden
    def hasSingleNumber(self):
        numArr = []
        cellArr = []
        for i in range(9):
            if self.candidatesInUnit[i] == 1 and not (cell := self.findCandidateInUnit(i)[0]).full:
                numArr.append(i+1) 
                cellArr.append(cell) 
        return numArr, cellArr
    

    
    # -------------------------------------------------------------------------------------------
    # REMOVING DOUBLES

    # findet Paare von Zellen in einem Unit, die beide die gleichen 2 Kandidaten haben und löscht diese Kandidaten von allen anderen Zellen im Unit
    # returned True, wenn ein Kandidat eliminiert werden konnte, sonst False
    def removeObviousPair(self):

        typ = "_"
        num = -1
        if isinstance(self, Row):
            typ = "row"
            num = self.unitCells[0].r 
        elif isinstance(self, Col):
            typ = "col"
            num = self.unitCells[0].c
        elif isinstance(self, Block):
            typ = "block"
            num = self.unitCells[0].b
        else:
            print("komisch :((")



        flag = False        
        for idx, cell in enumerate(self.unitCells):
            if cell.candidatesCount == 2:
                for i in range(idx+1, 9):
                    if (self.unitCells[i].candidates == cell.candidates).all():
                        # print("Obvious Pair in ", typ, num, "from cells ", cell.r, ", ", cell.c, " and ", self.unitCells[i].r, ", ", self.unitCells[i].c, " with candidates ", np.where(cell.candidates)[0]+1)
                        flag |= self.removeCandidatesInOtherCells(cell.candidates, [cell, self.unitCells[i]]) 
        return flag
    

    # findet Paare von Kandidaten, die nur in 2 gleichen Zellen vorkommen und löscht diese Kandidaten von allen anderen Zellen
    # returned True, wenn ein Kandidat eliminiert werden konnte, sonst False
    def removeHiddenPair(self):

        typ = "_"
        num = -1
        if isinstance(self, Row):
            typ = "row"
            num = self.unitCells[0].r 
        elif isinstance(self, Col):
            typ = "col"
            num = self.unitCells[0].c
        elif isinstance(self, Block):
            typ = "block"
            num = self.unitCells[0].b
        else:
            print("komisch :((")

        
        flag = False
        candids = np.where(self.candidatesInUnit == 2)[0]
        for i, j in it.combinations(candids, 2):
            
            if (candCells := self.findCandidateInUnit(i)) == self.findCandidateInUnit(j):
                # print("Hidden Pair in ", typ, num, "from cells ", candCells[0].r, ", ", candCells[0].c, " and ", candCells[1].r, ", ", candCells[1].c, " with candidates ", i+1, ", ", j+1)
                
                # entferne andere Kandidaten in diesen 2 Zellen
                for cell in candCells:
                    toRemove = np.where(cell.candidates & ~((np.arange(9) == i) | (np.arange(9) == j)))[0]
                    for candToRemove in toRemove:
                        cell.removeCandidate(candToRemove)

                # entferne diese Kandidaten in anderen Zellen
                flag |= self.removeCandidatesInOtherCells(cell.candidates, candCells) 

        return flag
    
    
    
    
   

    
    # -------------------------------------------------------------------------------------------
    # REMOVING CANDIDATES FROM OTHER CELLS
    
    # entfernt die Kandidaten von allen anderen Zellen des units
    # returned True, wenn ein Kandidat eliminiert werden konnte, sonst False
    # numArr ist ein 9er-bool Array, cellArr ein Array, der nur die cell-objekte beinhaltet, bei denen NICHT die Kandidaten entfernt werden sollen
    def removeCandidatesInOtherCells(self, numArr, cellArr):
        flag = False
        for idx, cell in enumerate(self.unitCells):
            if not cell.full and cell not in cellArr:

                # filtert die Kandidaten raus, die gelöscht werden müssen und auch Kandidaten sind
                toRemove = np.where(cell.candidates & numArr)[0]
                if toRemove.size > 0:
                    
                    oldCandidates = cell.candidates             # nur für printstatement relevant

                    for candToRemove in toRemove:
                        cell.removeCandidate(candToRemove)
                    flag = True

                    # print("removing ", toRemove+1, "from cell ", cell.r, ", ", cell.c)
 
        return flag    


        
    # -------------------------------------------------------------------------------------------
    # FINDING MINI ROW's AND COL's

    # gibt True zurück, wenn in der i-ten (0,1,2) Reihe (Länge 3) eines Blocks der Kandidat candidate befindet
    # kann auch für Reihen oder Spalten verwendet werden, also wenn der i-te Abschnitt einer Reihe/Spalte den Kandidaten enthält
    def miniRow(self, candidate, i):
        return np.any([cell.candidates[candidate] for cell in self.unitCells[i*3:i*3+3]])
    
    # gibt True zurück, wenn in der i-ten (0,1,2) Spalte (Länge 3) eines Blocks der Kandidat candidate befindet
    def miniCol(self, candidate, i):
        return np.any([cell.candidates[candidate] for cell in self.unitCells[i::3]])
    


    # -------------------------------------------------------------------------------------------
    # FINDING CANDIDATES IN UNIT

    # gibt ein array mit allen Zellen, die den Kandidaten i enthalten und nicht ausgefüllt sind zurück
    def findCandidateInUnit(self, i):
        canArr = []
        for idx, cell in enumerate(self.unitCells):
            if not cell.full and cell.candidates[i]:
                canArr.append(cell)

        return canArr
    



# -------------------------------------------------------------------------------------------
# CLASSES
# -------------------------------------------------------------------------------------------



class Row(Unit):
    def __init__(self, unitCells=None):
        super().__init__(unitCells)


    def removePointingOrReduction(self):
        self.removeBlockLineRow()

    # schaut ob in einer Reihe die Kandidaten einer Zahl nur in einem Block vorkommen
    # in diesem Fall werden alle Kandidaten der selben Zahl im gleichen Block aber in einer anderen Reihe gelöscht
    def removeBlockLineRow(self):
        flag = False

        for cand in range(9):
            if not self.numbersInUnit[cand] and self.candidatesInUnit[cand] < 4:
                # print("row ", self.unitCells[0].r, ", candidate ", cand+1)
                for i in range(3):
                    if self.miniRow(cand, i) and (not self.miniRow(cand, (i+1)%3) and not self.miniRow(cand, (i+2)%3)):
                        cell = self.unitCells[i*3]
                        block = cell.board.blocks[cell.b]
                        numArr = np.arange(9) == cand
                        h = cell.r % 3
                        cellArr = block.unitCells[h*3:h*3+3]
                        # print("Block Line Reduction in block", cell.b, " apart form row ", h, " with candidate ", cand+1)
                        flag |= Unit.removeCandidatesInOtherCells(block, numArr, cellArr) 
        return flag
    


# -------------------------------------------------------------------------------------------



class Col(Unit):
    def __init__(self, unitCells=None):
        super().__init__(unitCells)

    def removePointingOrReduction(self):
        self.removeBlockLineCol()


    # schaut ob in einer Spalte die Kandidaten einer Zahl nur in einem Block vorkommen
    # in diesem Fall werden alle Kandidaten der selben Zahl im gleichen Block aber in einer anderen Spalte gelöscht
    def removeBlockLineCol(self):
        flag = False

        for cand in range(9):
            if not self.numbersInUnit[cand] and self.candidatesInUnit[cand] < 4:
                # print("-- col ", self.unitCells[0].c, ", candidate ", cand+1, self.miniRow(cand, 0), self.miniRow(cand, 1), self.miniRow(cand, 2))
                for i in range(3):
                    if self.miniRow(cand, i) and (not self.miniRow(cand, (i+1)%3) and not self.miniRow(cand, (i+2)%3)):
                        cell = self.unitCells[i*3]
                        block = cell.board.blocks[cell.b]
                        numArr = np.arange(9) == cand
                        h = cell.c % 3
                        cellArr = block.unitCells[h::3]
                        # print("Block Line Reduction in block", cell.b, " apart form col ", h, " with candidate ", cand+1)
                        flag |= Unit.removeCandidatesInOtherCells(block, numArr, cellArr) 
        return flag




# -------------------------------------------------------------------------------------------


class Block(Unit):
    def __init__(self, unitCells=None):
        super().__init__(unitCells)

    def removePointingOrReduction(self):
        self.removePointings()
    
    # schaut ob in einem block die Kandidaten einer Zahl sich nur in einer der 3 Reihen oder Spalten befinden. 
    # in diesem Fall werden die Kandidaten der gleichen Reihe/ Spalte aus anderen Blocks gelöscht
    # nur für blocks
    def removePointings(self):
        flag = False 

        for cand in range(9):
            if not self.numbersInUnit[cand] and self.candidatesInUnit[cand] < 4:
                for i in range(3):
                    #rows
                    if self.miniRow(cand, i) and (not self.miniRow(cand, (i+1)%3) and not self.miniRow(cand, (i+2)%3)):
                        cell = self.unitCells[i*3]
                        row = cell.board.rows[cell.r]
                        numArr = np.arange(9) == cand
                        h = cell.c // 3
                        cellArr = row.unitCells[h*3:h*3+3]
                        # print("Pointings in row", cell.r, " apart form part ", h + 1, " with candidate ", cand+1)
                        flag |= Unit.removeCandidatesInOtherCells(row, numArr, cellArr) 
                        



                    #cols
                    if self.miniCol(cand, i) and (not self.miniCol(cand, (i+1)%3) and not self.miniCol(cand, (i+2)%3)):
                        cell = self.unitCells[i]
                        col = cell.board.cols[cell.c]
                        numArr = np.arange(9) == cand
                        h = cell.r // 3
                        cellArr = col.unitCells[h*3:h*3+3]
                        # print("Pointings in col", cell.c, " apart from part ", h + 1, " with candidate ", cand+1)
                        flag |= Unit.removeCandidatesInOtherCells(col, numArr, cellArr) 


        return flag
    



    @staticmethod
    def findBlock(r, c):
        i = r // 3
        j = c // 3
        return i * 3 + j 
    













    # hinzuzufügen:
    # obvious triples
    # hidden triples


    