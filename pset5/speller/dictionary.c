/**
 * Implements a dictionary's functionality.
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <ctype.h>

#include "dictionary.h"

// char *dict_local;
char alphabet[28] = "abcdefghijklmnopqrstuvwxyz'"; //should be of size 27 to store null terminator

typedef struct layer
{
    //the below is an int array, one value per symbol in the alphabet (plus ')
    // 0 = false, 1 = true exclusive, 2 = true inclusive (end of word or continuing of a word)
    int letter[27];

    //the following array contains pointers to another struct of this type, need to initialally nullify them
    struct layer *next[27];
}
layer;

layer * AddLayer (layer * main_layer, int i); //malloc's a new layer and returns address of that layer
layer * nullify (layer * main_layer, bool both); //nullifies all pointers and/or letters of layer
void deload(layer * l); //frees all malloc'ed memory space

layer * root_layer; //this is the only thing needing protection after we have malloc'ed it
layer * main_layer; //this is the working copy that will be changing throughout the code

int sz; //stores size of dictionary, in words
int last_match; //stores index for load() function, could have made this local instead

/**
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
            if(*(alphabet + i) == tolower(*(word + char_index))) //BOOM matched a letter
            {
                if(main_layer -> letter[i] == 0) //check if letter was recognized in current layer in dictionary
                {
                    return false; //if the corresponding layer letter is false, then the word was never in dictionary
                }
                else if(main_layer -> letter[i] == 1) //means that the letter is in middle of word
                {
                    char_index++;
                    if(main_layer -> next[i] != NULL && *(word + char_index) != '\0') //if there is a 'next' pointer, go there
                    {
                        main_layer = main_layer -> next[i];
                        break; //need to break out of for loop if we've found a match, need to read next char and begin new comparison
                    }
                    else if(main_layer -> next[i] != NULL && *(word + char_index) == '\0')
                    {
                        return false; //this letter was supposed to be mid-word, but the next char is a null term. return misspelled
                    }
                }
                else if(main_layer -> letter[i] == 2) //letter is the end of a word
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
    sz = 0;

    FILE *dict = NULL;
    if(dictionary != NULL)
    {
        dict = fopen(dictionary, "r");
        if(dict != NULL)
        {
            // printf("Succesfully opened dictionary: %s.\n", dictionary);
            // fclose(dict);
        }
    }

    root_layer = malloc(sizeof(struct layer));
    root_layer = nullify(root_layer, true);
    main_layer = root_layer; //give main_layer the address of root_layer, anytime we modify ML, we also modify RL

    char *read_char = malloc(sizeof(char));

    layer *temp_layer;

    while(fread(read_char, 1, 1, dict) > 0) //grab a single byte aka char at a time
    {
        for(int i = 0; i < 27; i++)
        {
            if(*(alphabet + i) == *read_char)
            {
                if(main_layer -> letter[i] == 0)
                    main_layer -> letter[i] = 1; //just maintain a >=1 value
                temp_layer = main_layer;
                main_layer = AddLayer(main_layer, i); //go to the next layer
                last_match = i;
                break; //don't need to be in this loop if we've found the right letter
            }
            else if(*read_char == '\0' || *read_char == '\n') //else: if the character is not in the alphabet (i.e., a null terminator or return char)
            {
                sz++;
                free(temp_layer -> next[last_match]); //since we've malloc'ed unnecessary space, need to free it
                temp_layer -> next[last_match] = NULL; //nullify just to be sure
                temp_layer -> letter[last_match] = 2; //set to 2 to let the program know it is the end of the word
                main_layer = root_layer; //pass back the original root layer address
                break;
            }
        }
    }
        free(read_char); //don't need read_char anymore, free that space
        fclose(dict);
        return true;
}

/**
 * Returns number of words in dictionary if loaded else 0 if not yet loaded.
 */
unsigned int size(void)
{
    return sz; //already obtained this value from load()
}

/**
 * Unloads dictionary from memory. Returns true if successful else false.
 */
bool unload(void)
{
    main_layer = root_layer;
    deload(main_layer);
    free(root_layer);
    return true;
}

layer * AddLayer (layer * main_layer, int letter_position) {

    layer * lp = main_layer;

    if (lp != NULL) //quick sanity check
    {
        if(lp -> next[letter_position] == NULL)
        {
    	    lp -> next[letter_position] = (struct layer *) malloc (sizeof (layer));
            nullify(lp -> next[letter_position], true); //need to nullify to ensure deterministic behavior
        }
    	lp = lp -> next[letter_position];
    	return lp;
    }
    else //should never have to enter this loop but just in case...
    {
    	lp = (struct layer *) malloc (sizeof (layer));
    	return lp;
    }
}

layer * nullify (layer * main_layer, bool both) //should be fairly self-explanatory
{
    layer * lp = main_layer;

    for(int i = 0; i < 27; i++)
    {
        if(both)
        {
            lp->letter[i] = 0;
        }
        lp->next[i] = NULL;
    }
    return lp;
}

void deload(layer * l)
{
    layer * pl;
    layer * ml = l;

    for(int i = 0; i < 27; i++)
    {
        if(ml -> letter[i] > 0 && ml -> next[i] != NULL) //aka, have another layer after this one
        {
            pl = ml; //temporarily store pointer in pl
            ml = ml -> next[i]; //go to new address
            deload(ml); //recursively execution
            ml = pl; //go back to original layer
            free(pl -> next[i]); //free that space
        }
    }
}