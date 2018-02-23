#include <stdio.h>
#include <cs50.h>
#include <math.h>

bool check_validity(long long card);
bool check_AMEX(long long card);
bool check_VISA(long long card);
bool check_MASTCARD(long long card);
int get_sum(long long card);

int main(void)
{
    printf("Number: ");
    long long card = get_long_long();
    //TODO: check for non-integers
    bool correct = check_validity(card);
    if(correct){
        if(check_AMEX(card))
            printf("AMEX\n");
        else if(check_VISA(card))
            printf("VISA\n");
        else if(check_MASTCARD(card))
            printf("MASTERCARD\n");
        else
            printf("Unknown card type.\n");
    }
    else
    {
        printf("INVALID\n");
    }
}

bool check_validity(long long card)
{
    int sum = 0;
    int i = 1;
    bool size_is_OK = true;

    while (size_is_OK){

        if( card > (long long) pow((double) 10, (double) i)){
            int partial_sum = ((card / ((long long) pow((double) 10, (double) i))) % 10) * 2;
            if(partial_sum > 9)
            {
                sum = sum + 1 + (partial_sum % 10);
            }
            else
            {
                sum += ((card / ((long long) pow((double) 10, (double) i))) % 10) * 2;
            }
            //printf("Multiplier: %i\n", ((int) pow((double) 10, (double) i)));
            //printf("Sum: %i\n", sum);
            i += 2;
        }
        else{
            size_is_OK = false;
        }
    }
    //printf("Sum: %i\n", sum);
    //size_is_OK is false at this point
    size_is_OK = true;

    //need to grab every other digit now, set i to 0
    i = 0;

    while (size_is_OK){

        if( card > ((long long) pow((double) 10, (double) i))){
            sum += ((card / ((long long) pow((double) 10, (double) i))) % 10);
            i += 2;
        }
        else{
            size_is_OK = false;
        }
    }
    //comment the below line after debug
    //printf("New sum: %i\n", sum);

    if (sum % 10 == 0){
        //printf("Number is valid!\n");
        return true;    //card number is valid
    }
    else{
        //printf("Number is not valid. :(");
        return false;
    }
}

bool check_AMEX(long long card)
{
    int sum = get_sum(card);
    if(sum == 37 || sum == 34)
    {
        return true;
    }
    else
        return false;

}

bool check_VISA(long long card)
{
    int sum = get_sum(card);
    if((sum / 10) == 4)
    {
        return true;
    }
    else
        return false;

}

bool check_MASTCARD(long long card)
{
    int sum = get_sum(card);
    if(sum == 51 || sum == 52 || sum == 53 || sum == 54 || sum == 55)
    {
        return true;
    }
    else
        return false;

}
int get_sum(long long card)
{
    int i = 0;

    while(((long long) pow((double) 10, (double) i)) < card)
    {
        i++;
    }
    int last_two_digits = (card / ((long long) pow((double) 10, (double) (i - 2)))); //should give last two digits of number
    //printf("Multiplier index 'i': %i\n", i);
    //printf("Last two digits: %i\n", last_two_digits);
    return last_two_digits;

    //int tens = last_two_digits / 10; //divide by ten to get tens digit
    //int ones = last_two_digits % 10; //modulo ten to get ones digit
}