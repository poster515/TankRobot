#include <stdio.h>
#include <cs50.h>

void pyramid(int size, int n);
void print_hashtag(int n);
void print_space(int size, int n);

int main(void)
{
    bool correct = true;
    while (correct){
        printf("Height: ");
        int size = get_int();
        if(size == 0)
        {
            correct = false;
        }
        else if(size == 1)
        {
            printf("#  #\n");
            correct = false;
        }
        else if(size > 1 && size < 24){
            for(int i = 1; i < size + 1; i++){
                pyramid(size, i); //here, i = row number
            }
            correct = false;
        }
        else if (size > 23){
           correct = true; //don't do anything really
        }
        else
            correct = true;
    }
}

void pyramid(int size, int n) //only dealing with size >= 2
{
    print_space(size, n);
    print_hashtag(n);
    printf("  ");
    print_hashtag(n);
    //print_space(size, n);
    printf("\n"); //need to go to next line after this
}

void print_hashtag(int n)
{
    for(int j = 0; j < n; j++){
        printf("#");
    }
}
void print_space(int size, int n)
{
    for(int i = 0; i < (size - n); i++){ //i = row number
        printf(" ");
    }
}
