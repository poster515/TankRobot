#include <cs50.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>

int main(void)
{
    string user_input = get_string();

    //need simple bool to know when to grab letter
    bool valid_to_get_letter = true;

    if(user_input != NULL)
    {
        for(int i = 0; i < strlen(user_input); i++)
        {
            if(user_input[i] != ' ' && valid_to_get_letter)
            {
                printf("%c", toupper(user_input[i]));

                //can't get next letter until we hit a space again
                valid_to_get_letter = false;
            }
            else if (user_input[i] == ' ')
            {
                valid_to_get_letter = true;
            }
        }
    }

    printf("\n");

}