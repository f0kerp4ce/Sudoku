//#include <cstddef>
#include <stdio.h>
#include <stdlib.h>
#include <limits.h>

#define Only_one_bit_set(b) (b && !(b & (b - 1)))


int* read_sudoku(const char* path) {
    int* board = (int *)malloc(81 * sizeof(int));
    if (!board) {
        fprintf(stderr, "Memory allocation failed\n");
        return NULL;
    }

    FILE* file = fopen(path, "r");
    if (!file) {
        fprintf(stderr, "Error opening file: %s\n", path);
        free(board);
        return NULL;
    }

    int idx = 0;
    int c;
    while ((c = fgetc(file)) != EOF && idx < 81) {
        if (c >= '1' && c <= '9') {
            board[idx++] = c - '0';
        } else if (c == '.') {
            board[idx++] = 0;
        }
    }

    fclose(file);

    if (idx != 81) {
        fprintf(stderr, "Warning: Expected 81 cells, got %d\n", idx);
    }

    return board;
}

void get_row(int* grid, int i, int* row) {
    for (int j = 0; j<9; j++) {
        row[j] = grid[i*9 + j];
    }
}

void get_column(int* grid, int i, int* column) {
    for (int j = 0; j<9; j++) {
        column[j] = grid[j*9 + i];
    }
}

void get_block(int* grid, int i, int j, int* block) {
    int ri = (i/3)*3;
    int cj = (j/3)*3;
    for (int k = 0; k<9; k++) {
        block[k] = grid[9*(ri + (k/3)) + (cj + (k%3))];
    }
}

int* get_possible_grid(int* grid) {
    // save the possible entries using bitwise encoding
    int* poss = (int *)malloc(81 * sizeof(int));
    
    
    int possij;
    int ri;
    int ci;
    int row[9];
    int col[9];
    int block[9];
    for (int i = 0; i < 81; i++) {
        if (grid[i] != 0) continue;
        // at first everything is possible
        possij = 1022; // 0b1111111110
        ri = i/9;
        ci = i%9;
        get_row(grid, ri, row);
        get_column(grid, ci, col);
        get_block(grid, ri, ci, block);

        for (int j = 0; j < 9; j++) {
            possij &= !(1 << row[j]) & !(1<<col[j]) & !(1<<block[j]);
        }
        poss[i] = possij;
    }
    return poss;
}

int check(int* grid) { // check the sudoku (very slow)
    int* poss = get_possible_grid(grid);
    int sol = 0;
    for (int i = 0; i<81; i++) {
        sol |= poss[i];
    }
    return !sol;
}

void copy(int* original, int* buffer) {
    for (int i = 0; i<81; i++) {
        buffer[i] = original[i];
    }
}

void set(int* grid, int* possible, int i, int j, int new) {
    // &= for every cell in the row, col, block
    int ri = (i/3)*3;
    int cj = (j/3)*3;
    int mask = !(1<<new);
    for (int k = 0; k<9; k++) {
        // row
        possible[9*i + k] &= mask;
        // col
        possible[k*9 + j] &= mask;
        // block
        possible[9*(ri + k/3) + (cj + k%3)] &= mask;
    }
    grid[9*i+j] = new;
    possible[9*i+j] = 0; // (remove mask)
}

int _solve(int* grid) {
    int* possible = get_possible_grid(grid);

    int b, nbits, which;
    int least_possible = 10;
    int lpidx = -1;

    for (int i = 0; i<81; i++) {
        if (grid[i] != 0) continue;
        b = possible[i];
        if (b == 0) { // this branch is doomed
            return -1;
        }
        if (Only_one_bit_set(b)) {
            which = sizeof(int) * CHAR_BIT - __builtin_clz(b) - 1; // find out which bit was set
            set(grid, possible, i/9, i%9, which);
            i = -1; // reset the loop and stay in this frame
            continue;
        }
        nbits = __builtin_popcount(b); // intrinsic to count bits set
        if (nbits < least_possible) {
            least_possible = nbits;
            lpidx = i;
        }
    }
    // we have found the least number of bits, now recurse
    b = possible[lpidx];
    for (int i = 0; i<9; i++) {
        which = sizeof(int) * CHAR_BIT - __builtin_clz(b) - 1;
        grid[lpidx] = which;
        copy(grid, possible); // possible is not used anymore => use it to copy
        int sol = _solve(possible);
        if (sol == 0) {
            // copy the solution into the old grid
            copy(possible, grid);
            return 0;
        }
        // delete this sol
        b ^= (1<<which);
    }
    return -1; // no solution found
}

int* solve(char* path) {
    int* grid = read_sudoku(path);
    _solve(grid);
    return grid;
}

void pretty_print_sol(int* sol) {
    printf("SOLUTION:");
    for (int i = 0; i<81; i++) {
        printf("%d", sol[i]); // print one by one without a newline
    }
    printf("\n");
}


int main(int argc, char *argv[]) {
    if (argc < 4) {
        fprintf(stderr, "Usage: %s <path> <n> <version>\n", argv[0]);
        return 1;
    }

    char* path = argv[1];
    int n = atoi(argv[2]);
    int version = atoi(argv[3]);

    printf("path: %s\n", path);
    printf("n: %d\n", n);
    printf("version: %d\n", version);

    int* sol = solve(path);
    int succ = check(sol);


    // todo
    printf("LANGUAGE:C\n");
    pretty_print_sol(sol);
    printf("MEAN_TIME_NS: %d\n", version);

    return 0;
}
