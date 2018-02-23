/**
 * Implements a dictionary's functionality.
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#include "dictionary.h"

#define LONGEST_WORD 46

// char *dict_local;
char alphabet[28] = "abcdefghijklmnopqrstuvwxyz'"; //should be of size 27 to store null terminator
int last_index[45]; //each number here represents the last index in a particular layer to have been accessed

typedef struct layer
{
    //the following array contains 26 boolean values that represent each
    //of the 26 letters in the alphabet. they will 'true' when a particular
    //letter is detected in a word

    bool letter[27];
    //int letter[27]; //each element can be either 0 = false, 1 = true exclusive, 2 = true inclusive

    //the following array contains pointers to another struct of this type, need to initialally nullify them
    struct layer *next[27];
}
layer;

layer * AddLayer (layer * main_layer, int i);
layer * nullify (layer * main_layer, bool both);
void search(layer * ml, layer * pl);

layer * root_layer; //this is the only thing needing protection after we have malloc'ed it
layer * main_layer; //this is the working copy that will be changing throughout the code

int sz;

/*
 *Returns true if word is in dictionary else false.
 */
bool check(const char *word)
{
    int char_index = 0;
    main_layer = root_layer;

    while(*(word + char_index) != '\0' && char_index < 46)
    {
        for(int i = 0; i < 27; i++)
        {
            if(*(alphabet + i) == *(word + char_index)) //BOOM matched a letter
            {
                if(main_layer -> letter[i] == false) //check if letter was recognized in current layer in dictionary
                {
                    return false; //can just return true here, if the corresponding layer letter is false, then the word was never in
                                    //dictionary
                }
                else if(main_layer -> letter[i] == true)
                {
                    //go to next layer, and continue onward
                    char_index++;
                    if(main_layer -> next[i] != NULL && *(word + char_index) != '\0') //if there is a 'next' pointer, go there
                    {
                        main_layer = main_layer -> next[i];
                        break; //need to break out of for loop if we've found a match, need to read next char and begin new comparison
                    }
                    else if(main_layer -> next[i] != NULL && *(word + char_index) == '\0')
                    {
                        return true; //could end up here if the word has ended and we still have a valid pointer, return not misspelled
                    }
                    else if(main_layer -> next[i] == NULL && *(word + char_index) != '\0')
                    {
                        return false; //requested word is longer than that branch of dictionary, return misspelled
                    }
                    else if(main_layer -> next[i] == NULL && *(word + char_index) == '\0')
                    {
                        return true; //requested word is exact longest word in that branch of dictionary, return not misspelled
                    }
                }
            }
        }
    }
    return true; //if you make it out of the while loop, the word is spelled correctly. should have all cases covered in while loop.
}

/**
 * Loads dictionary into memory. Returns true if successful else false.
 */
bool load(const char *dictionary)
{
    // since each word ends in a null terminator, just keep reading until the
    //file pointer is null, checking for the null terminator
    FILE *dict = NULL;
    if(dictionary != NULL)
    {
        dict = fopen(dictionary, "r");
        if(dict != NULL)
        {
            printf("Succesfully opened dictionary: %s.\n", dictionary);
            // fclose(dict);
        }
        // return true;
    }

    // main_layer = NULL;
    root_layer = malloc(sizeof(struct layer));
    root_layer = nullify(root_layer, true);
    main_layer = root_layer; //give main_layer the address of root_layer, anytime we modify ML, we also modify RL

    char *read_char = malloc(sizeof(char));

    layer *temp_layer;
    int last_match;

    while(fread(read_char, 1, 1, dict) > 0) //grab a single byte aka char at a time
    {
        for(int i = 0; i < 27; i++)
        {
            if(*(alphabet + i) == *read_char)
            {
                //wouldn't even do this
                main_layer -> letter[i] = true;

                //do this instead:
                // if(main_layer -> letter[i] < 1) main_layer -> letter[i] = 1;
                temp_layer = main_layer;
                main_layer = AddLayer(main_layer, i);
                last_match = i;
                // printf("Match: alphabet[%i]: %c, read_char: %c.\n", i, *(alphabet + i), *read_char);
                break; //don't need to be in this loop if we've found the right letter
            }
            else if(*read_char == '\0' || *read_char == '\n') //else: if the character is not in the alphabet (i.e., a null terminator or return char)
            {
                free(temp_layer -> next[last_match]);
                temp_layer -> next[last_match] = NULL;
                // temp_layer -> letter[last_match]++;
                // main_layer = nullify(temp_layer, false); //just nullify the 'next' pointers
                main_layer = root_layer; //pass back the original root layer address
                // printf("End of string. alphabet[%i]: %c, read_char: %c.\n", i, *(alphabet + i), *read_char);
                break;
            }
        }
    }
         fclose(dict);
        return true;
}

