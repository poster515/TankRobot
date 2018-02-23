#include <cs50.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>

int main(int argc, string argv[])
{
    bool valid_key = true;

    if(argc == 2)
    {
        string key = argv[1];

        for( int i = 0; i < strlen(key); i++)
        {
            if (!((key[i] >= 97 && key[i] <= 122) || (key[i] >= 65 && key[i] <= 90))) //these are ASCII letter codes
            {
                valid_key = false; //if not a letter (upper/lowercase), do not execute code
            }
        }

        if (valid_key)
        {
            printf("plaintext: ");
            string plaintext = get_string();

            printf("ciphertext: ");

            // 'A' and 'a' are 0, 'B' and 'b' are 1, ... , 'Z' and 'z' are 25
            // at this point we have the key, as an array of integers, and we have the plaintext to commutate

            for(int i = 0; i < strlen(plaintext); i++)
            {
                if(plaintext[i] >= 97 && plaintext[i] <= 122) //lowercase plaintext character
                {
                    printf("%c", (((plaintext[i] - 97) + (tolower(key[i % strlen(key)]) - 97)) % 26) + 97);

                }
                else if (plaintext[i] >= 65 && plaintext[i] <= 90) //uppercase plaintext character
                {
                    printf("%c", (((plaintext[i] - 65) + (tolower(key[i % strlen(key)]) - 97)) % 26) + 65);
                }
                else
                {
                    printf("%c", plaintext[i]); //else, leave output unchanged
                }
            }

            printf("\n");
            return 0;
        }
        else //if valid_key is false and the key is indeed invalid
        {
            printf("Error: key contains non-numeric characters\n");
            return 1;
        }

        return 0;
    }
    else //if number of arguments is not 2
    {
        printf("Error: wrong number of arguments\n");
        return 1;
    }
}