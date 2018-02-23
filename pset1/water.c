#include <stdio.h>
#include <cs50.h>

float ounces_per_gal = 128;
float gal_per_min = 1.5;
float ounces_per_bottle = 16;

int main(void)
{
    printf("Minutes: ");
    int minutes = get_int();
    printf("Bottles: %i\n", (int)(((float) minutes * gal_per_min * ounces_per_gal) / ounces_per_bottle ));
}