/**
 * Returns number of words in dictionary if loaded else 0 if not yet loaded.
 */
unsigned int size(void)
{
    // main_layer = root_layer;

    // sz = 0;

    search(main_layer, main_layer);
    printf("Size of library is %i\n", sz);

    return sz;
}

/**
 * Unloads dictionary from memory. Returns true if successful else false.
 */
bool unload(void)
{
    // TODO
    return false;
}

layer * AddLayer (layer * main_layer, int letter_position) {

    layer * lp = main_layer;

    if (lp != NULL)
    {
        if(lp -> next[letter_position] == NULL)
        {
    	    lp -> next[letter_position] = (struct layer *) malloc (sizeof (layer));
        }
    	lp = lp -> next[letter_position];
    	return lp;
    }
    else //should never have to enter this loop but just in case...
    {
    	lp = (struct layer *) malloc (sizeof (layer));
    	lp -> letter[letter_position] = true;
    	return lp;
    }
}

layer * nullify (layer * main_layer, bool both)
{
    layer * lp = main_layer;

    for(int i = 0; i < 27; i++)
    {
        if(both)
        {
            lp->letter[i] = false;
        }
        lp->next[i] = NULL;
    }
    return lp;
}

void search(layer * ml, layer * pl)
{
    layer * current_layer = ml;
    layer * prev_layer = pl;

    int current_layer_index = 0;
    int for_loop_index = 0;

    for(int i = for_loop_index; i < 27; i++)
    {
        if(current_layer -> letter[i] && current_layer -> next[i] != NULL) //aka, have another layer after this one
        {
            //record current layer index
            last_index[current_layer_index] = i;

            //prepare current_layer to match next layer number
            current_layer_index++;

            //go to next layer and reset for_loop_index
            prev_layer = current_layer;
            current_layer = current_layer -> next[i];
            for_loop_index = 0;

        }
        else if(current_layer -> letter[i] && current_layer -> next[i] == NULL) //aka, last layer for this letter, increment sz
        {
            //increment sz
            sz++;
            if(i == 26)
            {
                if(current_layer_index != 0 && last_index[current_layer_index - 1] < 26)
                {
                    //go to previous layer
                    current_layer = prev_layer;
                    for_loop_index = last_index[current_layer_index - 1] + 1;
                    current_layer_index--;

                    //reset loop index
                    for_loop_index = 0;
                }
                else //here, we've swept the last element of the second-to-last layer, and the 0th layer last_index = 26, i.e., we're done
                {
                    return;
                }
            }
        }
        //need to find some way to exit this loop...
        else if(i == 26)
        {
            if(current_layer_index != 0 && last_index[current_layer_index - 1] < 26)
            {
                //go to previous layer
                current_layer = prev_layer;
                for_loop_index = last_index[current_layer_index - 1] + 1;
                current_layer_index--;

                //reset loop index
                for_loop_index = 0;
            }
            else //here, we've swept the last element of the second-to-last layer, and the 0th layer last_index = 26, i.e., we're done
            {
                return;
            }
        }
    }
}