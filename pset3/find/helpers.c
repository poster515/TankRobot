/**
 * helpers.c
 *
 * Helper functions for Problem Set 3.
 */

#include <cs50.h>
#include <stdio.h>
#include <math.h>

#include "helpers.h"

#define MAX_LIMIT 65536 //just for the max # of values array can have

/**
 * Returns true if value is in array of n values, else false.
 */
bool search(int value, int values[], int n)
{
    if (value < 0)
    {
        printf("Search value is negative.\n");
        return false;
    }
    else
    {
        //debug only:
        // for(int l = 0; l < n; l++)
        // {
        //     printf("search array[%i]: %i\n", l, values[l]);
        // }
        int den_pow = 1;

        int numer = 1;

        bool valid_cont_search = true;
        int number_valid_searches = (int) ceil(log2(n));

        //debug only:
        // printf("number_valid_searches: %i || n = %i\n", number_valid_searches, n);

        do
        {
            int denom = (int) pow((double) 2, den_pow);

            int temp_search_value = values[(numer * n)/(2 * denom)];
            // printf("Searching...\n");
            // printf("index = %i || values[%i]: %i\n", (numer * n)/(2 * denom), (numer * n)/(2 * denom), temp_search_value);

            //now, compare this temp value to actual desired value
            if(value == temp_search_value)
            {
                //we're good!
                return true;
            }
            else if(number_valid_searches <= 0)
            {
                valid_cont_search = false;
            }
            //now check the lower half of the values
            else if(value < temp_search_value && valid_cont_search)
            {
                number_valid_searches--;
                numer = (numer * 2) - 1;
                den_pow++;

                //if numer is 1, we want to just keep that
                //the same and let denom increase

                // printf("desired value: %i, temp_search_value: %i\n", value, temp_search_value);
                // printf("number_valid_searches: %i || numer = %i || denom = %i\n", number_valid_searches, numer, denom);
            }
            else if(value > temp_search_value && valid_cont_search)
            {
                number_valid_searches--;
                numer = (numer * 2) + 1;
                den_pow++;

                // printf("desired value: %i, temp_search_value: %i\n", value, temp_search_value);
                // printf("number_valid_searches: %i || numer = %i || denom = %i\n", number_valid_searches, numer, denom);
            }

        } // do loop
        while(valid_cont_search);
    }
    return false;
}

// /**
//  * Sorts array of n values.
//  */
void sort(int values[], int n)
{
    int sorted_array[n];

    //pass first value to sorted array
    sorted_array[0] = values[0];

    for(int i = 1; i < n; i++)
    {
        int temp_unsorted_value = values[i]; //CONFIRMED that this is recieving array values properly

        //compare ith value to sorted array
        bool continue_sort = true;

        for(int j = 0; j < i; j++)
        {
            if(continue_sort)
            {
                if(temp_unsorted_value >= sorted_array[j] && j == i - 1)
                {
                    //do nothing unless we're at the last element
                    sorted_array[j + 1] = temp_unsorted_value;

                }
                else if(temp_unsorted_value < sorted_array[j])
                {
                    //shift entire array down

                    for(int k = i; k > j; k--)
                    {
                        sorted_array[k] = sorted_array[k - 1];
                    }
                    sorted_array[j] = temp_unsorted_value;

                    continue_sort = false;
                }
                else if(temp_unsorted_value > sorted_array[j] && j != i - 1)
                {
                    //don't need to do anything

                }
            } //if(continue_sort)
        }
    }
    //after sorting is all done, pass sorted_array back to 'values'
    //values = sorted_array;

    //debug only:
    for(int l = 0; l < n; l++)
    {
        values[l] = sorted_array[l];
        // printf("sort array[%i]: %i\n", l, values[l]);
    }
}
