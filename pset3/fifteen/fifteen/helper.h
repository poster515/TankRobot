#include <cs50.h>
#include <stdio.h>
#include <stdlib.h>
// #include <unistd.h>

// prototypes
void clear(void);
void greet(void);
// void init(int d, int array[d][d], int zero[]);
// void draw(int d, int array[d][d], int zero[]);
// bool move(int tile, int d, int array[d][d], int zero[]);
// bool won(int d, int array[d][d]);
// void update(int code, int zero[], int d, int board[d][d]);

void init(int d, int array[d][d]);
void draw(int d, int array[d][d]);
bool move(int tile, int d, int array[d][d]);
bool won(int d, int array[d][d]);
void update(int code, int d, int board[d][d]); //LAST WORKING COPY

