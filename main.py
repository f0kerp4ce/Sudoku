import numpy as np
import time
from sudoku.board import Sudoku


def read_sudoku():
    print("Enter the Sudoku row by row.") 
    grid = np.zeros((9, 9), dtype=int) 
    for r in range(9): 
        while True: 
            row_input = input(f"Row {r+1}: ") 
            
            if len(row_input) != 9: 
                print("Error: Row must contain exactly 9 digits.") 
                continue 
            if not row_input.isdigit(): 
                print("Error: Only digits (0–9) are allowed.") 
                continue 
            grid[r] = np.array([int(c) for c in row_input]) 
            break 
        
    return grid


def main():
    

    # play = Sudoku()

    # play.board = read_sudoku()

    # start = time.perf_counter()

    # play.solveSudoku() 

    # end = time.perf_counter()

    # print("time: ", end-start, "sec")

    sudokus = [".......52..497......16...47653....94.........79....21543...65......937..81.......",
               "1........96.8137....75......1342..9...........4..6183......85....9746.12........6",
               "..14..8...4..9.17......75.45..7........985........4..31.65......74.2..6...3..62..",
               "9...76...4........31...98..127.......6.....4.......712..18...67........3...54...8"]
    

    for idx, sudoku in enumerate(sudokus):
        board = np.array([
            [int(c) if c != '.' else 0 for c in sudoku[i:i+9]]
            for i in range(0, 81, 9)
        ])


        start = time.perf_counter()


        t = 10
        for i in range(t):
            play = Sudoku(board)
            play.solveSudoku()

        end = time.perf_counter()

        zeit = (end-start) / t

        print("solved Sudoku ", idx+1, " in ", zeit, "sec on average")














if __name__ == "__main__":
    main()


# print all candidates
# for row in Cells:
#     for cell in row:
#         print(cell.r, ", ", cell.c, ", ", np.where(cell.candidates)[0]+1, ", ", cell.candidatesCount)         

