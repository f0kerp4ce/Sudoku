import numpy as np
import time
import sys

class Sudoku:
    def __init__(self):
        self.sudoku = np.zeros(81)
        self._solve_bruteforce.name = "Brute Forcer 3000"
        self._solve_bruteforce_v2.name = "Brute Forcer 4000"
        
    @staticmethod
    def fromArray(grid):
        s = Sudoku()
        s.sudoku = grid
        return s

    def __str__(self):
        return "\n".join("".join([str(self.sudoku[9*i + j]) for j in range(9)]) for i in range(9))

    @staticmethod
    def readSudoku(path):
        with open(path, mode = 'r') as f:
            content = f.read()
            intcontent = np.array(list(map(lambda c: 0 if c=='.' else int(c), content)))
        return intcontent


    @staticmethod
    def enterSudoku():
        print("Please enter your sudoku, where empty spaces are 0s.")
        intcontent = np.zeros(81)
        for i in range(9):
            row = input(f"Please enter the numbers in row {i + 1}: ")
            intcontent[(i*9):(i*9 + 9)] = list(map(lambda c: 0 if c=='.' else int(c), row))
        return intcontent


    @staticmethod
    def testSolver(solve, n = 20):
        t = Timer()
        sudokus = ["data/sudoku0.txt", "data/sudoku1.txt", "data/sudoku2.txt", "data/sudoku3.txt"]
        solved = 0
        total_time = 0.0
        for s in sudokus:
            grid = Sudoku.readSudoku(s)
            succ = Sudoku._solve_and_check(grid, solve)
            if succ: solved += 1
            t.start()
            for _ in range(n):
                solve(grid.copy())
            t.stop()
            succmsg = "Solved " + s + " successfully " + str(n) + " times in"
            othermsg = "Failed to solve " + s + " " + str(n) + " times in"
            msg = succmsg if succ else othermsg
            total_time += t.print(msg, ".")
        avg = total_time / n / len(sudokus)
        print(f"The solver '{solve.name}' got {float(solved)/len(sudokus)*100}% correct with an average time of {avg} seconds.")


    @staticmethod
    def testAllSolvers():
        n = 1
        Sudoku.testSolver(Sudoku._solve_bruteforce, n)
        Sudoku.testSolver(Sudoku._solve_bruteforce_v2, n)

    def _get_row(self, i):
        return self.sudoku[(i*9):(i*9 + 9)]

    def _get_column(self, j):
        return self.sudoku[j : 81 + j : 9]
    
    def _get_block(self, i, j):
        ri = (i//3) *3
        rj = (j//3) *3
        return [self.sudoku[(ri + ci)*9 + (rj + cj)] for ci in range(3) for cj in range(3)]

    def _specific_is_possible(self, x, i, j):
        # check in the row
        if not all([x != c for c in self._get_row(i)]): return False
        # check same column
        if not all([x != c for c in self._get_block(i, j)]): return False
        # check same block
        if not all([x != c for c in self._get_column(j)]): return False
        return True

    def _get_possible_for(self, i, j):
        return list(filter(lambda x: self._specific_is_possible(x, i, j), range(1, 10)))

    
    @staticmethod 
    def _solve_bruteforce(grid):
        # very naive: check for every possibility
        s = Sudoku.fromArray(grid)
        
        for i in range(81):
            if grid[i] == 0:
                possible = s._get_possible_for(i//9, i%9)
                if possible is None: return None
                for x in possible:
                    grid[i] = x
                    sol = Sudoku._solve_bruteforce(grid.copy())
                    if Sudoku._check(sol): return sol
                return None
        return grid
    
    @staticmethod 
    def _solve_bruteforce_v2(grid):
        s = Sudoku.fromArray(grid)
        possible_positions = []


        for i in range(81):
            if grid[i] == 0:
                ri, rj = i//9, i%9
                possible = s._get_possible_for(ri, rj)
                tup = (ri, rj, possible, len(possible))

                # quick cut off
                if len(possible) == 0: return None
                if len(possible) == 1:
                    index = 9*ri + rj
                    grid[index] = possible[0]
                    return Sudoku._solve_bruteforce_v2(grid)

                possible_positions.append(tup)
        

        if not possible_positions: 
            return grid
        
        tup = min(possible_positions, key=lambda x: x[3])
        ri, rj, p, _ = tup

        
        
        i = 9*ri + rj
        for x in p:
            grid[i] = x
            sol = Sudoku._solve_bruteforce_v2(grid.copy())
            if sol is not None:
                return sol
        
        return None
        
    @staticmethod
    def _check(grid):
        if grid is None: return False

        s = Sudoku.fromArray(grid)
        correct = True
        def _is_complete(l):
            return all(map(lambda x: x in l, range(1,10))) and 0 not in l
        
        # check all rows
        for i in range(9):
            correct &= _is_complete(s._get_row(i))
        if not correct: return False
        # check all columns
        for i in range(9):
            correct &= _is_complete(s._get_column(i))
        if not correct: return False
        # check all blocks
        for i in range(3):
            for j in range(3):
                correct &= _is_complete(s._get_block(i*3, j*3))

        return correct

    @staticmethod
    def _solve_and_check(grid, solve):
        return Sudoku._check(solve(grid))


class Timer:
    def start(self):
        self.start_time = time.perf_counter()

    def stop(self):
        self.stop_time = time.perf_counter()

    def print(self, msgbefore, msgafter):
        print(msgbefore, (self.stop_time - self.start_time), "seconds", msgafter)
        return (self.stop_time - self.start_time)

class BetterTimer:
    def start(self):
        self.start_time = time.perf_counter_ns()

    def stop(self):
        self.stop_time = time.perf_counter_ns()

    def get_time(self):
        return self.stop_time - self.start_time


def main():
    Sudoku.testAllSolvers()


if __name__ == "__main__" and len(sys.argv) == 1:
    main()
elif len(sys.argv) != 1:
    path = sys.argv[1]
    n = int(sys.argv[2])
    index = int(sys.argv[3])

    solvers = [Sudoku._solve_bruteforce, Sudoku._solve_bruteforce_v2]
    if index > len(solvers) or index < 0:
        print("ERROR:solver does not exist")
    solver = solvers[index]

    print(f"Loading: {path}")
    print(f"Running {solver.__name__} {n} times...")
    grid = Sudoku.readSudoku(path)
    
    result = solver(grid)
    times = []
    bt = BetterTimer()
    for i in range(n):
        grid_copy = grid.copy()
        bt.start()
        result = solver(grid_copy)
        bt.stop()
        times.append(bt.get_time())

    total_time = sum(times)
    times.sort()
    mean_time = times[n//2]

    print("LANGUAGE:PYTHON")
    print("SOLUTION:" + "".join(list(map(str, list(result)))))
    print("MEAN_TIME_NS:" + str(mean_time))
    print("AVG_TIME_NS:" + str(total_time//n))
    print("TOTAL_TIME_NS:" + str(total_time))