/**
 * generate.c
 *
 * Generates pseudorandom numbers in [0,MAX), one per line.
 *
 * Usage: generate n [s]
 *
 * where n is number of pseudorandom numbers to print
 * and s is an optional seed
 */

#define _XOPEN_SOURCE

#include <cs50.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

// upper limit on range of integers that can be generated
#define LIMIT 65536

int main(int argc, string argv[])
{
    // need to verify that the command line argument count is correct
    if (argc != 2 && argc != 3)
    {
        printf("Usage: ./generate n [s]\n");
        return 1;
    }

    // use the 'atoi' function to grab the total # of desired random numbers
    int n = atoi(argv[1]);

    // if there was a third argument, grab it and seed the drand() function using srand()
    if (argc == 3)
    {
        srand48((long) atoi(argv[2]));
    }
    else
    {
        srand48((long) time(NULL));
    }

    // now, compute n number of random numbers. need to multiply by LIMIT to get actual
    // integers between 0 and LIMIT, vice 0 and 1.
    for (int i = 0; i < n; i++)
    {
        printf("%i", (int) (drand48() * LIMIT));
        printf("\n");
    }

    // success
    return 0;
}
