
#define zero_to_the_left 0
#define zero_to_the_right 1
#define zero_on_top 2
#define zero_on_bottom 3

#include <cs50.h>
#include <stdio.h>
#include <stdlib.h>
// #include <unistd.h>

#include "helper.h"

int zero[2];
/**
 * Clears screen using ANSI escape sequences.
 */
// void update(int code, int zero[], int d, int board[d][d]);

void clear(void)
{
    printf("\033[2J");
    printf("\033[%d;%dH", 0, 0);
}

/**
 * Greets player.
 */
void greet(void)
{
    clear();
    printf("WELCOME TO GAME OF FIFTEEN\n");
    // sleep(1);
}

/**
 * Initializes the game's board with tiles numbered 1 through d*d - 1
 * (i.e., fills 2D array with values but does not actually print them).
 */
// void init(int d, int array[d][d], int zero[])
void init(int d, int array[d][d]) //LAST WORKING COPY
{
    // TODO
    // int array[d][d];
    int max = (d * d) - 1; //e.g., 4x4 - 1 = 15

    for(int i = 0; i < d; i++)
    {
        for(int j = 0; j < d; j++)
        {
            array[i][j] = max - (d * i) - j;
        }
    }
    if(d % 2 == 0) //if d is even, # tiles is odd
    {
        array[d - 1][d - 3] = 1;
        array[d - 1][d - 2] = 2;
    }
    zero[0] = d - 1;
    zero[1] = d - 1;
    // array[d - 1][d - 1] = NULL;
}

/**
 * Prints the board in its current state.
 */
// void draw(int d, int array[d][d], int zero[])
void draw(int d, int array[d][d]) //LAST WORKING COPY
{
    //
    for(int i = 0; i < d; i++)
    {
        for(int j = 0; j < d; j++)
        {
            if(array[i][j] != 0)
            {
                printf(" %i", array[i][j]);
            }
            else
                printf(" _");

            // if(j < d - 1) //don't want a "|" for last element
            // {
            //     if(array[i][j] > 100)
            //     {
            //         //do nothing, all three digits filled
            //         printf("|");
            //     }
            //     else if (array[i][j] > 10)
            //     {
            //         //print a space
            //         printf(" |");
            //     }
            //     else if (array[i][j] >= 0)
            //     {
            //         //print two spaces
            //         printf("  |");
            //         if(array[i][j] == 0)
            //         {
            //             zero[0] = i;
            //             zero[1] = j;
            //         }
            //     }
            // } //if j < d - 1

        } //j for loop
        printf("\n");
    }// i for loop
}

/**
 * If tile borders empty space, moves tile and returns true, else
 * returns false.
 */
