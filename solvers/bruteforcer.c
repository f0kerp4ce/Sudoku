//#include <cstddef>
#include <bits/time.h>
#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include <time.h>

#define Only_one_bit_set(b) (b && !(b & (b - 1)))

// Globals to track used numbers in rows, columns, and blocks.
// Bit 'v' is 1 if number 'v' is already placed.
int row_mask[9] = {0};
int col_mask[9] = {0};
int box_mask[9] = {0};



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
        } else if (c == '.' || c == '0') {
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
        // if (grid[i] != 0) {
        //     poss[i] = 0;
        //     continue;
        // }
        // at first everything is possible
        possij = 1022; // 0b1111111110
        ri = i/9;
        ci = i%9;
        get_row(grid, ri, row);
        get_column(grid, ci, col);
        get_block(grid, ri, ci, block);

        for (int j = 0; j < 9; j++) {
            possij &= ~(1 << row[j]) & ~(1<<col[j]) & ~(1<<block[j]);
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
    free(poss);
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
    int mask = ~(1<<new);
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

void pretty_print_sol(int* sol) {
    for (int i = 0; i<81; i++) {
        printf("%d", sol[i]); // print one by one without a newline
    }
    printf("\n");
}

int _solve(int* grid) {
    // assume grid is free to be modified,
    // save the result of this iteration into grid
    int* possible = get_possible_grid(grid);

    int b, nbits, which;
    int least_possible = 10;
    int lpidx = -1;

    for (int i = 0; i<81; i++) {
        if (grid[i] != 0) continue;
        b = possible[i];
        if (b == 0) { // this branch is doomed
            free(possible);
            return -2;
        }
        if (Only_one_bit_set(b)) {
            which = __builtin_ctz(b); // find out which bit was set
            set(grid, possible, i/9, i%9, which);
            i = -1; // reset the loop and stay in this frame
            least_possible = 10;
            lpidx = -1; 
            continue;
        }
        nbits = __builtin_popcount(b); // intrinsic to count bits set
        if (nbits < least_possible) {
            least_possible = nbits;
            lpidx = i;
        }
    }
    if (lpidx == -1) {
        free(possible); // success
        return 0;
    }
    // we have found the least number of bits, now recurse
    b = possible[lpidx];
    while (b > 0) {
        which = __builtin_ctz(b); // which possibility to try
        grid[lpidx] = which;
        copy(grid, possible); // possible is not used anymore => use it to copy
        int sol = _solve(possible);
        if (sol == 0) {
            // copy the solution into the old grid
            copy(possible, grid);
            free(possible);
            return 0;
        }
        // delete this possibility
        b &= (b-1);
    }
    free(possible);
    return -1; // no solution found
}

int* solve(char* path) {
    int* grid = read_sudoku(path);
    int result = _solve(grid);
    return grid;
}

void get_possible_grid2(int* grid, int* poss) {
    // save the possible entries using bitwise encoding
    int possij;
    int ri;
    int ci;
    int row[9];
    int col[9];
    int block[9];
    for (int i = 0; i < 81; i++) {
        if (grid[i] != 0) {
            poss[i] = 0;
            continue;
        }
        // at first everything is possible
        possij = 1022; // 0b1111111110
        ri = i/9;
        ci = i%9;
        get_row(grid, ri, row);
        get_column(grid, ci, col);
        get_block(grid, ri, ci, block);

        for (int j = 0; j < 9; j++) {
            possij &= ~(1 << row[j]) & ~(1<<col[j]) & ~(1<<block[j]);
        }
        poss[i] = possij;
    }
}

int _solve2(int* grid) {
// assume grid is free to be modified,
    // save the result of this iteration into grid
    int possible[81];
    get_possible_grid2(grid, possible);

    int b, nbits, which;
    int least_possible = 10;
    int lpidx = -1;

    for (int i = 0; i<81; i++) {
        if (grid[i] != 0) continue;
        b = possible[i];
        if (b == 0) { // this branch is doomed
            return -2;
        }
        if (Only_one_bit_set(b)) {
            which = __builtin_ctz(b); // find out which bit was set
            set(grid, possible, i/9, i%9, which);
            i = -1; // reset the loop and stay in this frame
            least_possible = 10;
            lpidx = -1; 
            continue;
        }
        nbits = __builtin_popcount(b); // intrinsic to count bits set
        if (nbits < least_possible) {
            least_possible = nbits;
            lpidx = i;
        }
    }
    if (lpidx == -1) {
        return 0;
    }
    // we have found the least number of bits, now recurse
    b = possible[lpidx];
    while (b > 0) {
        which = __builtin_ctz(b); // which possibility to try
        grid[lpidx] = which;
        copy(grid, possible); // possible is not used anymore => use it to copy
        int sol = _solve2(possible);
        if (sol == 0) {
            // copy the solution into the old grid
            copy(possible, grid);
            return 0;
        }
        // delete this possibility
        b &= (b-1);
    }
    return -1; // no solution found
}


// Helper to get block index
static inline int get_box(int r, int c) {
    return (r / 3) * 3 + (c / 3);
}

// Initialize masks based on the starting grid
void init_masks(int* grid) {
    for (int i = 0; i < 9; i++) {
        row_mask[i] = 0; col_mask[i] = 0; box_mask[i] = 0;
    }
    for (int i = 0; i < 81; i++) {
        if (grid[i] != 0) {
            int r = i / 9;
            int c = i % 9;
            int v = grid[i];
            row_mask[r] |= (1 << v);
            col_mask[c] |= (1 << v);
            box_mask[get_box(r, c)] |= (1 << v);
        }
    }
}

int _solve_fast(int* grid) {
    int best_i = -1;
    int min_poss = 10;
    int best_mask = 0;

    // 1. Find the cell with the Minimum Remaining Values (MRV)
    for (int i = 0; i < 81; i++) {
        if (grid[i] == 0) {
            int r = i / 9;
            int c = i % 9;
            int b = get_box(r, c);
            
            // O(1) check for available numbers (Bits 1-9)
            int mask = ~(row_mask[r] | col_mask[c] | box_mask[b]) & 0x3FE;
            
            if (mask == 0) return -1; // Dead end, backtrack
            
            int nbits = __builtin_popcount(mask);
            if (nbits < min_poss) {
                min_poss = nbits;
                best_i = i;
                best_mask = mask;
                
                // Early exit: you can't beat 1 possibility
                if (nbits == 1) break; 
            }
        }
    }

    // If no empty cells were found, the puzzle is solved
    if (best_i == -1) return 0;

    int r = best_i / 9;
    int c = best_i % 9;
    int b = get_box(r, c);

    // 2. Try all possibilities for the best cell
    while (best_mask > 0) {
        int val = __builtin_ctz(best_mask); // Extract lowest set bit
        
        // Apply guess
        grid[best_i] = val;
        row_mask[r] |= (1 << val);
        col_mask[c] |= (1 << val);
        box_mask[b] |= (1 << val);

        // Recurse
        if (_solve_fast(grid) == 0) {
            return 0; // Success propagates up
        }

        // Undo guess (Backtrack)
        grid[best_i] = 0;
        row_mask[r] &= ~(1 << val);
        col_mask[c] &= ~(1 << val);
        box_mask[b] &= ~(1 << val);

        // Clear the tried bit
        best_mask &= (best_mask - 1); 
    }

    return -1; // No valid numbers worked, trigger backtrack
}

int _solve3(int* grid) {
    init_masks(grid);
    return _solve_fast(grid);
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

    int (*solver_ptr) (int* );
    if (version == 0) solver_ptr = &_solve;
    else solver_ptr = &_solve2;

    // correctness
    int* sol = solve(path);
    int succ = check(sol);

    // timing
    long long total_ns = 0;
    struct timespec start, end;
    int* grid = read_sudoku(path);
    int* grid_copy = malloc(81 * sizeof(int));
    for (int i = 0; i<n; i++) {
        // copy grid
        copy(grid, grid_copy);
        clock_gettime(CLOCK_MONOTONIC, &start);
        solver_ptr(grid_copy); // actual solving
        clock_gettime(CLOCK_MONOTONIC, &end);
        total_ns += ((end.tv_sec - start.tv_sec)*1000000000LL + end.tv_nsec - start.tv_nsec);

    }

    free(grid_copy);
    free(grid);

    // print results
    printf("LANGUAGE:C\n");
    printf("SOLUTION:"); pretty_print_sol(sol);
    printf((succ ? "SUCCESS:TRUE\n" : "SUCCESS:FALSE\n"));
    printf("MEAN_TIME_NS: %lld\n", total_ns/n);

    free(sol);
    return 0;
}
