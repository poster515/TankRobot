/**
 * fifteen.c
 *
 * Implements Game of Fifteen (generalized to d x d).
 *
 * Usage: fifteen d
 *
 * whereby the board's dimensions are to be d x d,
 * where d must be in [DIM_MIN,DIM_MAX]
 *
 * Note that u//sleep is obsolete, but it offers more granularity than
 * //sleep and is simpler to use than nano//sleep; `man u//sleep` for more.
 */

#define _XOPEN_SOURCE 500

#include <cs50.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

// constants
#define DIM_MIN 3
#define DIM_MAX 9

// board
int board[DIM_MAX][DIM_MAX];

// dimensions
int d;

void clear(void);
void greet(void);
void init(void);
void draw(void);
bool move(int tile);
bool won(void);
void update(int code); //LAST WORKING COPY

int main(int argc, string argv[])
{
    // ensure proper usage
    if (argc != 2)
    {
        printf("Usage: fifteen d\n");
        return 1;
    }

    // ensure valid dimensions
    d = atoi(argv[1]);
    if (d < DIM_MIN || d > DIM_MAX)
    {
        printf("Board must be between %i x %i and %i x %i, inclusive.\n",
            DIM_MIN, DIM_MIN, DIM_MAX, DIM_MAX);
        return 2;
    }

    // open log
    FILE *file = fopen("log.txt", "w");
    if (file == NULL)
    {
        return 3;
    }

    // greet user with instructions
    greet();

    // initialize the board
    init();

    // accept moves until game is won
    while (true)
    {
        // clear the screen
        clear();

        // draw the current state of the board
        draw();

        // log the current state of the board (for testing)
        for (int i = 0; i < d; i++)
        {
            for (int j = 0; j < d; j++)
            {
                fprintf(file, "%i", board[i][j]);
                if (j < d - 1)
                {
                    fprintf(file, "|");
                }
            }
            fprintf(file, "\n");
        }
        fflush(file);

        // check for win
        if (won())
        {
            printf("ftw!\n");
            break;
        }

        // prompt for move
        printf("Tile to move: ");
        int tile = get_int();

        // quit if user inputs 0 (for testing)
        if (tile == 0)
        {
            break;
        }

        // log move (for testing)
        fprintf(file, "%i\n", tile);
        fflush(file);

        // move if possible, else report illegality
        if (!move(tile))
        {
            printf("\nIllegal move.\n");
            usleep(500000);
        }

        // sleep thread for animation's sake
        usleep(500000);
    }

    // close log
    fclose(file);

    // success
    return 0;
}


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
void init(void) //LAST WORKING COPY
{
    // TODO
    // int array[d][d];
    int max = (d * d) - 1; //e.g., 4x4 - 1 = 15

    for(int i = 0; i < d; i++)
    {
        for(int j = 0; j < d; j++)
        {
            board[i][j] = max - (d * i) - j;
        }
    }
    if(d % 2 == 0) //if d is even, # tiles is odd
    {
        board[d - 1][d - 3] = 1;
        board[d - 1][d - 2] = 2;
    }

    // zero[0] = d - 1;
    // zero[1] = d - 1;
    // array[d - 1][d - 1] = NULL;
}

/**
 * Prints the board in its current state.
 */
// void draw(int d, int array[d][d], int zero[])
void draw(void) //LAST WORKING COPY
{
    //

    int zero[2];

    for(int i = 0; i < d; i++)
    {
        for(int j = 0; j < d; j++)
        {
            if(board[i][j] != 0)
            {
                printf(" %i", board[i][j]);
            }
            else
                printf(" _");

            if(j < d - 1) //don't want a "|" for last element
            {
                if(board[i][j] > 100)
                {
                    //do nothing, all three digits filled
                    printf("|");
                }
                else if (board[i][j] > 10)
                {
                    //print a space
                    printf(" |");
                }
                else if (board[i][j] >= 0)
                {
                    //print two spaces
                    printf("  |");
                    if(board[i][j] == 0)
                    {
                        zero[0] = i;
                        zero[1] = j;
                    }
                }
            } //if j < d - 1

        } //j for loop
        printf("\n");
    }// i for loop
}

/**
 * If tile borders empty space, moves tile and returns true, else
 * returns false.
 */
// bool move(int tile, int d, int array[d][d], int zero[])
bool move(int tile) //LAST WORKING COPY
{
    // #define zero_to_the_left 0
    // #define zero_to_the_right 1
    // #define zero_on_top 2
    // #define zero_on_bottom 3

    int zero_to_the_left = 0;
    int zero_to_the_right = 1;
    int zero_on_top = 2;
    int zero_on_bottom = 3;

    int tile_location[2];
    int zero[2];

    for(int i = 0; i < d; i++){
        for(int j = 0; j < d; j++)
        {
            if(board[i][j] == 0)
            {
                zero[0] = i;
                zero[1] = j;
            }
        }
    }

    for(int i = 0; i < d; i++)
    {
        for(int j = 0; j < d; j++)
        {
            if(board[i][j] == tile)
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
            update(zero_on_top);
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
            update(zero_on_bottom);
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
            update(zero_to_the_left);
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
            update(zero_to_the_right);
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
bool won(void) //LAST WORKING COPY
{
    // TODO
    for(int i = 0; i < d; i++)
    {
        for(int j = 0; j < d; j++)
        {
            if(i == d - 1 && j == d - 1) //last block
            {
                if(board[i][j] != 0)
                    return false;
            }
            else if(board[i][j] != ((i * d) + j + 1))
            {
                return false;
            }
        }
    }
    return true;
}

void update(int code)
{
    // #define zero_to_the_left 0
    // #define zero_to_the_right 1
    // #define zero_on_top 2
    // #define zero_on_bottom 3

    int zero_i;
    int zero_j;
    int temp;

    for(int i = 0; i < d; i++){
        for(int j = 0; j < d; j++)
        {
            if(board[i][j] == 0)
            {
                zero_i = i;
                zero_j = j;
            }
        }
    }

    switch(code)
    {
        case 0:
        //give temp the location of the tile to move
            temp = board[zero_i][zero_j + 1];
            board[zero_i][zero_j + 1] = 0;
            board[zero_i][zero_j] = temp;
            // zero[0] = zero_i;
            // zero[1] = zero_j + 1;

            break;
        case 1:
            temp = board[zero_i][zero_j - 1];
            board[zero_i][zero_j - 1] = 0;
            board[zero_i][zero_j] = temp;

            // zero[0] = zero_i;
            // zero[1] = zero_j - 1;

            break;
        case 2:
            temp = board[zero_i + 1][zero_j];
            board[zero_i + 1][zero_j] = 0;
            board[zero_i][zero_j] = temp;

            // zero[0] = zero_i + 1;
            // zero[1] = zero_j;

            break;
        case 3:
            temp = board[zero_i - 1][zero_j];
            board[zero_i - 1][zero_j] = 0;
            board[zero_i][zero_j] = temp;

            // zero[0] = zero_i - 1;
            // zero[1] = zero_j;

            break;
    }
}
