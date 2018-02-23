/**
 * Copies a BMP piece by piece, just because.
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdint.h>
#include <stdbool.h>

void enlarge(uint8_t * row, int new_width, int old_width, FILE * outptr, int padding);

int main(int argc, char *argv[])
{
    // ensure proper usage
    if (argc != 2)
    {
        fprintf(stderr, "Usage: ./resize resize_factor infile outfile\n");
        return 1;
    }

    // remember filename
    char *infile = argv[1];

    // open input file
    FILE *inptr = fopen(infile, "r");
    if (inptr == NULL)
    {
        fprintf(stderr, "Could not open %s.\n", infile);
        return 2;
    }
    //create output file name pointer
    char *outptr = malloc(8 * sizeof(char)); //xxx.jpg\0

    //initialize file counter to 0
    int file_number = 0;

    // //open new file
    // sprintf(outptr,"%3d.jpg", file_number);
    FILE *outfile = NULL;

    //reserve  'block_size' block worth of memory for reading at a time
    uint8_t buffer[512];

    // need generic lopp counter to count each read block
    int new_JPGs = 0;

    while(fread(buffer, 512, 1, inptr)==1)
      {
         if(buffer[0] == 0xff && buffer[1] == 0xd8 && buffer[2] == 0xff && (buffer[3] & 0xf0) == 0xe0)
         {
               if(outfile != NULL)
               {
                     fclose(outfile);
               }
               sprintf(outptr, "%03i.jpg", file_number);
               outfile = fopen(outptr, "w");
               file_number++;
         }
         if(outfile != NULL)
         {
              fwrite(buffer, 512, 1, outfile);
         }
      }

    free(outptr);

    // close infile
    fclose(inptr);

    // close outfile because we havent't done that yet
    fclose(outfile);

    if(new_JPGs == 0)
    {
        remove(outptr);
    }

    // success
    return 0;
}