// bool move(int tile, int d, int array[d][d], int zero[])
bool move(int tile, int d, int array[d][d]) //LAST WORKING COPY
{
    // #define zero_to_the_left 0
    // #define zero_to_the_right 1
    // #define zero_on_top 2
    // #define zero_on_bottom 3

    int tile_location[2];


    for(int i = 0; i < d; i++)
    {
        for(int j = 0; j < d; j++)
        {
            if(array[i][j] == tile)
            {
             tile_location[0] = i;
             tile_location[1] = j;
            }
        }
    }
    // printf("tile[0]: %i, tile[1]: %i, zero[]0: %i, zero[1]: %i\n",
    //         tile_location[0], tile_location[1], zero[0], zero[1]);
    // sleep(4);

    if(tile_location[0] - zero[0] == 1 &&
        tile_location[1] == zero[1])
    {
        // | zero |
        // | tile |
        //tile is 'below' zero, check for lower boundary
        if(zero[0] <= 2){
            update(zero_on_top, d, array);
            // printf("zero_on_top, zero[0]: %i, zero[1]: %i", zero[0], zero[1]);
            // sleep(4);
            return true;
        }
        else
        {
            // printf("on bottom boundary, zero[0]: %i, zero[1]: %i", zero[0], zero[1]);
            // sleep(4);
            return false;
        }
    }
    else if(zero[0] - tile_location[0] == 1 &&
        tile_location[1] == zero[1])
    {
        // | tile |
        // | zero |
        //tile is 'above' zero, check for upper boundary
        if(zero[0] >= 1){
            // update(zero_on_bottom, d, array); //LAST WROKING COPY
            update(zero_on_bottom, d, array);
            // printf("zero_on_bottom, zero[0]: %i, zero[1]: %i", zero[0], zero[1]);
            // sleep(4);
            return true;
        }
        else
        {
            // printf("on top boundary, zero[0]: %i, zero[1]: %i", zero[0], zero[1]);
            // sleep(4);
            return false;
        }
    }
    else if(tile_location[1] - zero[1] == 1 &&
        tile_location[0] == zero[0])
    {
        // | zero | tile |

        //tile is 'to the right of' zero, check for right boundary
        if(zero[1] <= 2){
            update(zero_to_the_left, d, array);
            // printf("zero_to_the_left, zero[0]: %i, zero[1]: %i", zero[0], zero[1]);
            // sleep(4);
            return true;
        }
        else
        {
            // printf("on right boundary, zero[0]: %i, zero[1]: %i", zero[0], zero[1]);
            // sleep(4);
            return false;
        }
    }

    else if(zero[1] - tile_location[1] == 1 &&
        tile_location[0] == zero[0])
    {
        // | tile | zero |

        //tile is 'to the right of' zero, check for right boundary
        if(zero[1] >= 1){
            update(zero_to_the_right, d, array);
            // printf("zero_to_the_right, zero[0]: %i, zero[1]: %i", zero[0], zero[1]);
            // sleep(4);
            return true;
        }
        else
        {
            // printf("on left boundary, zero[0]: %i, zero[1]: %i", zero[0], zero[1]);
            // sleep(4);
            return false;
        }
    }
    return false; //need this to account for random numbers chosen
                    //that aren't adjacent
}

/**
 * Returns true if game is won (i.e., board is in winning configuration),
 * else false.
 */
bool won(int d, int array[d][d]) //LAST WORKING COPY
{
    // TODO
    for(int i = 0; i < d; i++)
    {
        for(int j = 0; j < d; j++)
        {
            if(i == d - 1 && j == d - 1) //last block
            {
                if(array[i][j] != 0)
                    return false;
            }
            else if(array[i][j] != ((i * d) + j + 1))
            {
                return false;
            }
        }
    }
    return true;
}

void update(int code, int d, int board[d][d])
{
    // #define zero_to_the_left 0
    // #define zero_to_the_right 1
    // #define zero_on_top 2
    // #define zero_on_bottom 3
    int zero_i = zero[0];
    int zero_j = zero[1];
    int temp;

    switch(code)
    {
        case 0:
        //give temp the location of the tile to move
            temp = board[zero_i][zero_j + 1];
            board[zero_i][zero_j + 1] = 0;
            board[zero_i][zero_j] = temp;
            zero[0] = zero_i;
            zero[1] = zero_j + 1;

            break;
        case 1:
            temp = board[zero_i][zero_j - 1];
            board[zero_i][zero_j - 1] = 0;
            board[zero_i][zero_j] = temp;

            zero[0] = zero_i;
            zero[1] = zero_j - 1;

            break;
        case 2:
            temp = board[zero_i + 1][zero_j];
            board[zero_i + 1][zero_j] = 0;
            board[zero_i][zero_j] = temp;

            zero[0] = zero_i + 1;
            zero[1] = zero_j;

            break;
        case 3:
            temp = board[zero_i - 1][zero_j];
            board[zero_i - 1][zero_j] = 0;
            board[zero_i][zero_j] = temp;

            zero[0] = zero_i - 1;
            zero[1] = zero_j;

            break;
    }
}
