/**
 * Prompts user for as many as MAX values until EOF is reached,
 * then proceeds to search that "haystack" of values for given needle.
 *
 * Usage: ./find needle
 *
 * where needle is the value to find in a haystack of values
 */

#include <cs50.h>
#include <stdio.h>
#include <stdlib.h>

#include "helpers.h"
// #include "test_helper.h"

// maximum amount of hay
const int MAX = 1000;

int main(int argc, string argv[])
{
    // ensure proper usage
    if (argc != 2)
    {
        printf("Usage: ./find needle\n");
        return -1;
    }

    // remember needle
    int needle = atoi(argv[1]);

    // fill haystack
    int size;
    int values[MAX];

    //the below 'for' loop currently is used to initialize an array

    for (size = 0; size < MAX; size++)
    {
        // wait for hay until EOF
        // printf("haystack[%i] = ", size);

        // int straw = get_int();
        int straw;
        scanf("%d", &straw);
        if (straw == INT_MAX)
        {
            break;
        }

        // add hay to stack
        values[size] = straw;
        // printf("%i, %i\n", straw, size);
    }
    // printf("\n");

    // sort the haystack, if size > 0
    if(size > 0)
    {

        sort(values, size);

        // for(int i = 0; i < size; i++)
        // {
        //     printf("find array[%i]: %i\n", i, values[i]);
        // }

        // try to find needle in haystack
        if (search(needle, values, size))
        {
            printf("\nFound needle in haystack!\n");
            return 0;
        }
        else
        {
            printf("\nDidn't find needle in haystack.\n");
            return 1;
        }
    }
}