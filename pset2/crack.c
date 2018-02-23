#include <cs50.h>
#include <stdio.h>
#include <string.h>
#include <crypt.h>
#include <math.h>
#define _XOPEN_SOURCE
#include <unistd.h>

int main(int argc, string argv[])
{
    if(argc == 2)
    {
        string hashed_pw = argv[1];

        char pw[] = "xxxx"; //arbitrarily initialize

        const char salt[] = {hashed_pw[0], hashed_pw[1]};

//now, go through all possible interations of upper and lower case letters arranged in
//a four letter sequence, and then hash that number

        for(long int i = 0; i < 52 * 52 * 52 * 52; i++)
        {
            //here, i is our 'seed' and now we compute an integer for each letter in
            //the four letter sequence, representing an applicable upper or lower
            //case letter

            for(int j = 0; j < 4; j++)
            {
                //pw_integer_format[j] = get_new_pw(i, j);
                if(((i / (int) pow((double) 52, (double) j)) % 52) < 26) //treat as lower case
                {
                    pw[j] = ((i / (int) pow((double) 52, (double) j)) % 52) + 97;
                }
                else
                {
                    pw[j] = ((i / (int) pow((double) 52, (double) j)) % 52) - 26 + 65; //reset to 0 by subtracting 26
                }
            }

            string new_hashed_pw = crypt(pw, salt);

            if(strcmp(new_hashed_pw, hashed_pw) == 0){
                printf("%s\n", pw);
                return 0;
            }
        }
    }
    else //if number of arguments is not 2
    {
        printf("Error: wrong number of arguments\n");
        return 1;
    }
}