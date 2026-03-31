#include <stdio.h>
#include <stdlib.h>

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

int* get_possible_grid(int* grid) {
    // save the possible entries using bitwise encoding
    int* poss = (int *)malloc(81 * sizeof(int));
    
    // at first everything is possible
    for (int i = 0; i < 81; i++) {
        poss[i] = 1022; // 0b1111111110
    }

    for (int i = 0; i < 81; i++) {
        if (grid[i] == 0) continue;
        poss[i] = 1022; // 0b1111111110
    }


}






int main(int argc, char *argv[]) {
    if (argc < 4) {
        fprintf(stderr, "Usage: %s <path> <n> <version>\n", argv[0]);
        return 1;
    }

    char *path = argv[1];
    int n = atoi(argv[2]);
    int version = atoi(argv[3]);

    printf("path: %s\n", path);
    printf("n: %d\n", n);
    printf("version: %d\n", version);

    return 0;
}
